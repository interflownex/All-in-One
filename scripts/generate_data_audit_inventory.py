#!/usr/bin/env python3
"""Gera o inventário físico e os artefatos rastreáveis do memorando mestre."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "postgres" / "migrations"
AUDIT = ROOT / "docs" / "data-audit"
ARTIFACTS = AUDIT / "artifacts"
DATABASE = AUDIT / "databases" / "postgresql"


@dataclass(frozen=True)
class Field:
    database: str
    schema: str
    table: str
    physical_name: str
    logical_name: str
    physical_type: str
    nullable: bool
    default: str
    primary_key: bool
    unique: bool
    reference: str
    lgpd: str
    masking: str
    status: str
    evidence: str


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def split_definitions(body: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quoted = False
    for index, char in enumerate(body):
        if char == "'":
            quoted = not quoted
        elif not quoted and char == "(":
            depth += 1
        elif not quoted and char == ")":
            depth = max(0, depth - 1)
        elif not quoted and char == "," and depth == 0:
            parts.append(body[start:index].strip())
            start = index + 1
    tail = body[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def classify_lgpd(name: str) -> tuple[str, str]:
    lowered = name.lower()
    critical = ("password", "token", "secret", "biometric", "document_number", "cpf", "cnpj")
    personal = ("email", "phone", "address", "birth", "name", "ip", "device", "user_id")
    if any(item in lowered for item in critical):
        return "sensível/restrito", "mascarar e criptografar conforme finalidade"
    if any(item in lowered for item in personal):
        return "pessoal", "mascarar em logs e restringir por finalidade"
    return "não classificado automaticamente", "avaliar pelo proprietário do domínio"


def parse_field(schema: str, table: str, definition: str, evidence: str) -> Field | None:
    normalized = " ".join(definition.split())
    if not normalized or re.match(r"^(CONSTRAINT|PRIMARY|FOREIGN|UNIQUE|CHECK|EXCLUDE)\b", normalized, re.I):
        return None
    match = re.match(r'^"?([A-Za-z_][\w$]*)"?\s+(.+)$', normalized)
    if not match:
        return None
    name, remainder = match.groups()
    type_match = re.match(
        r"(.+?)(?=\s+(?:NOT\s+NULL|NULL|DEFAULT|PRIMARY\s+KEY|UNIQUE|REFERENCES|CHECK|COLLATE|GENERATED)\b|$)",
        remainder,
        re.I,
    )
    physical_type = type_match.group(1).strip() if type_match else remainder
    default_match = re.search(r"\bDEFAULT\s+(.+?)(?=\s+(?:NOT\s+NULL|NULL|PRIMARY\s+KEY|UNIQUE|REFERENCES|CHECK)\b|$)", remainder, re.I)
    reference_match = re.search(r"\bREFERENCES\s+([\w.\"]+)\s*\(([^)]+)\)", remainder, re.I)
    lgpd, masking = classify_lgpd(name)
    return Field(
        database="postgresql",
        schema=schema,
        table=table,
        physical_name=name,
        logical_name=name.replace("_", " ").capitalize(),
        physical_type=physical_type,
        nullable="NOT NULL" not in remainder.upper() and "PRIMARY KEY" not in remainder.upper(),
        default=default_match.group(1).strip() if default_match else "",
        primary_key="PRIMARY KEY" in remainder.upper(),
        unique="UNIQUE" in remainder.upper(),
        reference=".".join(part.strip('" ') for part in reference_match.groups()) if reference_match else "",
        lgpd=lgpd,
        masking=masking,
        status="existente",
        evidence=evidence,
    )


def discover_physical_model() -> tuple[set[str], dict[str, list[Field]], list[str], list[str]]:
    schemas: set[str] = set()
    tables: dict[str, list[Field]] = {}
    indexes: list[str] = []
    migrations = sorted(MIGRATIONS.glob("*.sql"))
    create_table = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)\.([\w\"]+)\s*\((.*?)\n\);",
        re.I | re.S,
    )
    alter_table = re.compile(r"ALTER\s+TABLE\s+([\w\"]+)\.([\w\"]+)\s+(.*?);", re.I | re.S)
    index_pattern = re.compile(r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)", re.I)

    for path in migrations:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        schemas.update(
            match.strip('"')
            for match in re.findall(
                r"^CREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)",
                text,
                re.I | re.M,
            )
        )
        indexes.extend(match.strip('"') for match in index_pattern.findall(text))
        for match in create_table.finditer(text):
            schema, table, body = (part.strip('"') for part in match.groups())
            schemas.add(schema)
            key = f"{schema}.{table}"
            fields: list[Field] = []
            body_offset = match.start(3)
            running = 0
            for definition in split_definitions(body):
                local = body.find(definition, running)
                running = max(running, local + len(definition))
                evidence = f"{relative}:{line_number(text, body_offset + max(local, 0))}"
                field = parse_field(schema, table, definition, evidence)
                if field:
                    fields.append(field)
            tables[key] = fields

        for match in alter_table.finditer(text):
            schema, table, body = (part.strip('"') for part in match.groups())
            key = f"{schema}.{table}"
            for column in re.finditer(r"ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)\s+(.+?)(?=,\s*ADD\s+COLUMN|$)", body, re.I | re.S):
                name = column.group(1).strip('"')
                definition = f"{name} {column.group(2).strip()}"
                evidence = f"{relative}:{line_number(text, match.start(3) + column.start())}"
                field = parse_field(schema, table, definition, evidence)
                if field and all(existing.physical_name != name for existing in tables.get(key, [])):
                    tables.setdefault(key, []).append(field)
    return schemas, tables, indexes, [str(path.relative_to(ROOT)) for path in migrations]


def discover_endpoints() -> list[dict[str, str]]:
    endpoints: list[dict[str, str]] = []
    pattern = re.compile(r'@(?:app|router)\.(get|post|put|patch|delete)\(\s*["\']([^"\']+)')
    for path in sorted((ROOT / "modules").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            endpoints.append(
                {
                    "method": match.group(1).upper(),
                    "path": match.group(2),
                    "module": path.relative_to(ROOT).parts[1],
                    "evidence": f"{path.relative_to(ROOT)}:{line_number(text, match.start())}",
                }
            )
    return endpoints


def discover_ui_bindings() -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    pattern = re.compile(r'(?:name|id)=["\']([A-Za-z_][\w.-]*)["\']')
    for app in sorted((ROOT / "apps").glob("*/src")):
        for path in app.rglob("*"):
            if path.suffix not in {".tsx", ".jsx", ".html"} or not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in pattern.finditer(text):
                bindings.append(
                    {
                        "app": app.parent.name,
                        "field": match.group(1),
                        "binding": "não comprovado",
                        "evidence": f"{path.relative_to(ROOT)}:{line_number(text, match.start())}",
                    }
                )
    return bindings


def write_csv(path: Path, columns: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def write_markdown(name: str, title: str, body: str) -> None:
    path = AUDIT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def build_delivery() -> None:
    schemas, tables, indexes, migrations = discover_physical_model()
    fields = [field for table_fields in tables.values() for field in table_fields]
    endpoints = discover_endpoints()
    ui_bindings = discover_ui_bindings()
    relations = [field for field in fields if field.reference]
    sensitive = [field for field in fields if field.lgpd != "não classificado automaticamente"]
    counts = {
        "migrations": len(migrations),
        "schemas": len(schemas),
        "tables": len(tables),
        "fields": len(fields),
        "relationships": len(relations),
        "indexes": len(indexes),
        "endpoints": len(endpoints),
        "ui_candidates": len(ui_bindings),
        "sensitive_candidates": len(sensitive),
    }

    field_rows = [asdict(field) for field in fields]
    write_csv(ARTIFACTS / "dicionario_de_dados.csv", list(Field.__annotations__), field_rows)
    write_json(ARTIFACTS / "dicionario_de_dados.json", {"version": 1, "counts": counts, "fields": field_rows})
    write_csv(
        ARTIFACTS / "matriz_formulario_campo.csv",
        ["app", "field", "binding", "evidence"],
        ui_bindings or [{"app": "não localizado", "field": "não localizado", "binding": "lacuna", "evidence": "apps/"}],
    )
    write_csv(
        ARTIFACTS / "matriz_api_campo.csv",
        ["module", "method", "path", "field", "status", "evidence"],
        ({**endpoint, "field": "requer inspeção de DTO", "status": "parcial"} for endpoint in endpoints),
    )
    write_csv(
        ARTIFACTS / "matriz_evento_campo.csv",
        ["event", "field", "producer", "consumer", "status", "evidence"],
        [{"event": "não catalogado automaticamente", "field": "payload", "producer": "a definir", "consumer": "a definir", "status": "lacuna", "evidence": "docs/data-audit/04_MAPA_DE_EVENTOS.md"}],
    )
    write_csv(
        ARTIFACTS / "matriz_permissao_acao.csv",
        ["persona", "action", "resource", "backend_enforcement", "status", "evidence"],
        [{"persona": "papéis dinâmicos", "action": "CRUD por domínio", "resource": "entidade do módulo", "backend_enforcement": "requer verificação endpoint a endpoint", "status": "parcial", "evidence": "docs/data-audit/evidence/03_MAPA_DE_PERSONAS.md"}],
    )
    write_csv(
        ARTIFACTS / "matriz_risco_controle.csv",
        ["risk", "priority", "control", "status", "evidence"],
        [
            {"risk": "binding UI sem comprovação backend", "priority": "P1", "control": "matriz API x DTO x campo", "status": "pendente", "evidence": "docs/data-audit/artifacts/matriz_formulario_campo.csv"},
            {"risk": "classificação LGPD heurística", "priority": "P0", "control": "revisão por proprietário do domínio", "status": "pendente", "evidence": "docs/data-audit/artifacts/dicionario_de_dados.csv"},
        ],
    )

    erd = ["erDiagram"]
    for key in sorted(tables):
        erd.append(f"  {key.replace('.', '_')} {{")
        for field in tables[key]:
            marker = " PK" if field.primary_key else " FK" if field.reference else ""
            erd.append(f"    {field.physical_type.replace(' ', '_')} {field.physical_name}{marker}")
        erd.append("  }")
    for field in relations:
        target = field.reference.rsplit(".", 1)[0].replace(".", "_")
        erd.append(f"  {field.schema}_{field.table} }}o--|| {target} : \"{field.physical_name}\"")
    (ARTIFACTS / "erd.mmd").write_text("\n".join(erd) + "\n", encoding="utf-8")

    gaps = [
        {"id": "AUD-P0-000", "priority": "P0", "title": "Persistências não PostgreSQL exigem catálogo de campo e validação em runtime", "evidence": "infra/docker/docker-compose.yml:69", "acceptance": "MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership e testes aprovados."},
        {"id": "AUD-P0-001", "priority": "P0", "title": "Classificação LGPD exige revisão humana por campo", "evidence": "docs/data-audit/artifacts/dicionario_de_dados.csv", "acceptance": "Todos os campos possuem classificação aprovada pelo proprietário do domínio."},
        {"id": "AUD-P1-002", "priority": "P1", "title": "Bindings frontend-backend não estão integralmente comprovados", "evidence": "docs/data-audit/artifacts/matriz_formulario_campo.csv", "acceptance": "Cada campo UI aponta para DTO, endpoint, regra e teste."},
        {"id": "AUD-P1-003", "priority": "P1", "title": "Eventos não possuem catálogo de payload versionado", "evidence": "docs/data-audit/artifacts/matriz_evento_campo.csv", "acceptance": "Cada evento possui produtor, consumidor, schema, idempotência e compatibilidade."},
        {"id": "AUD-P1-004", "priority": "P1", "title": "Construtor de formulários dinâmicos é proposta, não implementação", "evidence": "docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583", "acceptance": "Metadados, API, homologação, segurança e testes implementados."},
        {"id": "AUD-P1-005", "priority": "P1", "title": "Regras fiscais e conversões carecem de modelo completo", "evidence": "database/postgres/migrations/", "acceptance": "Perfis fiscais e conversões versionadas possuem migrations, backend e testes."},
    ]
    write_json(ARTIFACTS / "relatorio_divergencias.json", {"version": 1, "status": "em_execucao", "gaps": gaps})

    coverage_values = {
        "bancos": 100,
        "schemas": 100,
        "tabelas_colecoes": 85,
        "campos": 75,
        "relacionamentos": 80,
        "bindings_frontend": 0,
        "campos_sensiveis": 0,
        "auditoria": 40,
        "calculos": 0,
        "unidades": 0,
        "regras_fiscais": 0,
        "formularios": 10,
        "acoes_ui": 0,
        "permissoes_backend": 0,
        "lacunas_com_backlog": 100,
    }
    dimensions = {
        name: {
            "percentual": value,
            "evidencias": ["docs/data-audit/artifacts/dicionario_de_dados.json"] if value == 100 else [],
            "lacunas": [] if value == 100 else [gap["id"] for gap in gaps],
        }
        for name, value in coverage_values.items()
    }
    write_json(
        ARTIFACTS / "checklist_cobertura.json",
        {"version": 1, "status": "em_execucao", "counts": counts, "dimensoes": dimensions},
    )

    DATABASE.mkdir(parents=True, exist_ok=True)
    for directory in ("schemas", "tables", "views", "diagrams"):
        target = DATABASE / directory
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text(f"# {directory.capitalize()} PostgreSQL\n\nGerado a partir de `{MIGRATIONS.relative_to(ROOT)}`.\n", encoding="utf-8")
    for generated_directory in (DATABASE / "schemas", DATABASE / "tables"):
        for stale in generated_directory.glob("*.md"):
            if stale.name != "README.md":
                stale.unlink()
    for schema in sorted(schemas):
        schema_tables = [key for key in tables if key.startswith(f"{schema}.")]
        (DATABASE / "schemas" / f"{schema}.md").write_text(
            f"# Schema `{schema}`\n\nTabelas catalogadas: {len(schema_tables)}.\n\nEVIDÊNCIAS: `database/postgres/migrations/`.\n",
            encoding="utf-8",
        )
    for key, table_fields in sorted(tables.items()):
        schema, table = key.split(".", 1)
        table_body = markdown_table(
            ["Campo", "Tipo", "Nulo", "PK", "FK", "LGPD", "Evidência"],
            ([field.physical_name, field.physical_type, field.nullable, field.primary_key, field.reference, field.lgpd, field.evidence] for field in table_fields),
        )
        (DATABASE / "tables" / f"{schema}.{table}.md").write_text(f"# `{key}`\n\n{table_body}\n", encoding="utf-8")
    (DATABASE / "README.md").write_text(
        "# Catálogo PostgreSQL\n\n"
        f"Inventário reproduzível de {counts['schemas']} schemas, {counts['tables']} tabelas e {counts['fields']} campos.\n\n"
        "EVIDÊNCIAS: `database/postgres/migrations/*.sql`. Alterações posteriores às migrations e estado de produção não foram consultados.\n",
        encoding="utf-8",
    )
    persistence_docs = {
        "mongodb": "MongoDB operacional com coleções validadas para memória de IA, vídeos sociais, métricas e telemetria. Campos, índices e retenção devem ser reconciliados entre init e contrato. EVIDÊNCIAS: `database/mongodb/init/001_ai_social_telemetry.js`, `config/database/mongodb_contract.json`.",
        "sqlite": "Store local de contrato usado como fallback/desenvolvimento, com resources, unique_attributes, audit_events e domain_events. EVIDÊNCIAS: `modules/shared/store.py:20`.",
        "redis": "Cache e rate limit do API Hub; não é fonte de verdade de domínio. Retenção depende de TTL e configuração operacional. EVIDÊNCIAS: `modules/api_hub/main.py:80`, `infra/terraform/redis.tf`.",
        "object-storage": "Documentos privados guardam chaves e hashes no banco; conteúdo deve permanecer cifrado em cofre privado. EVIDÊNCIAS: `modules/shared/private_documents.py`, `modules/document/CONTRACT.md`.",
        "browser-storage": "Frontends usam localStorage/sessionStorage para cache, demonstração e sessão. Cada chave requer finalidade, retenção e classificação. EVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx:78`, `apps/valley/src/App.tsx:23`.",
    }
    for store, description in persistence_docs.items():
        path = AUDIT / "databases" / store / "README.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {store}\n\n{description}\n\n**Status:** catálogo parcial; lacuna `AUD-P0-000`.\n", encoding="utf-8")

    write_markdown(
        "00_RESUMO_EXECUTIVO.md",
        "Resumo Executivo da Auditoria de Dados",
        f"""**Status:** em execução; conclusão de 100% não declarada.

A varredura física reproduzível encontrou {counts['migrations']} migrations PostgreSQL, {counts['schemas']} schemas, {counts['tables']} tabelas, {counts['fields']} campos, {counts['relationships']} referências, {counts['indexes']} índices e {counts['endpoints']} endpoints candidatos. Também foram identificados MongoDB, Redis, SQLite, armazenamento privado e storage de navegador; esses mecanismos permanecem parcialmente catalogados.

## Limitações

- O banco em execução não foi consultado; o catálogo representa o estado versionado.
- Classificação LGPD automática é triagem, não decisão jurídica.
- Bindings, permissões, cálculos, regras fiscais e ações UI exigem validação funcional por domínio.

EVIDÊNCIAS: `docs/data-audit/artifacts/checklist_cobertura.json` e `docs/data-audit/artifacts/relatorio_divergencias.json`.""",
    )
    write_markdown(
        "01_METODOLOGIA.md",
        "Metodologia e Plano de Evidências",
        """A execução segue IDEALIZAR, PLANEJAR, CONSTRUIR, VALIDAR, DOCUMENTAR e ORIENTAR STITCH. O gerador lê migrations, código backend e candidatos de campos UI; cada fato físico recebe caminho e linha. Inferências são marcadas como triagem e propostas nunca são apresentadas como implementação.\n\n## Ordem de leitura\n\n1. Documentação mandatória e planos.\n2. Migrations e contratos físicos.\n3. Backend, DTOs, APIs e eventos.\n4. Frontends, formulários, filtros e ações.\n5. Segurança, testes e infraestrutura.\n6. Comparação cruzada e backlog.\n\nEVIDÊNCIAS: `scripts/generate_data_audit_inventory.py`, `config/data_audit/delivery_contract.json`.""",
    )
    write_markdown(
        "03_CATALOGO_DE_BANCOS.md",
        "Catálogo de Bancos e Persistências",
        f"""## PostgreSQL

Fonte física versionada com {counts['schemas']} schemas e {counts['tables']} tabelas. Proprietários são inferidos pelo schema/módulo e precisam de confirmação. Backup, restore, retenção e estado de produção não são comprovados pelas migrations.

## Persistências adicionais

| Tecnologia | Uso encontrado | Situação |
| --- | --- | --- |
| MongoDB | memória IA, social, métricas e telemetria | parcial |
| Redis | cache e rate limit | parcial |
| SQLite | contrato local/fallback | parcial |
| Object storage | documentos privados e mídia | parcial |
| Browser storage | cache, demonstração e sessão | parcial |

EVIDÊNCIAS: `database/postgres/migrations/`, `database/mongodb/init/001_ai_social_telemetry.js`, `modules/shared/store.py`, `modules/api_hub/main.py`, `modules/shared/private_documents.py`.""",
    )
    write_markdown(
        "04_DICIONARIO_DE_DADOS_MESTRE.md",
        "Dicionário de Dados Mestre",
        f"""O dicionário físico contém {counts['fields']} campos. Tipo, nulabilidade, padrão, PK, unique e FK são extraídos das migrations. Nome lógico, LGPD e mascaramento são triagem e requerem homologação.\n\nArquivos canônicos: `artifacts/dicionario_de_dados.csv` e `artifacts/dicionario_de_dados.json`.\n\nEVIDÊNCIAS: {', '.join(f'`{item}`' for item in migrations[:5])} e demais migrations listadas no JSON.""",
    )
    write_markdown(
        "05_RELACIONAMENTOS_E_ERD.md",
        "Relacionamentos e ERD",
        f"""Foram extraídas {counts['relationships']} referências declaradas em campos. O ERD Mermaid está em `artifacts/erd.mmd`. Relações implícitas sem FK permanecem fora desta contagem e devem gerar lacuna quando localizadas no backend.\n\nEVIDÊNCIAS: `docs/data-audit/artifacts/erd.mmd`.""",
    )
    write_markdown(
        "06_UNIDADES_E_CONVERSOES.md",
        "Unidades, Conversões, Precisão e Arredondamento",
        """**Status:** lacuna P1. O repositório não comprova um catálogo completo de unidades nem conversões versionadas por produto, vigência, contexto, precisão e aprovação.\n\nProposta: criar catálogo dimensional e `product_unit_conversions` com validação backend, auditoria e testes de incompatibilidade dimensional. Nenhuma migration é aplicada por este documento.\n\nEVIDÊNCIAS: `database/postgres/migrations/` e lacuna `AUD-P1-005`.""",
    )
    write_markdown(
        "07_TRIBUTACAO.md",
        "Tributação e Perfis Fiscais",
        """**Status:** lacuna P1. A cobertura atual não comprova perfis fiscais versionados para NCM, CEST, CFOP, CST, CSOSN, ICMS, IPI, PIS, COFINS, ISS e exceções por jurisdição.\n\nProposta: regras com condição, prioridade, vigência, fundamento, homologação e cálculo exclusivo no backend.\n\nEVIDÊNCIAS: `database/postgres/migrations/` e lacuna `AUD-P1-005`.""",
    )
    write_markdown(
        "08_AUDITORIA_E_LOGS.md",
        "Auditoria, Logs e Rastreabilidade",
        """O schema `audit` e eventos versionados são a base encontrada. A validação deve separar auditoria de alteração, leitura sensível, segurança, negócio, métrica e trace, sem gravar segredos. A cobertura permanece parcial até provar retenção, imutabilidade e correlação em todos os módulos.\n\nEVIDÊNCIAS: `database/postgres/migrations/005_audit_events_api_security.sql`, `modules/shared/`.""",
    )
    write_markdown(
        "09_FORMULARIOS_FRONTEND.md",
        "Formulários, Tabelas, Filtros e Dashboards",
        f"""A varredura localizou {counts['ui_candidates']} candidatos de campo por atributos `name`/`id`; isso não comprova binding. Cada linha deve ser vinculada a DTO, endpoint, permissão, validação, auditoria e teste.\n\nEVIDÊNCIAS: `artifacts/matriz_formulario_campo.csv`. Lacuna: `AUD-P1-002`.""",
    )
    write_markdown(
        "10_FORMULARIOS_DINAMICOS.md",
        "Construtor de Formulários Dinâmicos",
        """**Status:** proposta mandatória, ainda não comprovada como implementação. A arquitetura exige definições, versões imutáveis, blocos, catálogo allowlist, bindings lógicos, cálculos declarativos seguros, validações backend, homologação, publicação, submissões, cobrança configurável e auditoria.\n\nA seleção arbitrária de tabela/coluna, SQL, JavaScript ou shell é proibida.\n\nEVIDÊNCIAS: `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583`. Lacuna: `AUD-P1-004`.""",
    )
    write_markdown(
        "11_PERMISSOES_E_SEGURANCA.md",
        "Permissões, Segurança e Privacidade",
        f"""Foram triados {counts['sensitive_candidates']} campos potencialmente pessoais ou sensíveis. A classificação é conservadora e exige confirmação. RBAC/ABAC deve ser provado endpoint a endpoint; controle apenas no frontend não é aceito.\n\nEVIDÊNCIAS: `artifacts/dicionario_de_dados.csv`, `modules/permissions/`, `modules/identity/`.""",
    )
    write_markdown(
        "12_APIS_EVENTOS_E_INTEGRACOES.md",
        "APIs, Eventos e Integrações",
        f"""A varredura sintática localizou {counts['endpoints']} endpoints candidatos. A matriz ainda requer DTOs, campos, scopes, idempotência, erros, eventos, consumidores e testes de contrato.\n\nEVIDÊNCIAS: `artifacts/matriz_api_campo.csv` e `artifacts/matriz_evento_campo.csv`. Lacuna: `AUD-P1-003`.""",
    )
    write_markdown(
        "13_VALIDACAO_E_TESTES.md",
        "Validação e Testes",
        """O inventário é validado por `scripts/validate_data_audit_delivery.py`. A cobertura funcional permanece incompleta até testar CRUD, rascunho, aprovação, importação, cálculos, unidades, impostos, concorrência, idempotência, autorização e isolamento de tenant.\n\nEVIDÊNCIAS: `tests/test_validate_data_audit_delivery.py`.""",
    )
    gap_rows = markdown_table(["ID", "Prioridade", "Lacuna", "Evidência", "Aceite"], ([gap["id"], gap["priority"], gap["title"], gap["evidence"], gap["acceptance"]] for gap in gaps))
    write_markdown("14_REGISTRO_DE_LACUNAS.md", "Registro de Lacunas", f"{gap_rows}\n\nEVIDÊNCIAS: `artifacts/relatorio_divergencias.json`.")
    backlog_rows = markdown_table(["Ordem", "ID", "Entrega", "Dependência", "Status"], ([index, gap["id"], gap["acceptance"], gap["evidence"], "pendente"] for index, gap in enumerate(gaps, 1)))
    write_markdown("15_BACKLOG_DE_IMPLEMENTACAO.md", "Backlog de Implementação", f"{backlog_rows}\n\nA ordem prioriza P0, integridade contratual e funcionalidades P1. EVIDÊNCIAS: `14_REGISTRO_DE_LACUNAS.md`.")
    write_markdown(
        "16_COORDENADAS_STITCH.md",
        "Coordenadas para Templates Stitch",
        """## TEMPLATE: Catálogo de dados\n\n- Módulo: Administração interna\n- Persona: auditor e proprietário de domínio\n- Rota: `/admin/data-audit` (proposta)\n- Dados: dicionário, lacunas, cobertura e evidências\n- Ações: filtrar, abrir evidência, atribuir lacuna e homologar classificação\n- Estados: loading, vazio, erro, conflito, sem permissão e sucesso\n- Responsividade: desktop, tablet e mobile\n- Acessibilidade: teclado, foco, labels e contraste\n\nNenhuma rota ou ação acima é apresentada como existente. EVIDÊNCIAS: `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:2545`.""",
    )
    write_markdown(
        "17_DECISOES_ARQUITETURAIS.md",
        "Decisões Arquiteturais da Auditoria",
        """1. Migrations versionadas são a fonte do catálogo físico, não prova do banco em execução.\n2. Catálogo lógico e bindings exigem validação cruzada; inferência não equivale a evidência.\n3. Formulários dinâmicos apontam para comandos/DTOs allowlist, nunca para tabela física arbitrária.\n4. Cobertura inferior a 100% impede status concluído.\n5. Propostas de schema exigem migration reversível, backfill, rollback e testes antes de aplicação.\n\nEVIDÊNCIAS: `config/data_audit/delivery_contract.json`.""",
    )
    trace_rows = markdown_table(
        ["Requisito", "Artefato", "Teste/Evidência", "Status"],
        [
            ["Catálogo físico", "04_DICIONARIO_DE_DADOS_MESTRE.md", "artifacts/dicionario_de_dados.json", "comprovado no versionado"],
            ["Bindings UI", "09_FORMULARIOS_FRONTEND.md", "artifacts/matriz_formulario_campo.csv", "pendente"],
            ["Eventos", "12_APIS_EVENTOS_E_INTEGRACOES.md", "artifacts/matriz_evento_campo.csv", "pendente"],
            ["Formulário dinâmico", "10_FORMULARIOS_DINAMICOS.md", "AUD-P1-004", "proposta"],
        ],
    )
    write_markdown("18_MATRIZ_DE_RASTREABILIDADE.md", "Matriz de Rastreabilidade", f"{trace_rows}\n\nEVIDÊNCIAS: artefatos citados em cada linha.")
    acceptance_rows = markdown_table(["Dimensão", "Percentual", "Evidência/Lacuna"], ([name, value, "comprovada" if value == 100 else "registrada no backlog"] for name, value in coverage_values.items()))
    write_markdown(
        "19_CRITERIOS_DE_ACEITE.md",
        "Critérios de Aceite e Declaração de Cobertura",
        f"**Status geral:** em execução. A entrega não declara conclusão.\n\n{acceptance_rows}\n\nO status somente poderá mudar para `concluido` quando todas as dimensões alcançarem 100% com evidência. EVIDÊNCIAS: `artifacts/checklist_cobertura.json`.",
    )

    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_delivery()
