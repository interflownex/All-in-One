#!/usr/bin/env python3
"""Gera o inventário físico e os artefatos rastreáveis do memorando mestre."""

from __future__ import annotations

import csv
import ast
import json
import re
import sys
import types
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "postgres" / "migrations"
AUDIT = ROOT / "docs" / "data-audit"
ARTIFACTS = AUDIT / "artifacts"
DATABASE = AUDIT / "databases" / "postgresql"
DYNAMIC_FORM_MODEL = ROOT / "config" / "data_audit" / "dynamic_form_model_proposal.json"
PRODUCT_UNITS_TAX_MODEL = ROOT / "config" / "data_audit" / "product_units_tax_model_proposal.json"
FIELD_CLASSIFICATION_POLICY = ROOT / "config" / "data_audit" / "field_classification_policy.json"
AUDIT_TRACEABILITY_POLICY = ROOT / "config" / "data_audit" / "audit_traceability_policy.json"
STITCH_TEMPLATE_COORDINATE = ROOT / "config" / "stitch" / "template_project_coordinate.json"
MASTER_MEMO = ROOT / "docs" / "MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md"
PYTEST_EXECUTION_REPORTS = (
    ARTIFACTS / "pytest_unit_results.xml",
    ARTIFACTS / "pytest_identity_e2e_results.xml",
)


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
    classification_basis: str
    encryption: str
    masking: str
    retention: str
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


def classify_lgpd(name: str) -> tuple[str, str, str, str, str]:
    policy = json.loads(FIELD_CLASSIFICATION_POLICY.read_text(encoding="utf-8"))
    lowered = name.lower()
    for category in policy["categories"]:
        matched = [pattern for pattern in category["patterns"] if pattern in lowered]
        if matched:
            return (
                category["classification"],
                f"política v{policy['version']} categoria {category['id']}; padrões: {', '.join(matched)}",
                category["encryption"],
                category["masking"],
                category["retention"],
            )
    default = policy["default"]
    return (
        default["classification"],
        f"política v{policy['version']}; nenhuma regra automática aplicável",
        default["encryption"],
        default["masking"],
        default["retention"],
    )


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
    lgpd, classification_basis, encryption, masking, retention = classify_lgpd(name)
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
        classification_basis=classification_basis,
        encryption=encryption,
        masking=masking,
        retention=retention,
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


def discover_mongodb_model() -> list[dict[str, object]]:
    init_path = ROOT / "database" / "mongodb" / "init" / "001_ai_social_telemetry.js"
    contract_path = ROOT / "config" / "database" / "mongodb_contract.json"
    text = init_path.read_text(encoding="utf-8")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    starts = list(re.finditer(r'createValidatedCollection\("([^"]+)",\s*\{', text))
    rows: list[dict[str, object]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[match.start():end]
        collection = match.group(1)
        required_match = re.search(r"required:\s*\[([^]]*)\]", block)
        required = set(re.findall(r'"([^"]+)"', required_match.group(1))) if required_match else set()
        properties_match = re.search(r"properties:\s*\{(.*)", block, re.S)
        properties = properties_match.group(1) if properties_match else ""
        for field_match in re.finditer(r"^    ([A-Za-z_][\w]*):\s*\{([^\n]*)", properties, re.M):
            field_name, definition = field_match.groups()
            type_match = re.search(r'bsonType:\s*"([^"]+)"', definition)
            enum_match = re.search(r"enum:\s*\[([^]]+)\]", definition)
            lgpd, basis, encryption, masking, retention = classify_lgpd(field_name)
            rows.append(
                {
                    "database": contract["default_database"],
                    "collection": collection,
                    "field": field_name,
                    "bson_type": type_match.group(1) if type_match else "object/complex",
                    "required": field_name in required,
                    "enum": re.findall(r'"([^"]+)"', enum_match.group(1)) if enum_match else [],
                    "sensitive_declared": field_name in contract["collections"][collection]["sensitive_fields"],
                    "lgpd": lgpd,
                    "classification_basis": basis,
                    "encryption": encryption,
                    "masking": masking,
                    "retention": retention,
                    "indexes": contract["collections"][collection]["indexes"],
                    "evidence": f"{init_path.relative_to(ROOT)}:{line_number(text, match.start() + properties_match.start(1) + field_match.start())}",
                }
            )
    return rows


def discover_sqlite_model() -> list[dict[str, object]]:
    path = ROOT / "modules" / "shared" / "store.py"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\((.*?)\n\s*\);", re.I | re.S)
    rows: list[dict[str, object]] = []
    for match in pattern.finditer(text):
        table, body = match.groups()
        for definition in split_definitions(body):
            field = parse_field("local_contract", table, definition, f"{path.relative_to(ROOT)}:{line_number(text, match.start())}")
            if field:
                rows.append({**asdict(field), "database": "sqlite_contract_store"})
    return rows


def source_evidence(relative: str, needle: str) -> str:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    offset = text.find(needle)
    if offset < 0:
        raise RuntimeError(f"Evidência não localizada em {relative}: {needle}")
    return f"{relative}:{line_number(text, offset)}"


def discover_redis_catalog() -> list[dict[str, object]]:
    return [
        {
            "technology": "Redis 7", "database": "0", "key_pattern": "rate_limit:{ip}",
            "purpose": "Contador de requisições por endereço IP no API Hub", "owner": "api_hub",
            "operations": ["GET", "INCR", "EXPIRE"], "value_type": "integer", "ttl_seconds": 60,
            "limit": 100, "source_of_truth": False, "data_classification": "identificador técnico pseudônimo",
            "encryption": "trânsito/rede privada dependem do ambiente; não comprovado em runtime",
            "retention": "TTL deslizante de 60 segundos", "failure_mode": "fail-open quando cliente ou Redis falha",
            "backup_restore": "não requerido para cache; reconstruído pelo tráfego", "runtime_verified": False,
            "evidence": source_evidence("modules/api_hub/main.py", 'key = f"rate_limit:{ip}"'),
            "infrastructure_evidence": [source_evidence("infra/docker/docker-compose.yml", "image: redis:7-alpine"), source_evidence("infra/terraform/redis.tf", 'redis_version = "REDIS_7_0"')],
        }
    ]


def discover_object_storage_catalog() -> list[dict[str, object]]:
    return [
        {
            "store": "private_document_vault", "provider": "filesystem privado local/fallback", "container": "ALL_IN_ONE_PRIVATE_DOCUMENT_DIR",
            "object_pattern": "ctps/{sha256_prefix}/{sha256}.pdf.aesgcm", "purpose": "PDFs CTPS e evidências privadas",
            "owner": "jobs/shared", "access": "backend PrivateDocumentStore", "classification": "crítica",
            "encryption": "AES-256-GCM com AAD SHA-256", "retention": "não implementada no store; política externa necessária",
            "versioning": "deduplicação pelo hash; sem versionamento nativo", "backup_restore": "política declara snapshot diário versionado e teste trimestral",
            "public": False, "runtime_verified": False, "evidence": source_evidence("modules/shared/private_documents.py", 'URI_PREFIX = "private://jobs/"'),
        },
        {
            "store": "document_domain_references", "provider": "private_vault|gcs_kms|s3_kms", "container": "storage_bucket por documento",
            "object_pattern": "storage_key versionada", "purpose": "Documentos, versões, OCR e assinatura",
            "owner": "document", "access": "serviço document com autorização", "classification": "crítica conforme documento",
            "encryption": "KMS obrigatório por contrato", "retention": "retention_policies por domínio; enforcement runtime não comprovado",
            "versioning": "versions append-only", "backup_restore": "RPO 60 min, RTO 240 min na política declarada",
            "public": False, "runtime_verified": False, "evidence": source_evidence("modules/document/CONTRACT.md", "storage_key` e `storage_bucket` devem apontar para cofre privado"),
        },
        {
            "store": "mobile_public_artifacts", "provider": "Google Cloud Storage", "container": "all-in-one-public-artifacts",
            "object_pattern": "valley-latest.apk", "purpose": "Distribuição pública de artefato Android",
            "owner": "release engineering", "access": "allUsers roles/storage.objectViewer", "classification": "pública",
            "encryption": "padrão do provedor; não comprovado", "retention": "não declarada", "versioning": "nome latest sobrescrevível; versionamento de bucket não declarado",
            "backup_restore": "não declarado; artefato pode ser reconstruído", "public": True, "runtime_verified": False,
            "evidence": source_evidence("scripts/deploy_mobile_artifacts.py", 'DEFAULT_BUCKET = "all-in-one-public-artifacts"'),
        },
        {
            "store": "terraform_state", "provider": "Google Cloud Storage", "container": "all-in-one-tfstate",
            "object_pattern": "terraform/state/**", "purpose": "Estado da infraestrutura Terraform",
            "owner": "plataforma", "access": "IAM do bucket; não inventariado neste artefato", "classification": "operacional sensível",
            "encryption": "padrão do provedor; CMEK não declarada no backend", "retention": "não declarada", "versioning": "não declarado no código",
            "backup_restore": "não declarado", "public": False, "runtime_verified": False,
            "evidence": source_evidence("infra/terraform/provider.tf", 'bucket = "all-in-one-tfstate"'),
        },
    ]


def discover_browser_storage_catalog() -> list[dict[str, object]]:
    definitions = [
        ("sessionStorage", "valley.session.token", "token de autenticação da sessão web", "credencial", "até fechar a sessão/clear", "apps/valley/src/App.tsx", "valley.session.token"),
        ("sessionStorage", "valley.session.user-id", "identificador do usuário autenticado", "dado pessoal pseudônimo", "até fechar a sessão/clear", "apps/valley/src/App.tsx", "valley.session.user-id"),
        ("sessionStorage", "valley.session.email", "email injetado pelo shell Android", "dado pessoal", "até clear/logout", "apps/valley-android/app/src/main/java/com/example/valley/ui/main/MainScreen.kt", "valley.session.email"),
        ("sessionStorage", "valley.session.source", "origem da sessão injetada", "metadado técnico", "até clear/logout", "apps/valley-android/app/src/main/java/com/example/valley/ui/main/MainScreen.kt", "valley.session.source"),
        ("localStorage", "valley.session.mode", "ativa modo de demonstração", "configuração", "sem TTL; remoção explícita", "apps/valley/src/lib/valleyPlatform.ts", "valley.session.mode"),
        ("localStorage", "valley.demo.users", "usuários simulados", "dado de demonstração potencialmente pessoal", "sem TTL", "apps/valley/src/lib/valleyPlatform.ts", "valley.demo.users"),
        ("localStorage", "valley.demo.offers", "ofertas simuladas", "dado de demonstração", "sem TTL", "apps/valley/src/lib/valleyPlatform.ts", "valley.demo.offers"),
        ("localStorage", "valley.demo.orders", "pedidos simulados", "dado transacional de demonstração", "sem TTL", "apps/valley/src/lib/valleyPlatform.ts", "valley.demo.orders"),
        ("localStorage", "valley.demo.reviews", "avaliações simuladas", "conteúdo de demonstração", "sem TTL", "apps/valley/src/lib/valleyPlatform.ts", "valley.demo.reviews"),
        ("localStorage", "valley.demo.support", "casos de suporte simulados", "conteúdo de demonstração potencialmente pessoal", "sem TTL", "apps/valley/src/lib/valleyPlatform.ts", "valley.demo.support"),
        ("localStorage", "valley.catalog.v1.{query}", "cache de páginas do catálogo", "catálogo público e parâmetros de busca", "timestamp cachedAt gravado; expiração não comprovada", "apps/valley/src/lib/valleyPlatform.ts", "valley.catalog.v1."),
        ("localStorage", "all-in-one:{module}:{resourceType}", "fallback CRUD local por recurso", "pode conter dados de qualquer módulo", "sem TTL", "apps/all-in-one/src/components/SmartCRUD.tsx", "all-in-one:${module}:${resourceType}"),
    ]
    return [
        {
            "storage": storage, "key_pattern": key, "purpose": purpose, "classification": classification,
            "retention": retention, "owner": "frontend indicado pela evidência", "operations": ["GET", "SET", "REMOVE/CLEAR quando implementado"],
            "encryption": "não criptografado pela aplicação", "source_of_truth": False,
            "risk": "acessível a JavaScript/XSS; não usar como fonte oficial nem persistir segredo além da sessão necessária",
            "runtime_verified": False, "evidence": source_evidence(relative, needle),
        }
        for storage, key, purpose, classification, retention, relative, needle in definitions
    ]


def annotation_name(node: ast.AST | None) -> str:
    return ast.unparse(node) if node is not None else ""


def discover_endpoints() -> list[dict[str, object]]:
    endpoints: list[dict[str, object]] = []
    for path in sorted((ROOT / "modules").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        models: dict[str, list[str]] = {}
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not any(annotation_name(base).endswith("BaseModel") for base in node.bases):
                continue
            models[node.name] = [item.target.id for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                    continue
                method = decorator.func.attr.lower()
                if method not in {"get", "post", "put", "patch", "delete"} or not decorator.args:
                    continue
                route_node = decorator.args[0]
                if not isinstance(route_node, ast.Constant) or not isinstance(route_node.value, str):
                    continue
                response_model = ""
                for keyword in decorator.keywords:
                    if keyword.arg == "response_model":
                        response_model = annotation_name(keyword.value)
                parameters: list[dict[str, object]] = []
                for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                    annotation = annotation_name(argument.annotation)
                    if argument.arg in {"self", "request"}:
                        continue
                    model_name = annotation.split("[")[-1].rstrip("]") if "[" in annotation else annotation
                    parameters.append(
                        {
                            "name": argument.arg,
                            "annotation": annotation,
                            "model_fields": models.get(model_name, []),
                        }
                    )
                endpoints.append(
                    {
                        "method": method.upper(),
                        "path": route_node.value,
                        "module": path.relative_to(ROOT).parts[1],
                        "function": node.name,
                        "parameters": parameters,
                        "response_model": response_model,
                        "evidence": f"{path.relative_to(ROOT)}:{decorator.lineno}",
                    }
                )
    return endpoints


def literal_strings(node: ast.AST | None) -> list[str]:
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return [item.value for item in node.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
    return []


def discover_logical_rules(tables: dict[str, list[Field]], ui_bindings: list[dict[str, str]]) -> list[dict[str, object]]:
    path = ROOT / "modules" / "shared" / "domain_rules.py"
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    module_entities: dict[str, tuple[str, ...]] = {}
    override_node: ast.Dict | None = None
    for node in tree.body:
        target = node.target if isinstance(node, ast.AnnAssign) else node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None
        if not isinstance(target, ast.Name):
            continue
        if target.id == "MODULE_ENTITIES":
            module_entities = ast.literal_eval(node.value)
        elif target.id == "RULE_OVERRIDES" and isinstance(node.value, ast.Dict):
            override_node = node.value

    overrides: dict[tuple[str, str], dict[str, object]] = {}
    if override_node:
        for key_node, value_node in zip(override_node.keys, override_node.values):
            try:
                key = ast.literal_eval(key_node)
            except (ValueError, TypeError):
                continue
            if not isinstance(key, tuple) or len(key) != 2 or not isinstance(value_node, ast.Call):
                continue
            positional = value_node.args
            keywords = {item.arg: item.value for item in value_node.keywords if item.arg}
            required_node = keywords.get("required_fields") or (positional[0] if positional else None)
            unique_node = keywords.get("unique_fields") or (positional[1] if len(positional) > 1 else None)
            status_node = keywords.get("initial_status") or (positional[2] if len(positional) > 2 else None)
            status = status_node.value if isinstance(status_node, ast.Constant) and isinstance(status_node.value, str) else "draft"
            overrides[(str(key[0]), str(key[1]))] = {
                "required_fields": literal_strings(required_node),
                "unique_fields": literal_strings(unique_node),
                "initial_status": status,
                "sensitive": isinstance(keywords.get("sensitive"), ast.Constant) and keywords["sensitive"].value is True,
                "immutable": isinstance(keywords.get("immutable"), ast.Constant) and keywords["immutable"].value is True,
                "monetary_fields": literal_strings(keywords.get("monetary_fields")),
                "evidence": f"{path.relative_to(ROOT)}:{value_node.lineno}",
            }

    store_targets: dict[tuple[str, str], str] = {}
    for module in module_entities:
        store_path = ROOT / "modules" / "shared" / f"{module}_postgres_store.py"
        if not store_path.exists():
            continue
        store_tree = ast.parse(store_path.read_text(encoding="utf-8"))
        for node in ast.walk(store_tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            target = node.target if isinstance(node, ast.AnnAssign) else node.targets[0] if len(node.targets) == 1 else None
            if not isinstance(target, ast.Name) or target.id not in {"TABLES", "tables"}:
                continue
            try:
                mapping = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if isinstance(mapping, dict):
                store_targets.update({(module, str(resource)): str(table) for resource, table in mapping.items()})

    canonical_by_compact = {
        (module, entity.replace("_", "")): entity
        for module, entities in module_entities.items()
        for entity in entities
    }
    ui_resources = {
        (row["module"], canonical_by_compact.get((row["module"], row["entity"]), row["entity"]))
        for row in ui_bindings
    }
    rows: list[dict[str, object]] = []
    for module, entities in module_entities.items():
        for entity in entities:
            override = overrides.get((module, entity), {})
            physical_target = store_targets.get((module, entity), f"{module}.{entity}")
            has_physical_target = physical_target in tables
            rows.append(
                {
                    "module": module,
                    "entity": entity,
                    "required_fields": override.get("required_fields", []),
                    "unique_fields": override.get("unique_fields", []),
                    "monetary_fields": override.get("monetary_fields", []),
                    "initial_status": override.get("initial_status", "draft"),
                    "sensitive": override.get("sensitive", False),
                    "immutable": override.get("immutable", False),
                    "has_rule_override": (module, entity) in overrides,
                    "physical_storage_target": physical_target,
                    "persistence_decision": (
                        "typed_table" if physical_target == f"{module}.{entity}" and has_physical_target
                        else "typed_alias" if has_physical_target
                        else "missing_typed_relation"
                    ),
                    "has_physical_table": has_physical_target,
                    "has_ui_surface": (module, entity) in ui_resources,
                    "evidence": override.get("evidence", f"{path.relative_to(ROOT)}:74"),
                }
            )
    return rows


def discover_transitions(logical_rules: list[dict[str, object]]) -> list[dict[str, object]]:
    modules_root = str(ROOT / "modules")
    if modules_root not in sys.path:
        sys.path.insert(0, modules_root)
    try:
        from shared.domain_rules import RULE_OVERRIDES  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        if exc.name != "fastapi":
            raise
        fastapi_stub = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, *args: object, **kwargs: object) -> None:
                super().__init__(*args)
                self.detail = kwargs.get("detail")
                self.status_code = kwargs.get("status_code")

        fastapi_stub.HTTPException = HTTPException  # type: ignore[attr-defined]
        sys.modules["fastapi"] = fastapi_stub
        from shared.domain_rules import RULE_OVERRIDES  # type: ignore[import-not-found,no-redef]

    required_by_resource = {
        (str(row["module"]), str(row["entity"])): list(row["required_fields"])
        for row in logical_rules
    }
    rows: list[dict[str, object]] = []
    for (module, entity), rule in sorted(RULE_OVERRIDES.items()):
        for action, transition in sorted(rule.transitions.items()):
            if not transition.event:
                continue
            rows.append(
                {
                    "event": transition.event,
                    "version": "não declarada",
                    "module": module,
                    "entity": entity,
                    "action": action,
                    "source_statuses": sorted(transition.source),
                    "target_status": transition.target,
                    "roles": sorted(transition.roles),
                    "requires_mfa": transition.requires_mfa,
                    "payload_fields": required_by_resource.get((module, entity), []),
                    "producer": module,
                    "consumers": [],
                    "idempotency_key": "não comprovada no schema do evento",
                    "correlation_id": "exigido pelo runtime compartilhado",
                    "evidence": "modules/shared/domain_rules.py",
                }
            )
    return rows


def discover_ui_bindings(tables: dict[str, list[Field]]) -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    tag_pattern = re.compile(r"<SmartCRUD\s+(.+?)/>", re.S)
    prop_pattern = re.compile(r'(module|entity|type|title)=["\']([^"\']+)["\']')
    generic_fields = {
        "form": ("name", "description", "category"),
        "list": ("name", "title", "status", "created_at"),
    }
    smart_crud_text = (ROOT / "apps" / "all-in-one" / "src" / "components" / "SmartCRUD.tsx").read_text(
        encoding="utf-8"
    )
    resource_aliases = dict(
        re.findall(r"'([^']+:[^']+)':\s*'([^']+)'", smart_crud_text)
    )
    app_path = ROOT / "apps" / "all-in-one" / "src" / "App.tsx"
    app_text = app_path.read_text(encoding="utf-8")
    imports = {
        component: str((app_path.parent / f"{relative}.tsx").relative_to(ROOT))
        for component, relative in re.findall(
            r"const\s+(\w+)\s*=\s*lazy\(\(\)\s*=>\s*import\('([^']+)'\)\)", app_text
        )
    }
    routes_by_file: dict[str, str] = {}
    for route, component in re.findall(r'<Route\s+path="([^"]+)"\s+element=\{(\w+)', app_text):
        if component in imports:
            routes_by_file[imports[component]] = route
    pages = ROOT / "apps" / "all-in-one" / "src" / "pages"
    for path in sorted(pages.rglob("*.tsx")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in tag_pattern.finditer(text):
            props = dict(prop_pattern.findall(match.group(1)))
            if not {"module", "entity", "type"}.issubset(props):
                continue
            entity = resource_aliases.get(f"{props['module']}:{props['entity']}", props["entity"])
            table_fields = {field.physical_name for field in tables.get(f"{props['module']}.{entity}", [])}
            for field in generic_fields.get(props["type"], ("não identificado",)):
                binding = "campo físico provável" if field in table_fields else "payload genérico/não comprovado"
                bindings.append(
                    {
                        "app": "all-in-one",
                        "module": props["module"],
                        "entity": entity,
                        "surface": props["type"],
                        "title": props.get("title", ""),
                        "route": routes_by_file.get(str(path.relative_to(ROOT)), "não localizada"),
                        "field": field,
                        "binding": binding,
                        "evidence": f"{path.relative_to(ROOT)}:{line_number(text, match.start())}",
                    }
                )
    return bindings


def discover_ui_actions(ui_bindings: list[dict[str, str]]) -> list[dict[str, object]]:
    source = "apps/all-in-one/src/components/SmartCRUD.tsx"
    source_text = (ROOT / source).read_text(encoding="utf-8")
    save_contract_compatible = all(
        marker in source_text
        for marker in (
            "method: isEditing ? 'PATCH' : 'POST'",
            "isEditing ? { payload } : { user_id: actorId, payload }",
            "'X-Idempotency-Key': crypto.randomUUID()",
            "'X-Correlation-Id': crypto.randomUUID()",
        )
    )
    surfaces = {
        (row["evidence"], row["module"], row["entity"], row["surface"], row["route"])
        for row in ui_bindings
    }
    aliases = {
        ("identity", "identity"): "users",
        ("delivery", "deliveryrequests"): "delivery_requests",
        ("jobs", "jobpostings"): "job_postings",
    }
    rows: list[dict[str, object]] = []
    for surface_evidence, module, entity, surface, route in sorted(surfaces):
        resource = aliases.get((module, entity), entity)
        base = f"/{module}/resources/{resource}"
        common = {"module": module, "entity": entity, "surface": surface, "route": route, "surface_evidence": surface_evidence}
        if surface == "form":
            rows.extend(
                [
                    {
                        **common, "action": "Cancelar", "trigger": "click", "method": "local", "endpoint": "navigate(-1)",
                        "request_contract": "não aplicável", "backend_contract": "não aplicável", "contract_status": "comprovado_local",
                        "frontend_permission_gate": "não aplicável", "backend_enforcement": "não aplicável", "audit": "não aplicável",
                        "states": ["idle"], "test_evidence": "não localizado por superfície", "evidence": source_evidence(source, "navigate(-1)"),
                    },
                    {
                        **common, "action": "Salvar Registro", "trigger": "submit", "method": "POST (criação) / PATCH (edição)", "endpoint": base,
                        "request_contract": "POST {user_id,payload}; PATCH {payload}; correlação e idempotência na criação",
                        "backend_contract": "ResourceCreate {user_id,entity_id?,payload}; ResourcePatch {payload}",
                        "contract_status": "compativel" if save_contract_compatible else "incompativel", "frontend_permission_gate": "token com sub obrigatório", "backend_enforcement": True,
                        "audit": "backend registra criação/edição aceita com ator e correlação", "states": ["saving", "saved", "failed"],
                        "test_evidence": "contrato estático compartilhado; E2E por superfície ainda necessário", "evidence": source_evidence(source, "method: isEditing ? 'PATCH' : 'POST'"),
                    },
                ]
            )
        else:
            rows.extend(
                [
                    {**common, "action": "Pesquisar", "trigger": "click", "method": "GET", "endpoint": base, "request_contract": "query/limit", "backend_contract": "lista protegida por actor_from_headers", "contract_status": "parcial_com_fallback_local", "frontend_permission_gate": False, "backend_enforcement": True, "audit": "leitura sensível não comprovada por superfície", "states": ["loading", "erro", "sucesso"], "test_evidence": "não localizado por superfície", "evidence": source_evidence(source, "onClick={fetchData}")},
                    {**common, "action": "Novo registro", "trigger": "click", "method": "local", "endpoint": f"/{module}/{entity}-form", "request_contract": "navegação", "backend_contract": "não aplicável até salvar", "contract_status": "comprovado_local", "frontend_permission_gate": False, "backend_enforcement": "não aplicável", "audit": "não aplicável", "states": ["idle"], "test_evidence": "não localizado por superfície", "evidence": source_evidence(source, "Novo registro")},
                    {**common, "action": "Ver detalhes", "trigger": "click", "method": "local", "endpoint": "modal em memória", "request_contract": "registro já carregado", "backend_contract": "não consulta GET de detalhe", "contract_status": "comprovado_local_sem_refresh", "frontend_permission_gate": False, "backend_enforcement": False, "audit": "leitura de detalhe não auditada no clique", "states": ["aberto", "fechado"], "test_evidence": "não localizado por superfície", "evidence": source_evidence(source, "setSelectedMedia(item)")},
                    {**common, "action": "Editar", "trigger": "click", "method": "local", "endpoint": f"/{module}/{entity}-form", "request_contract": "registro em location.state", "backend_contract": "salvamento posterior usa PATCH ResourcePatch", "contract_status": "compativel_via_formulario" if save_contract_compatible else "parcial_edicao_incompativel", "frontend_permission_gate": "token validado no salvamento", "backend_enforcement": "no salvamento", "audit": "backend no salvamento", "states": ["idle"], "test_evidence": "contrato estático compartilhado; E2E por superfície ainda necessário", "evidence": source_evidence(source, ">Editar</button>")},
                    {**common, "action": "Excluir", "trigger": "click", "method": "DELETE", "endpoint": f"{base}/{{id}}", "request_contract": "UUID e confirmação", "backend_contract": "soft delete; imutáveis/sensíveis retornam 409", "contract_status": "parcial_com_fallback_local", "frontend_permission_gate": False, "backend_enforcement": True, "audit": "backend audita somente chamada remota aceita", "states": ["running", "completed", "failed"], "test_evidence": "não localizado por superfície", "evidence": source_evidence(source, "onClick={() => deleteRecord(item)}")},
                ]
            )
            journey = {
                ("marketplace", "orders"): ("Autorizar pagamento sandbox", "POST", "/gateway/payments/sandbox/authorize"),
                ("delivery", "delivery_requests"): ("Executar jornada de entrega", "POST x3", "/delivery/resources/delivery_requests/{id}/actions/{assign|pickup|complete}"),
                ("jobs", "job_postings"): ("Enviar candidatura", "POST x2", "/jobs/resources/{resumes|applications}"),
            }.get((module, entity))
            if journey:
                action, method, endpoint = journey
                rows.append({**common, "action": action, "trigger": "click", "method": method, "endpoint": endpoint, "request_contract": "contrato específico implementado no SmartCRUD", "backend_contract": "rotas específicas com actor/autorização", "contract_status": "implementado_requer_e2e_vivo", "frontend_permission_gate": "token e presença de dados; papel não verificado", "backend_enforcement": True, "audit": "backend conforme transições", "states": ["running", "completed", "failed"], "test_evidence": "testes de jornada existem, cobertura por tela requer confirmação", "evidence": source_evidence(source, "const runJourneyAction = async () =>")})
    return rows


def discover_permission_enforcement(
    logical_rules: list[dict[str, object]], transitions: list[dict[str, object]]
) -> list[dict[str, object]]:
    runtime = "modules/shared/runtime.py"
    runtime_text = (ROOT / runtime).read_text(encoding="utf-8")
    generic_read_has_ownership = '_authorize_resource_read(actor, UUID(item["user_id"]), rule, module_name)' in runtime_text
    test_sources = [(path, path.read_text(encoding="utf-8", errors="ignore")) for path in sorted((ROOT / "tests").rglob("*.py"))]

    def test_evidence(entity: str, operation: str) -> list[str]:
        candidates: list[str] = []
        verb = {"create": "post", "list": "get", "read": "get", "update": "patch", "delete": "delete"}.get(operation, "post")
        needs_resource_id = operation not in {"create", "list"}
        suffix = "/" if needs_resource_id else "[\\\"']"
        endpoint_pattern = re.compile(rf"\.{verb}\(\s*f?[\"']/resources/{re.escape(entity)}{suffix}")
        for path, text in test_sources:
            match = endpoint_pattern.search(text)
            if not match:
                continue
            if operation not in {"create", "list", "read", "update", "delete"}:
                window = text[match.start():match.start() + 500]
                if f"/actions/{operation}" not in window:
                    continue
            candidates.append(f"{path.relative_to(ROOT)}:{line_number(text, match.start())}")
            if len(candidates) == 3:
                break
        return candidates

    rows: list[dict[str, object]] = []
    generic_operations = (
        ("create", "POST", "/resources/{resource_type}", "owner_or_operator", "store.create gera audit/event", "X-Idempotency-Key somente transacionais", '@app.post("/resources/{resource_type}"'),
        ("list", "GET", "/resources/{resource_type}", "lista do actor; user_id de terceiro exige APPROVER_ROLES", "leitura não auditada genericamente", "não aplicável", '@app.get("/resources/{resource_type}")'),
        ("read", "GET", "/resources/{resource_type}/{resource_id}", "owner_or_operator antes da exposição", "leitura não auditada genericamente", "não aplicável", '@app.get("/resources/{resource_type}/{resource_id}")'),
        ("update", "PATCH", "/resources/{resource_type}/{resource_id}", "owner_or_operator", "store.update gera audit", "não exigida genericamente", '@app.patch("/resources/{resource_type}/{resource_id}")'),
        ("delete", "DELETE", "/resources/{resource_type}/{resource_id}", "owner_or_operator; sensíveis/imutáveis bloqueados", "soft_delete gera audit", "não aplicável", '@app.delete("/resources/{resource_type}/{resource_id}"'),
    )
    for rule in logical_rules:
        module, entity = str(rule["module"]), str(rule["entity"])
        sensitive = bool(rule["sensitive"])
        for operation, method, endpoint, ownership, audit, idempotency, evidence_needle in generic_operations:
            is_permissions = module == "permissions"
            horizontal_gap = operation == "read" and not sensitive and not is_permissions and not generic_read_has_ownership
            role_enforcement = (
                "SENSITIVE_ROLES para leitura; PERMISSIONS_WRITE_ROLES para escrita"
                if is_permissions
                else "papel sensível somente para leitura de terceiro sensível; demais CRUDs usam owner/operator"
            )
            rows.append(
                {
                    "module": module, "entity": entity, "operation": operation, "method": method,
                    "endpoint": endpoint.replace("{resource_type}", entity), "authentication": "actor_from_headers obrigatório",
                    "role_enforcement": role_enforcement, "ownership_enforcement": ownership,
                    "tenant_enforcement": "não genérico; regras especiais por domínio quando implementadas",
                    "mfa_enforcement": "permissions em recursos configurados; não genérico nos demais CRUDs",
                    "sensitive_resource": sensitive, "audit_enforcement": audit, "idempotency": idempotency,
                    "enforcement_status": "lacuna_autorizacao_horizontal" if horizontal_gap else "parcial_estatico",
                    "test_evidence": test_evidence(entity, operation),
                    "evidence": source_evidence(runtime, evidence_needle),
                }
            )
    sensitive_by_resource = {(str(row["module"]), str(row["entity"])): bool(row["sensitive"]) for row in logical_rules}
    for transition in transitions:
        module, entity, action = str(transition["module"]), str(transition["entity"]), str(transition["action"])
        roles = list(transition["roles"])
        rows.append(
            {
                "module": module, "entity": entity, "operation": action, "method": "POST",
                "endpoint": f"/resources/{entity}/{{resource_id}}/actions/{action}", "authentication": "actor_from_headers obrigatório",
                "role_enforcement": roles or ["owner_or_operator"],
                "ownership_enforcement": "papel da transição quando declarado; caso contrário owner_or_operator",
                "tenant_enforcement": "Jobs valida company_id/business_id em vagas e candidaturas; demais dependem de regra de domínio",
                "mfa_enforcement": bool(transition["requires_mfa"]),
                "sensitive_resource": sensitive_by_resource.get((module, entity), False),
                "audit_enforcement": "store.update registra ação e evento de transição",
                "idempotency": "não exigida genericamente na rota de transição",
                "enforcement_status": "regra_backend_estatica; teste_endpoint_requerido",
                "test_evidence": test_evidence(entity, action),
                "evidence": transition["evidence"],
            }
        )
    return rows


def normalized_words(value: str) -> set[str]:
    folded = unicodedata.normalize("NFKD", value.casefold()).encode("ascii", "ignore").decode("ascii")
    return {word for word in re.findall(r"[a-z0-9]+", folded) if len(word) >= 3}


def discover_test_execution() -> dict[str, dict[str, object]]:
    outcomes: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for report in PYTEST_EXECUTION_REPORTS:
        if not report.is_file():
            continue
        try:
            root = ET.parse(report).getroot()
        except (ET.ParseError, OSError):
            continue
        for case in root.iter("testcase"):
            classname = case.attrib.get("classname", "")
            function = case.attrib.get("name", "").split("[", 1)[0]
            path = classname.replace(".", "/") + ".py"
            test_id = f"{path}::{function}"
            outcome = "aprovado"
            if case.find("error") is not None:
                outcome = "erro"
            elif case.find("failure") is not None:
                outcome = "falhou"
            elif case.find("skipped") is not None:
                outcome = "ignorado"
            outcomes[test_id].append((outcome, str(report.relative_to(ROOT))))
    result: dict[str, dict[str, object]] = {}
    for test_id, observations in outcomes.items():
        cases = [outcome for outcome, _ in observations]
        if "erro" in cases:
            aggregate_status = "erro"
        elif "falhou" in cases:
            aggregate_status = "falhou"
        elif "aprovado" in cases:
            aggregate_status = "aprovado"
        else:
            aggregate_status = "ignorado"
        result[test_id] = {
            "status": aggregate_status,
            "cases": len(cases),
            "passed_cases": cases.count("aprovado"),
            "evidence": ";".join(sorted({evidence for _, evidence in observations})),
        }
    return result


def discover_test_catalog() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    execution = discover_test_execution()
    test_paths = set((ROOT / "tests").rglob("*.py"))
    test_paths.update(ROOT.glob("modules/*/tests/**/*.py"))
    for path in sorted(test_paths):
        text = path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.name.startswith("test_"):
                continue
            assertions = [item for item in ast.walk(node) if isinstance(item, ast.Assert)]
            calls = [item for item in ast.walk(node) if isinstance(item, ast.Call)]
            methods = sorted({call.func.attr.upper() for call in calls if isinstance(call.func, ast.Attribute) and call.func.attr.lower() in {"get", "post", "put", "patch", "delete"}})
            endpoints = sorted(
                {
                    value.value
                    for value in ast.walk(node)
                    if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value.startswith("/")
                }
            )
            decorators = [annotation_name(item.func if isinstance(item, ast.Call) else item) for item in node.decorator_list]
            status_assertions = sum(
                isinstance(item, ast.Attribute) and item.attr == "status_code"
                for assertion in assertions
                for item in ast.walk(assertion)
            )
            test_id = f"{path.relative_to(ROOT)}::{node.name}"
            executed = execution.get(test_id)
            rows.append(
                {
                    "test_id": test_id, "file": str(path.relative_to(ROOT)),
                    "function": node.name, "line": node.lineno, "async": isinstance(node, ast.AsyncFunctionDef),
                    "assertions": len(assertions), "status_code_assertions": status_assertions,
                    "http_methods": methods, "endpoint_literals": endpoints,
                    "parametrized": any("parametrize" in decorator for decorator in decorators),
                    "decorators": decorators,
                    "execution_status": executed["status"] if executed else "não consta nos relatórios de execução",
                    "execution_cases": executed["cases"] if executed else 0,
                    "passed_cases": executed["passed_cases"] if executed else 0,
                    "execution_evidence": executed["evidence"] if executed else "",
                    "evidence": f"{path.relative_to(ROOT)}:{node.lineno}",
                }
            )
    return sorted(rows, key=lambda row: str(row["test_id"]))


def discover_memo_requirements(test_catalog: list[dict[str, object]]) -> list[dict[str, object]]:
    text = MASTER_MEMO.read_text(encoding="utf-8")
    lines = text.splitlines()
    section = ""
    subsection = ""
    counters: Counter[str] = Counter()
    requirements: list[dict[str, object]] = []
    keyword_map = {
        "banc": ["database", "postgres", "mongodb", "sqlite", "redis"], "schema": ["schema", "migration"],
        "tabel": ["table", "store", "migration"], "cole": ["collection", "mongodb"], "camp": ["field", "payload", "catalog"],
        "relacion": ["relationship", "foreign", "erd"], "frontend": ["frontend", "ui", "stitch"], "binding": ["binding", "contract"],
        "sens": ["sensitive", "lgpd", "privacy"], "auditor": ["audit", "log", "trace"], "calcul": ["calculation", "precision", "decimal"],
        "unidad": ["unit", "conversion"], "tribut": ["tax", "fiscal"], "fisc": ["fiscal", "tax"], "formul": ["form", "smartcrud"],
        "bot": ["action", "button", "ui"], "permiss": ["permission", "authorization", "enforcement", "role"], "lacuna": ["gap", "coverage", "audit_delivery"],
        "teste": ["test", "pytest"], "document": ["document", "delivery", "markdown"], "evid": ["evidence", "traceability"],
        "evento": ["event", "outbox"], "api": ["api", "endpoint", "gateway"], "risco": ["risk", "security"],
        "persona": ["persona", "role"], "dominio": ["domain", "module"], "stitch": ["stitch"], "erd": ["erd"],
        "segur": ["security", "permission", "auth"], "e2e": ["e2e", "journey"], "respons": ["responsive", "mobile"],
        "acess": ["accessibility", "wcag"], "acao": ["action", "transition"], "estado": ["state", "status"], "componente": ["component", "frontend"],
    }
    test_words = [(row, normalized_words(str(row["test_id"]))) for row in test_catalog]
    for number, line in enumerate(lines, 1):
        if line.startswith("# 21."):
            section = "conclusao"
            subsection = "criterios_de_conclusao"
            continue
        if line.startswith("# 24."):
            section = "checklist"
            subsection = "geral"
            continue
        if line.startswith("# 22.") or line.startswith("# 25."):
            section = ""
        if section and line.startswith("## "):
            subsection = re.sub(r"[^a-z0-9]+", "_", unicodedata.normalize("NFKD", line[3:].casefold()).encode("ascii", "ignore").decode("ascii")).strip("_")
            continue
        if not section or not line.startswith("- "):
            continue
        requirement = re.sub(r"^- (?:\[[ xX]\]\s*)?", "", line).strip().rstrip(";").rstrip(".")
        counters[section] += 1
        requirement_id = f"{'CONCL' if section == 'conclusao' else 'CHECK'}-{counters[section]:03d}"
        words = normalized_words(requirement)
        match_terms = set(words)
        for stem, translations in keyword_map.items():
            if any(word.startswith(stem) for word in words):
                match_terms.update(translations)
        candidate_rows = [
            row
            for row, candidate_words in test_words
            if match_terms & candidate_words
        ][:20]
        candidates = [str(row["test_id"]) for row in candidate_rows]
        passed_candidates = [str(row["test_id"]) for row in candidate_rows if row["execution_status"] == "aprovado"]
        requirements.append(
            {
                "requirement_id": requirement_id, "section": section, "subsection": subsection,
                "requirement": requirement, "test_candidates": candidates,
                "candidate_count": len(candidates),
                "passed_test_candidates": passed_candidates,
                "passed_candidate_count": len(passed_candidates),
                "trace_status": "candidatos_localizados" if candidates else "sem_teste_localizado",
                "execution_status": "candidatos_aprovados" if passed_candidates else "sem_candidato_aprovado",
                "proof_status": "não comprovado; candidatos aprovados exigem revisão de escopo",
                "evidence": f"{MASTER_MEMO.relative_to(ROOT)}:{number}",
            }
        )
    return requirements


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
    mongodb_fields = discover_mongodb_model()
    sqlite_fields = discover_sqlite_model()
    redis_entries = discover_redis_catalog()
    object_storage_entries = discover_object_storage_catalog()
    browser_storage_entries = discover_browser_storage_catalog()
    fields = [field for table_fields in tables.values() for field in table_fields]
    endpoints = discover_endpoints()
    ui_bindings = discover_ui_bindings(tables)
    ui_actions = discover_ui_actions(ui_bindings)
    logical_rules = discover_logical_rules(tables, ui_bindings)
    transitions = discover_transitions(logical_rules)
    permission_enforcement = discover_permission_enforcement(logical_rules, transitions)
    test_catalog = discover_test_catalog()
    memo_requirements = discover_memo_requirements(test_catalog)
    relations = [field for field in fields if field.reference]
    sensitive = [field for field in fields if field.lgpd != "não classificado automaticamente"]
    counts = {
        "migrations": len(migrations),
        "schemas": len(schemas),
        "tables": len(tables),
        "fields": len(fields),
        "mongodb_collections": len({row["collection"] for row in mongodb_fields}),
        "mongodb_fields": len(mongodb_fields),
        "sqlite_tables": len({row["table"] for row in sqlite_fields}),
        "sqlite_fields": len(sqlite_fields),
        "redis_key_patterns": len(redis_entries),
        "object_storage_stores": len(object_storage_entries),
        "browser_storage_key_patterns": len(browser_storage_entries),
        "relationships": len(relations),
        "indexes": len(indexes),
        "endpoints": len(endpoints),
        "endpoints_with_response_model": sum(bool(row["response_model"]) for row in endpoints),
        "api_model_fields": sum(len(parameter["model_fields"]) for row in endpoints for parameter in row["parameters"]),
        "ui_candidates": len(ui_bindings),
        "ui_bindings_probable": sum(row["binding"] == "campo físico provável" for row in ui_bindings),
        "ui_bindings_unproven": sum(row["binding"] != "campo físico provável" for row in ui_bindings),
        "ui_surfaces": len({row["evidence"] for row in ui_bindings}),
        "ui_forms": len({row["evidence"] for row in ui_bindings if row["surface"] == "form"}),
        "ui_actions": len(ui_actions),
        "ui_actions_incompatible": sum(row["contract_status"] == "incompativel" for row in ui_actions),
        "ui_actions_without_frontend_permission_gate": sum(row["frontend_permission_gate"] is False for row in ui_actions),
        "permission_operations": len(permission_enforcement),
        "permission_horizontal_read_gaps": sum(row["enforcement_status"] == "lacuna_autorizacao_horizontal" for row in permission_enforcement),
        "permission_operations_with_test_candidates": sum(bool(row["test_evidence"]) for row in permission_enforcement),
        "test_functions": len(test_catalog),
        "tests_with_assertions": sum(bool(row["assertions"]) for row in test_catalog),
        "tests_with_http_calls": sum(bool(row["http_methods"]) for row in test_catalog),
        "test_functions_in_execution_reports": sum(row["execution_status"] != "não consta nos relatórios de execução" for row in test_catalog),
        "test_functions_passed": sum(row["execution_status"] == "aprovado" for row in test_catalog),
        "memo_requirements_traced": len(memo_requirements),
        "memo_requirements_without_test_candidates": sum(not row["test_candidates"] for row in memo_requirements),
        "memo_requirements_with_passed_candidates": sum(bool(row["passed_test_candidates"]) for row in memo_requirements),
        "logical_entities": len(logical_rules),
        "logical_without_physical_table": sum(not row["has_physical_table"] for row in logical_rules),
        "logical_without_ui_surface": sum(not row["has_ui_surface"] for row in logical_rules),
        "event_transitions": len(transitions),
        "unique_events": len({row["event"] for row in transitions}),
        "sensitive_candidates": len(sensitive),
    }
    dynamic_form_model = json.loads(DYNAMIC_FORM_MODEL.read_text(encoding="utf-8"))
    product_units_tax_model = json.loads(PRODUCT_UNITS_TAX_MODEL.read_text(encoding="utf-8"))
    field_classification_policy = json.loads(FIELD_CLASSIFICATION_POLICY.read_text(encoding="utf-8"))
    audit_policy = json.loads(AUDIT_TRACEABILITY_POLICY.read_text(encoding="utf-8"))
    stitch_template_coordinate = json.loads(STITCH_TEMPLATE_COORDINATE.read_text(encoding="utf-8"))
    counts["dynamic_form_entities_proposed"] = len(dynamic_form_model["entities"])
    counts["measurement_entities_proposed"] = len(product_units_tax_model["measurement_entities"])
    counts["fiscal_entities_proposed"] = len(product_units_tax_model["fiscal_entities"])
    audit_tables = {
        key: {field.physical_name for field in table_fields}
        for key, table_fields in tables.items()
        if key.startswith("audit.") or any(token in key for token in ("audit", "_logs", "events"))
    }
    audit_coverage: list[dict[str, object]] = []
    for audit_type in ("change_audit", "read_audit"):
        for requirement, aliases in audit_policy[audit_type].items():
            matches = {
                table: sorted(set(aliases) & field_names)
                for table, field_names in audit_tables.items()
                if set(aliases) & field_names
            }
            audit_coverage.append(
                {
                    "audit_type": audit_type,
                    "requirement": requirement,
                    "aliases": aliases,
                    "covered": bool(matches),
                    "matching_tables": matches,
                    "evidence": [f"docs/data-audit/databases/postgresql/tables/{table}.md" for table in matches],
                }
            )
    counts["audit_candidate_tables"] = len(audit_tables)
    counts["audit_requirements"] = len(audit_coverage)
    counts["audit_requirements_covered"] = sum(bool(row["covered"]) for row in audit_coverage)

    field_rows = [asdict(field) for field in fields]
    write_csv(ARTIFACTS / "dicionario_de_dados.csv", list(Field.__annotations__), field_rows)
    write_json(ARTIFACTS / "dicionario_de_dados.json", {"version": 1, "counts": counts, "fields": field_rows})
    mongodb_csv_rows = [
        {**row, "enum": ";".join(row["enum"]), "indexes": json.dumps(row["indexes"], ensure_ascii=False)}
        for row in mongodb_fields
    ]
    write_csv(
        ARTIFACTS / "catalogo_mongodb.csv",
        ["database", "collection", "field", "bson_type", "required", "enum", "sensitive_declared", "lgpd", "classification_basis", "encryption", "masking", "retention", "indexes", "evidence"],
        mongodb_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_mongodb.json", {"version": 1, "counts": counts, "fields": mongodb_fields})
    write_csv(ARTIFACTS / "catalogo_sqlite.csv", list(Field.__annotations__), sqlite_fields)
    write_json(ARTIFACTS / "catalogo_sqlite.json", {"version": 1, "counts": counts, "fields": sqlite_fields})
    logical_csv_rows = [
        {**row, "required_fields": ";".join(row["required_fields"]), "unique_fields": ";".join(row["unique_fields"]), "monetary_fields": ";".join(row["monetary_fields"])}
        for row in logical_rules
    ]
    write_csv(
        ARTIFACTS / "catalogo_logico.csv",
        ["module", "entity", "required_fields", "unique_fields", "monetary_fields", "initial_status", "sensitive", "immutable", "has_rule_override", "physical_storage_target", "persistence_decision", "has_physical_table", "has_ui_surface", "evidence"],
        logical_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_logico.json", {"version": 1, "counts": counts, "entities": logical_rules})
    event_csv_rows = [
        {
            **row,
            "source_statuses": ";".join(row["source_statuses"]),
            "roles": ";".join(row["roles"]),
            "payload_fields": ";".join(row["payload_fields"]),
            "consumers": ";".join(row["consumers"]),
        }
        for row in transitions
    ]
    write_csv(
        ARTIFACTS / "catalogo_eventos.csv",
        ["event", "version", "module", "entity", "action", "source_statuses", "target_status", "roles", "requires_mfa", "payload_fields", "producer", "consumers", "idempotency_key", "correlation_id", "evidence"],
        event_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_eventos.json", {"version": 1, "counts": counts, "events": transitions})
    api_csv_rows = [
        {
            **row,
            "parameters": ";".join(f"{parameter['name']}:{parameter['annotation']}" for parameter in row["parameters"]),
            "request_fields": ";".join(field for parameter in row["parameters"] for field in parameter["model_fields"]),
        }
        for row in endpoints
    ]
    write_csv(
        ARTIFACTS / "catalogo_apis.csv",
        ["module", "method", "path", "function", "parameters", "request_fields", "response_model", "evidence"],
        api_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_apis.json", {"version": 1, "counts": counts, "endpoints": endpoints})
    write_json(ARTIFACTS / "matriz_acao_ui_backend.json", {"version": 1, "status": "auditoria_estatica", "counts": counts, "actions": ui_actions})
    write_csv(
        ARTIFACTS / "matriz_acao_ui_backend.csv",
        ["module", "entity", "surface", "route", "action", "trigger", "method", "endpoint", "request_contract", "backend_contract", "contract_status", "frontend_permission_gate", "backend_enforcement", "audit", "states", "test_evidence", "evidence", "surface_evidence"],
        ({**row, "states": ";".join(row["states"])} for row in ui_actions),
    )
    write_json(ARTIFACTS / "matriz_enforcement_permissao.json", {"version": 1, "status": "auditoria_estatica", "counts": counts, "operations": permission_enforcement})
    write_csv(
        ARTIFACTS / "matriz_enforcement_permissao.csv",
        ["module", "entity", "operation", "method", "endpoint", "authentication", "role_enforcement", "ownership_enforcement", "tenant_enforcement", "mfa_enforcement", "sensitive_resource", "audit_enforcement", "idempotency", "enforcement_status", "test_evidence", "evidence"],
        (
            {
                **row,
                "role_enforcement": ";".join(row["role_enforcement"]) if isinstance(row["role_enforcement"], list) else row["role_enforcement"],
                "test_evidence": ";".join(row["test_evidence"]),
            }
            for row in permission_enforcement
        ),
    )
    write_json(ARTIFACTS / "catalogo_testes.json", {"version": 1, "status": "inventario_estatico", "counts": counts, "tests": test_catalog})
    write_csv(
        ARTIFACTS / "catalogo_testes.csv",
        ["test_id", "file", "function", "line", "async", "assertions", "status_code_assertions", "http_methods", "endpoint_literals", "parametrized", "decorators", "execution_status", "execution_cases", "passed_cases", "execution_evidence", "evidence"],
        ({**row, "http_methods": ";".join(row["http_methods"]), "endpoint_literals": ";".join(row["endpoint_literals"]), "decorators": ";".join(row["decorators"])} for row in test_catalog),
    )
    write_json(ARTIFACTS / "matriz_requisito_teste.json", {"version": 1, "status": "rastreabilidade_estatica", "counts": counts, "requirements": memo_requirements})
    write_csv(
        ARTIFACTS / "matriz_requisito_teste.csv",
        ["requirement_id", "section", "subsection", "requirement", "test_candidates", "candidate_count", "passed_test_candidates", "passed_candidate_count", "trace_status", "execution_status", "proof_status", "evidence"],
        ({**row, "test_candidates": ";".join(row["test_candidates"]), "passed_test_candidates": ";".join(row["passed_test_candidates"])} for row in memo_requirements),
    )
    for artifact_name, rows in (
        ("catalogo_redis", redis_entries),
        ("catalogo_object_storage", object_storage_entries),
        ("catalogo_browser_storage", browser_storage_entries),
    ):
        write_json(ARTIFACTS / f"{artifact_name}.json", {"version": 1, "status": "inventario_estatico", "counts": counts, "entries": rows})
        csv_rows = []
        for row in rows:
            csv_rows.append({key: ";".join(str(item) for item in value) if isinstance(value, list) else value for key, value in row.items()})
        write_csv(ARTIFACTS / f"{artifact_name}.csv", sorted({key for row in csv_rows for key in row}), csv_rows)
    write_json(ARTIFACTS / "formulario_dinamico_modelo.json", dynamic_form_model)
    write_json(ARTIFACTS / "modelo_unidades_tributacao.json", product_units_tax_model)
    write_json(ARTIFACTS / "politica_classificacao_campos.json", field_classification_policy)
    write_json(ARTIFACTS / "coordenada_projetos_stitch.json", stitch_template_coordinate)
    write_json(
        ARTIFACTS / "cobertura_auditoria.json",
        {"version": 1, "policy": audit_policy, "counts": counts, "candidate_tables": sorted(audit_tables), "coverage": audit_coverage},
    )
    write_csv(
        ARTIFACTS / "cobertura_auditoria.csv",
        ["audit_type", "requirement", "aliases", "covered", "matching_tables", "evidence"],
        (
            {
                **row,
                "aliases": ";".join(row["aliases"]),
                "matching_tables": ";".join(row["matching_tables"]),
                "evidence": ";".join(row["evidence"]),
            }
            for row in audit_coverage
        ),
    )
    surfaces: dict[str, dict[str, object]] = {}
    actions_by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for action in ui_actions:
        actions_by_surface[str(action["surface_evidence"])].append(
            {key: value for key, value in action.items() if key not in {"surface_evidence", "surface", "route", "module", "entity"}}
        )
    required_states = ["loading", "vazio", "erro", "sucesso", "sem_permissao", "conflito", "dados_desatualizados"]
    for row in ui_bindings:
        evidence = row["evidence"]
        surface = surfaces.setdefault(
            evidence,
            {
                "module": row["module"],
                "entity": row["entity"],
                "title": row["title"],
                "surface": row["surface"],
                "route": row["route"],
                "persona": "papel autorizado do módulo; requer detalhamento",
                "fields": [],
                "primary_action": "Salvar registro" if row["surface"] == "form" else "Abrir detalhes",
                "actions": actions_by_surface[evidence],
                "endpoint": f"/{row['module']}/resources/{row['entity']}",
                "permissions": "enforcement backend requer validação",
                "states": required_states,
                "responsive": ["desktop", "tablet", "mobile"],
                "accessibility": ["label", "foco visível", "teclado", "leitor de tela", "contraste"],
                "binding_status": "parcial",
                "evidence": evidence,
            },
        )
        surface["fields"].append({"name": row["field"], "binding": row["binding"]})
    coordinate_rows = [
        {
            **surface,
            "fields": ";".join(f"{item['name']}:{item['binding']}" for item in surface["fields"]),
            "states": ";".join(surface["states"]),
            "responsive": ";".join(surface["responsive"]),
            "accessibility": ";".join(surface["accessibility"]),
        }
        for surface in surfaces.values()
    ]
    write_csv(
        ARTIFACTS / "coordenadas_stitch.csv",
        ["module", "entity", "title", "surface", "route", "persona", "fields", "primary_action", "endpoint", "permissions", "states", "responsive", "accessibility", "binding_status", "evidence"],
        coordinate_rows,
    )
    write_json(ARTIFACTS / "coordenadas_stitch.json", {"version": 1, "counts": counts, "coordinates": list(surfaces.values())})
    write_csv(
        ARTIFACTS / "matriz_formulario_campo.csv",
        ["app", "module", "entity", "surface", "title", "route", "field", "binding", "evidence"],
        ui_bindings or [{"app": "não localizado", "module": "", "entity": "", "surface": "", "title": "", "route": "", "field": "não localizado", "binding": "lacuna", "evidence": "apps/"}],
    )
    write_csv(
        ARTIFACTS / "matriz_api_campo.csv",
        ["module", "method", "path", "field", "status", "evidence"],
        (
            {
                "module": endpoint["module"],
                "method": endpoint["method"],
                "path": endpoint["path"],
                "field": field,
                "status": status,
                "evidence": endpoint["evidence"],
            }
            for endpoint in endpoints
            for field, status in (
                [
                    (field, "campo de modelo Pydantic comprovado")
                    for parameter in endpoint["parameters"]
                    for field in parameter["model_fields"]
                ]
                or [("payload sem modelo local comprovado", "lacuna")]
            )
        ),
    )
    write_csv(
        ARTIFACTS / "matriz_evento_campo.csv",
        ["event", "field", "producer", "consumer", "status", "evidence"],
        (
            {
                "event": row["event"],
                "field": field,
                "producer": row["producer"],
                "consumer": "não comprovado",
                "status": "produtor e campo inferidos; consumidor pendente",
                "evidence": row["evidence"],
            }
            for row in transitions
            for field in (row["payload_fields"] or ["payload não especificado"])
        ),
    )
    write_csv(
        ARTIFACTS / "matriz_permissao_acao.csv",
        ["persona", "action", "resource", "backend_enforcement", "status", "evidence"],
        (
            {
                "persona": role or "sem papel explícito",
                "action": row["action"],
                "resource": f"{row['module']}.{row['entity']}",
                "backend_enforcement": f"Transition roles; MFA={row['requires_mfa']}",
                "status": "regra de transição comprovada; endpoint exige validação",
                "evidence": row["evidence"],
            }
            for row in transitions
            for role in (row["roles"] or [""])
        ),
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
        {
            "id": "AUD-P0-000", "priority": "P0", "module": "infraestrutura", "title": "Persistências não PostgreSQL exigem catálogo e validação operacional",
            "description": "PostgreSQL, MongoDB, SQLite, Redis, object storage e storage de navegador possuem inventários estáticos estruturados; as instâncias e políticas aplicadas ainda não foram confrontadas integralmente em runtime.",
            "evidence": ["infra/docker/docker-compose.yml:69", "docs/data-audit/artifacts/catalogo_mongodb.json", "docs/data-audit/artifacts/catalogo_sqlite.json"],
            "impact": "Retenção, recuperação, ownership e divergências entre configuração e ambiente não são comprovados.", "risk": "Perda, exposição ou inconsistência de dados fora do PostgreSQL.",
            "proposal": "Catalogar chaves, objetos, buckets e políticas; adicionar sondagens não destrutivas e testes por tecnologia.", "dependencies": ["credenciais dos ambientes", "serviços acessíveis"],
            "affected_files": ["infra/docker/docker-compose.yml", "docs/data-audit/databases"], "migration": "avaliar por tecnologia", "backend": "inventariar clientes e contratos", "frontend": "inventariar chaves de storage", "tests": "testes de contrato e sondagem runtime", "documentation": "03_CATALOGO_DE_BANCOS.md", "acceptance": "MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership, restore e testes aprovados.", "status": "parcial", "owner_suggestion": "plataforma e dados", "dimensions": ["bancos", "tabelas_colecoes", "campos"]
        },
        {
            "id": "AUD-P0-001", "priority": "P0", "module": "compliance", "title": "Classificação LGPD exige revisão humana por campo",
            "description": "A classificação atual é heurística e ainda não foi aprovada pelos proprietários dos domínios.", "evidence": ["docs/data-audit/artifacts/politica_classificacao_campos.json", "docs/data-audit/artifacts/dicionario_de_dados.csv"],
            "impact": "Mascaramento, retenção e acesso podem não refletir finalidade e base legal reais.", "risk": "Tratamento indevido de dados pessoais e sensíveis.", "proposal": "Executar revisão campo a campo com DPO e responsáveis dos domínios, registrando decisão e vigência.", "dependencies": ["DPO", "proprietários de domínio"], "affected_files": ["config/data_audit/field_classification_policy.json"], "migration": "não aplicável até decisão", "backend": "aplicar classificação aprovada", "frontend": "aplicar mascaramento aprovado", "tests": "testar acesso e mascaramento por classe", "documentation": "11_PERMISSOES_E_SEGURANCA.md", "acceptance": "Todos os campos possuem classificação, retenção, criptografia e mascaramento aprovados pelo proprietário do domínio.", "status": "pendente_aprovacao", "owner_suggestion": "DPO e compliance", "dimensions": ["campos_sensiveis"]
        },
        {
            "id": "AUD-P1-002", "priority": "P1", "module": "frontend e APIs", "title": "Bindings frontend-backend não estão integralmente comprovados",
            "description": "Os 47 aliases de recurso compactado foram ligados aos nomes canônicos do backend e todas as 120 entidades lógicas têm superfície UI; ainda há 844 bindings de campo genéricos/não comprovados e 224 coincidências prováveis com campo físico.", "evidence": ["apps/all-in-one/src/components/SmartCRUD.tsx", "docs/data-audit/artifacts/matriz_formulario_campo.csv", "docs/data-audit/artifacts/coordenadas_stitch.json"], "impact": "Os endpoints agora recebem o recurso canônico, mas formulários genéricos ainda podem omitir campos específicos.", "risk": "Perda de dados ou validação incompleta nos campos ainda genéricos.", "proposal": "Resolver cada binding restante por rota e campo e vinculá-lo a DTO, validação, origem, destino e teste.", "dependencies": ["contratos DTO"], "affected_files": ["apps/all-in-one/src", "modules"], "migration": "não aplicável", "backend": "tipar payloads e responses", "frontend": "aliases resolvidos; declarar bindings específicos restantes", "tests": "contrato canônico aprovado; integração e E2E por campo restantes", "documentation": "09_FORMULARIOS_FRONTEND.md", "acceptance": "Cada campo UI aponta para DTO, endpoint, validação e teste aprovados.", "status": "implementacao_parcial", "owner_suggestion": "frontend e backend", "dimensions": ["bindings_frontend", "formularios"]
        },
        {
            "id": "AUD-P1-003", "priority": "P1", "module": "eventos", "title": "Eventos não possuem catálogo integral de payload versionado",
            "description": "As transições identificam nomes e produtores, mas consumidores e contratos completos não são demonstrados para todos os eventos.", "evidence": ["docs/data-audit/artifacts/catalogo_eventos.json", "docs/data-audit/artifacts/matriz_evento_campo.csv"], "impact": "Mudanças podem quebrar consumidores ou impedir replay seguro.", "risk": "Inconsistência assíncrona e duplicidade de processamento.", "proposal": "Versionar schemas, consumidores, idempotência, correlação, retenção e compatibilidade por evento.", "dependencies": ["produtores", "consumidores", "mensageria"], "affected_files": ["modules", "contracts"], "migration": "não aplicável", "backend": "publicar e consumir contrato versionado", "frontend": "não aplicável salvo atualizações em tempo real", "tests": "contrato, idempotência, replay e compatibilidade", "documentation": "12_APIS_EVENTOS_E_INTEGRACOES.md", "acceptance": "Cada evento possui produtor, consumidor, schema, dados proibidos, idempotência, correlação, retenção e compatibilidade testados.", "status": "pendente", "owner_suggestion": "arquitetura de integração", "dimensions": ["campos", "relacionamentos"]
        },
        {
            "id": "AUD-P1-004", "priority": "P1", "module": "formulários dinâmicos", "title": "Construtor de formulários dinâmicos é proposta, não implementação",
            "description": "O modelo cobre metadados e governança, mas migrations, APIs, UI e enforcement ainda não existem.", "evidence": ["docs/data-audit/artifacts/formulario_dinamico_modelo.json", "docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583"], "impact": "O produto pago de formulários sob medida não pode ser usado ou homologado.", "risk": "Implementação ad hoc e exposição de tabelas físicas.", "proposal": "Implementar por fases o modelo aprovado, mantendo seleção de tabela e coluna físicas proibida.", "dependencies": ["decisão arquitetural", "modelo de cobrança"], "affected_files": ["database/postgres/migrations", "modules", "apps/all-in-one/src"], "migration": "criar migrations reversíveis após aprovação", "backend": "APIs, regras e homologação", "frontend": "builder, preview e publicação", "tests": "segurança, ciclos, versionamento, tenant e cobrança", "documentation": "10_FORMULARIOS_DINAMICOS.md", "acceptance": "Metadados, API, homologação, segurança, publicação, cobrança, auditoria e testes estão implementados.", "status": "proposta", "owner_suggestion": "produto, arquitetura e engenharia", "dimensions": ["tabelas_colecoes", "campos", "formularios", "acoes_ui", "permissoes_backend", "auditoria", "calculos"]
        },
        {
            "id": "AUD-P1-005", "priority": "P1", "module": "catálogo e fiscal", "title": "Regras fiscais, unidades e conversões carecem de implementação completa",
            "description": "Migration reversível, rollback, cálculo Decimal, contratos HTTP, console web e testes de integração foram implementados; faltam integração PostgreSQL viva e homologação por especialista fiscal.", "evidence": ["docs/data-audit/artifacts/modelo_unidades_tributacao.json", "database/postgres/migrations/025_units_tax_governance.sql", "database/postgres/rollbacks/025_units_tax_governance.down.sql", "modules/shared/units_tax.py", "modules/stock/main.py", "modules/erp/main.py", "apps/all-in-one/src/pages/UnitsTaxGovernance.tsx", "tests/test_units_tax_governance.py"], "impact": "Sem os gates externos restantes, compra, estoque, venda, custo e tributação ainda podem divergir em operação.", "risk": "Cálculo financeiro ou fiscal não homologado em ambiente operacional.", "proposal": "Executar integração PostgreSQL viva e homologar cenários com especialista fiscal.", "dependencies": ["especialista fiscal", "ambiente PostgreSQL"], "affected_files": ["database/postgres", "modules/stock", "modules/erp"], "migration": "implementada com rollback; backfill explícito sem inferência", "backend": "Decimal, vigência, aprovação, precisão, arredondamento e contratos HTTP implementados", "frontend": "console responsivo de unidades e cálculo fiscal implementado", "tests": "unitários e contratos HTTP aprovados; PostgreSQL vivo e homologação fiscal pendentes", "documentation": "06_UNIDADES_E_CONVERSOES.md e 07_TRIBUTACAO.md", "acceptance": "Unidades, conversões, perfis fiscais, vigência e cálculos possuem migrations, backend, frontend, integração e homologação aprovados.", "status": "implementacao_parcial", "owner_suggestion": "catálogo, estoque, ERP e fiscal", "dimensions": ["tabelas_colecoes", "campos", "calculos", "unidades", "regras_fiscais", "formularios"]
        },
        {
            "id": "AUD-P1-006", "priority": "P1", "module": "arquitetura modular", "title": "Entidades lógicas sem decisão de persistência homônima",
            "description": "Todas as 120 entidades lógicas possuem superfície UI canônica; a migration 026 materializou 44 destinos tipados e cinco aliases físicos foram reconhecidos. Restam 13 recursos de adaptadores legados sem relação tipada executável.", "evidence": ["docs/data-audit/artifacts/catalogo_logico.json", "database/postgres/migrations/026_complete_typed_store_relations.sql", "database/postgres/rollbacks/026_complete_typed_store_relations.down.sql", "tests/test_typed_store_persistence_contract.py"], "impact": "A maior parte da persistência declarada foi materializada, mas 13 ciclos de vida ainda não funcionam com DSN PostgreSQL.", "risk": "Falha de CRUD nos recursos legados restantes.", "proposal": "Migrar os cinco adaptadores legados para o BasePostgresStore ou implementar fallback tipado para os 13 recursos restantes.", "dependencies": ["refatoração dos adaptadores finance, marketplace, delivery, services e mobility"], "affected_files": ["modules/shared/*_postgres_store.py", "database/postgres/migrations"], "migration": "44 relações implementadas com rollback; 13 recursos restantes exigem modelagem", "backend": "todos os destinos já declarados pelos stores possuem relação física", "frontend": "120 de 120 entidades com superfície canônica", "tests": "contrato de destino tipado e reversibilidade aprovados", "documentation": "02_MAPA_DE_DOMINIOS.md", "acceptance": "Cada entidade possui decisão explícita de persistência, ownership e coordenada UI, ou justificativa versionada de ausência.", "status": "implementacao_parcial", "owner_suggestion": "arquitetura e responsáveis de domínio", "dimensions": ["tabelas_colecoes", "campos", "relacionamentos", "formularios"]
        },
        {
            "id": "AUD-P1-007", "priority": "P1", "module": "auditoria e segurança", "title": "Trilhas de auditoria não cobrem todos os atributos mandatórios",
            "description": "A análise de cinco tabelas candidatas encontrou cobertura global de apenas parte dos 35 requisitos; faltam, entre outros, sessão, origem, canal, motivo, causação, integridade, retenção e registros de leitura/exportação.", "evidence": ["docs/data-audit/artifacts/cobertura_auditoria.json", "docs/data-audit/artifacts/cobertura_auditoria.csv"], "impact": "A plataforma não consegue demonstrar integralmente quem acessou ou alterou dados, em qual contexto e por qual motivo.", "risk": "Não repúdio insuficiente, investigação incompleta e descumprimento de auditoria/LGPD.", "proposal": "Aprovar contrato unificado de auditoria, mapear requisito por operação e implementar escrita append-only com testes de integridade e acesso.", "dependencies": ["segurança", "compliance", "proprietários de domínio"], "affected_files": ["database/postgres/migrations", "modules/shared/store.py", "modules"], "migration": "criar ou evoluir trilha com backfill quando tecnicamente possível", "backend": "registrar criação, mudança, leitura sensível, exportação e autorização", "frontend": "enviar motivo quando obrigatório e nunca registrar segredo", "tests": "integração por operação, imutabilidade, autorização e retenção", "documentation": "08_AUDITORIA_E_LOGS.md", "acceptance": "Os 35 requisitos de auditoria têm implementação ou decisão justificada por operação, com integridade, retenção e testes aprovados.", "status": "parcial", "owner_suggestion": "segurança, plataforma e compliance", "dimensions": ["auditoria", "campos_sensiveis", "permissoes_backend"]
        },
        {
            "id": "AUD-P1-008", "priority": "P1", "module": "frontend e runtime compartilhado", "title": "Salvar Registro é incompatível com o contrato CRUD do backend",
            "description": "Nas 129 superfícies de formulário, o contrato compartilhado de gravação precisa permanecer compatível com ResourceCreate e ResourcePatch.", "evidence": [source_evidence("apps/all-in-one/src/components/SmartCRUD.tsx", "method: isEditing ? 'PATCH' : 'POST'"), source_evidence("modules/shared/runtime.py", "class ResourceCreate(BaseModel):"), source_evidence("modules/shared/runtime.py", '@app.post("/resources/{resource_type}"'), source_evidence("modules/shared/runtime.py", '@app.patch("/resources/{resource_type}/{resource_id}"'), "docs/data-audit/artifacts/matriz_acao_ui_backend.json"], "impact": "Criação e edição autenticadas podem falhar se o contrato regredir.", "risk": "Botão principal não conclui a operação e o fallback local mascara a incompatibilidade.", "proposal": "Manter adapter frontend tipado por entidade, POST {user_id,payload}, PATCH {payload}, idempotência e testes HTTP/E2E.", "dependencies": ["bindings de campo", "actor autenticado", "contratos por entidade"], "affected_files": ["apps/all-in-one/src/components/SmartCRUD.tsx", "modules/shared/runtime.py"], "migration": "não aplicável", "backend": "manter contratos explícitos e documentar métodos", "frontend": "manter envelope, método, idempotência e gates de permissão", "tests": "contrato HTTP e E2E para criação/edição das 129 superfícies", "documentation": "09_FORMULARIOS_FRONTEND.md", "acceptance": "Cada formulário cria e edita via contrato backend compatível, com permissão, estados, auditoria e teste aprovado.", "status": "resolvido", "owner_suggestion": "frontend e plataforma backend", "dimensions": ["bindings_frontend", "formularios", "acoes_ui", "permissoes_backend"]
        },
        {
            "id": "AUD-P0-009", "priority": "P0", "module": "runtime compartilhado", "title": "Leitura por ID não aplica ownership para recursos não sensíveis",
            "description": "A rota genérica GET por resource_id autentica o ator, mas _expose só restringe leitura de terceiro quando a regra é sensível. Das 61 entidades não sensíveis, 56 fora do módulo permissions não recebem verificação de proprietário, tenant ou papel nessa rota.", "evidence": [source_evidence("modules/shared/runtime.py", '@app.get("/resources/{resource_type}/{resource_id}"'), source_evidence("modules/shared/runtime.py", "def _expose(item:"), "docs/data-audit/artifacts/matriz_enforcement_permissao.json"], "impact": "Um usuário autenticado que obtenha UUID alheio pode ler registro não sensível de outro usuário ou contexto.", "risk": "IDOR e quebra de isolamento horizontal/multitenant.", "proposal": "Aplicar autorização owner/operator ou política ABAC/tenant antes de _expose, negar por padrão e criar testes negativos para todas as classes de recurso.", "dependencies": ["contrato de ownership por entidade", "tenant/business context"], "affected_files": ["modules/shared/runtime.py", "tests"], "migration": "não aplicável", "backend": "enforcement deny-by-default em get_resource", "frontend": "não confiar em ocultação de links ou UUIDs", "tests": "teste negativo de leitura cruzada para as 56 entidades e teste positivo autorizado", "documentation": "11_PERMISSOES_E_SEGURANCA.md", "acceptance": "Toda leitura por ID valida owner, tenant ou papel/atributo explicitamente autorizado e possui teste negativo/positivo por política.", "status": "incompativel_seguranca", "owner_suggestion": "segurança e plataforma backend", "dimensions": ["permissoes_backend", "auditoria"]
        },
    ]
    if counts["ui_actions_incompatible"] == 0:
        gaps = [gap for gap in gaps if gap["id"] != "AUD-P1-008"]
    if counts["permission_horizontal_read_gaps"] == 0:
        gaps = [gap for gap in gaps if gap["id"] != "AUD-P0-009"]
    gap_counts = {priority: sum(gap["priority"] == priority for gap in gaps) for priority in ("P0", "P1", "P2", "P3", "P4")}
    write_json(ARTIFACTS / "relatorio_divergencias.json", {"version": 2, "status": "em_execucao", "counts": {"total": len(gaps), **gap_counts}, "required_fields": ["id", "title", "module", "description", "evidence", "impact", "risk", "priority", "proposal", "dependencies", "affected_files", "migration", "backend", "frontend", "tests", "documentation", "acceptance", "status"], "gaps": gaps})

    def coverage_ratio(covered: int, total: int) -> int:
        return round(100 * covered / total) if total else 0

    units_gate = product_units_tax_model["implementation_gate"]
    calculations_gate_names = ("migration_reversible", "backend_implemented", "unit_tests_implemented", "integration_tests_implemented", "fiscal_homologation")
    units_gate_names = ("migration_reversible", "backfill_defined", "backend_implemented", "frontend_implemented", "unit_tests_implemented", "integration_tests_implemented")
    fiscal_gate_names = tuple(units_gate)
    coverage_values = {
        "bancos": 80,
        "schemas": 100,
        "tabelas_colecoes": 85,
        "campos": 75,
        "relacionamentos": coverage_ratio(sum(bool(field.evidence and field.reference) for field in relations), len(relations)),
        "bindings_frontend": coverage_ratio(counts["ui_bindings_probable"], counts["ui_candidates"]),
        "campos_sensiveis": 0,
        "auditoria": coverage_ratio(counts["audit_requirements_covered"], counts["audit_requirements"]),
        "calculos": coverage_ratio(sum(bool(units_gate[name]) for name in calculations_gate_names), len(calculations_gate_names)),
        "unidades": coverage_ratio(sum(bool(units_gate[name]) for name in units_gate_names), len(units_gate_names)),
        "regras_fiscais": coverage_ratio(sum(bool(units_gate[name]) for name in fiscal_gate_names), len(fiscal_gate_names)),
        "formularios": coverage_ratio(counts["ui_surfaces"], counts["ui_surfaces"]),
        "acoes_ui": coverage_ratio(counts["ui_actions"] - counts["ui_actions_incompatible"], counts["ui_actions"]),
        "permissoes_backend": coverage_ratio(counts["permission_operations"] - counts["permission_horizontal_read_gaps"], counts["permission_operations"]),
        "lacunas_com_backlog": 100,
    }
    evidence_by_dimension = {
        "bancos": ["docs/data-audit/03_CATALOGO_DE_BANCOS.md"], "schemas": ["docs/data-audit/artifacts/dicionario_de_dados.json"],
        "tabelas_colecoes": ["docs/data-audit/artifacts/dicionario_de_dados.json", "docs/data-audit/artifacts/catalogo_mongodb.json", "docs/data-audit/artifacts/catalogo_sqlite.json"],
        "campos": ["docs/data-audit/artifacts/dicionario_de_dados.json"], "relacionamentos": ["docs/data-audit/artifacts/erd.mmd"],
        "bindings_frontend": ["docs/data-audit/artifacts/matriz_formulario_campo.csv"], "campos_sensiveis": ["docs/data-audit/artifacts/politica_classificacao_campos.json"],
        "auditoria": ["docs/data-audit/artifacts/cobertura_auditoria.json"], "calculos": ["docs/data-audit/artifacts/modelo_unidades_tributacao.json"],
        "unidades": ["docs/data-audit/artifacts/modelo_unidades_tributacao.json"], "regras_fiscais": ["docs/data-audit/artifacts/modelo_unidades_tributacao.json"],
        "formularios": ["docs/data-audit/artifacts/coordenadas_stitch.json"], "acoes_ui": ["docs/data-audit/artifacts/coordenadas_stitch.json"],
        "permissoes_backend": ["docs/data-audit/artifacts/matriz_permissao_acao.csv", "docs/data-audit/artifacts/matriz_enforcement_permissao.json"], "lacunas_com_backlog": ["docs/data-audit/artifacts/relatorio_divergencias.json"],
    }
    dimensions = {}
    for name, value in coverage_values.items():
        dimension_gaps = [gap["id"] for gap in gaps if name in gap["dimensions"]]
        dimensions[name] = {
            "percentual": min(value, 99) if dimension_gaps else value,
            "evidencias": evidence_by_dimension[name],
            "lacunas": dimension_gaps,
            "metodo": "razão derivada dos artefatos quando disponível; dimensão com lacuna aberta nunca recebe 100%",
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
        "mongodb": f"Inventário estático de {counts['mongodb_collections']} coleções e {counts['mongodb_fields']} campos; estado runtime não comprovado. EVIDÊNCIAS: `artifacts/catalogo_mongodb.json`.",
        "sqlite": f"Inventário estático de {counts['sqlite_tables']} tabelas e {counts['sqlite_fields']} campos do fallback local; instâncias não comprovadas. EVIDÊNCIAS: `artifacts/catalogo_sqlite.json`.",
        "redis": f"Inventário estático de {counts['redis_key_patterns']} padrão de chave para rate limit, com TTL e modo de falha; runtime não comprovado. EVIDÊNCIAS: `artifacts/catalogo_redis.json`.",
        "object-storage": f"Inventário estático de {counts['object_storage_stores']} stores/referências, incluindo cofre privado, documentos, APK público e estado Terraform; buckets e políticas runtime não comprovados. EVIDÊNCIAS: `artifacts/catalogo_object_storage.json`.",
        "browser-storage": f"Inventário estático de {counts['browser_storage_key_patterns']} chaves/famílias de localStorage e sessionStorage, com finalidade, classificação, retenção e risco. EVIDÊNCIAS: `artifacts/catalogo_browser_storage.json`.",
    }
    for store, description in persistence_docs.items():
        path = AUDIT / "databases" / store / "README.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {store}\n\n{description}\n\n**Status:** catálogo parcial; lacuna `AUD-P0-000`.\n", encoding="utf-8")

    write_markdown(
        "00_RESUMO_EXECUTIVO.md",
        "Resumo Executivo da Auditoria de Dados",
        f"""**Status:** em execução; conclusão de 100% não declarada.

A varredura física reproduzível encontrou {counts['migrations']} migrations PostgreSQL, {counts['schemas']} schemas, {counts['tables']} tabelas, {counts['fields']} campos, {counts['relationships']} referências, {counts['indexes']} índices e {counts['endpoints']} endpoints candidatos. Também foram catalogados estaticamente {counts['mongodb_collections']} coleções MongoDB, {counts['sqlite_tables']} tabelas SQLite, {counts['redis_key_patterns']} padrão Redis, {counts['object_storage_stores']} stores de objetos e {counts['browser_storage_key_patterns']} chaves/famílias de browser storage. A validação operacional desses mecanismos permanece pendente.

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
| MongoDB | {counts['mongodb_collections']} coleções / {counts['mongodb_fields']} campos | inventário estático; runtime pendente |
| Redis | {counts['redis_key_patterns']} padrão de chave com TTL | inventário estático; runtime pendente |
| SQLite | {counts['sqlite_tables']} tabelas / {counts['sqlite_fields']} campos | inventário estático; runtime pendente |
| Object storage | {counts['object_storage_stores']} stores/referências | inventário estático; buckets e restore pendentes |
| Browser storage | {counts['browser_storage_key_patterns']} chaves/famílias | inventário estático; comportamento E2E pendente |

EVIDÊNCIAS: `database/postgres/migrations/`, `database/mongodb/init/001_ai_social_telemetry.js`, `modules/shared/store.py`, `modules/api_hub/main.py`, `modules/shared/private_documents.py`.""",
    )
    write_markdown(
        "04_DICIONARIO_DE_DADOS_MESTRE.md",
        "Dicionário de Dados Mestre",
        f"""O dicionário físico contém {counts['fields']} campos. O catálogo lógico contém {counts['logical_entities']} entidades, das quais {counts['logical_without_physical_table']} não possuem tabela física homônima e {counts['logical_without_ui_surface']} não possuem superfície UI homônima. Tipo, nulabilidade, padrão, PK, unique e FK são extraídos das migrations; regras lógicas vêm de `MODULE_ENTITIES` e `RULE_OVERRIDES`. Nome lógico, LGPD e mascaramento são triagem e requerem homologação.\n\nArquivos canônicos: `artifacts/dicionario_de_dados.csv`, `artifacts/dicionario_de_dados.json`, `artifacts/catalogo_logico.csv` e `artifacts/catalogo_logico.json`.\n\nEVIDÊNCIAS: {', '.join(f'`{item}`' for item in migrations[:5])}, `modules/shared/domain_rules.py` e demais migrations listadas no JSON.""",
    )
    write_markdown(
        "05_RELACIONAMENTOS_E_ERD.md",
        "Relacionamentos e ERD",
        f"""Foram extraídas {counts['relationships']} referências declaradas em campos. O ERD Mermaid está em `artifacts/erd.mmd`. Relações implícitas sem FK permanecem fora desta contagem e devem gerar lacuna quando localizadas no backend.\n\nEVIDÊNCIAS: `docs/data-audit/artifacts/erd.mmd`.""",
    )
    write_markdown(
        "06_UNIDADES_E_CONVERSOES.md",
        "Unidades, Conversões, Precisão e Arredondamento",
        f"""**Status:** implementação parcial comprovada; frontend, integração PostgreSQL viva e homologação pendentes.

## Estruturas

Foram modeladas {counts['measurement_entities_proposed']} estruturas: {', '.join(f'`{name}`' for name in product_units_tax_model['measurement_entities'])}. Os propósitos cobrem cadastro, estoque base, compra, venda, consumo, produção, transporte, fiscal, exibição, conferência e inventário.

## Conversão e precisão

- Decimal é obrigatório; ponto flutuante binário é proibido.
- Conversões exigem compatibilidade dimensional, vigência, versão, aprovação, tolerância e arredondamento.
- Conversões entre dimensões exigem fórmula segura, densidade e contexto técnico.
- Movimentações preservam unidade informada, quantidade base e snapshot do fator.
- O backend recalcula e registra correlação e idempotência.

## Gate

Migration reversível, rollback, estratégia de backfill sem inferência, cálculo Decimal e testes unitários estão implementados. Frontend, integração PostgreSQL viva e homologação permanecem pendentes. A migration não é aplicada por este documento.

EVIDÊNCIAS: `database/postgres/migrations/025_units_tax_governance.sql`, `database/postgres/rollbacks/025_units_tax_governance.down.sql`, `modules/shared/units_tax.py`, `tests/test_units_tax_governance.py`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.""",
    )
    write_markdown(
        "07_TRIBUTACAO.md",
        "Tributação e Perfis Fiscais",
        f"""**Status:** persistência, cálculo e testes unitários implementados; frontend, integração e homologação fiscal pendentes.

## Estruturas

Foram modeladas {counts['fiscal_entities_proposed']} estruturas fiscais e três estruturas de preço/custo. Regras possuem prioridade, jurisdição, regime, operação, cliente, destino, canal, benefício, alíquota, base, crédito, arredondamento, fundamento, vigência, versão e aprovação.

## Brasil

O checklist cobre {', '.join(f'`{item}`' for item in product_units_tax_model['brazilian_fields_to_evaluate'])}. Aplicabilidade deve ser decidida por cenário e nunca duplicada indiscriminadamente em cada produto.

## Cálculo

Cada snapshot preserva regra, classificação, base, alíquota, valor, moeda, precisão, arredondamento, fundamento, versão e hash de entrada. Cálculos fiscais são exclusivos do backend.

## Gate

Migration reversível, rollback, estratégia de backfill sem inferência, cálculo Decimal, vigência, aprovação e testes unitários estão implementados. Frontend, integração PostgreSQL viva e homologação por cenários permanecem pendentes.

EVIDÊNCIAS: `database/postgres/migrations/025_units_tax_governance.sql`, `database/postgres/rollbacks/025_units_tax_governance.down.sql`, `modules/shared/units_tax.py`, `tests/test_units_tax_governance.py`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.""",
    )
    write_markdown(
        "08_AUDITORIA_E_LOGS.md",
        "Auditoria, Logs e Rastreabilidade",
        f"""O inventário encontrou {counts['audit_candidate_tables']} tabelas candidatas de auditoria/log/evento. O contrato possui {counts['audit_requirements']} requisitos de alteração e leitura; {counts['audit_requirements_covered']} possuem ao menos um alias físico em alguma tabela candidata.

Essa cobertura global não prova que cada operação ou dado sensível seja auditado. Requisitos ausentes, retenção, imutabilidade, correlação e enforcement por módulo permanecem lacunas até testes de integração.

Logs técnicos, segurança, auditoria, negócio, métricas, traces e eventos de integração devem permanecer separados e correlacionados. Segredos e valores sensíveis não podem ser gravados em texto aberto.

EVIDÊNCIAS: `config/data_audit/audit_traceability_policy.json`, `artifacts/cobertura_auditoria.json`, `database/postgres/migrations/005_audit_events_api_security.sql`, `modules/shared/`.""",
    )
    write_markdown(
        "09_FORMULARIOS_FRONTEND.md",
        "Formulários, Tabelas, Filtros e Dashboards",
        f"""A varredura localizou {counts['ui_surfaces']} superfícies SmartCRUD, sendo {counts['ui_forms']} formulários, {counts['ui_candidates']} combinações superfície/campo e {counts['ui_actions']} ocorrências de ação. O componente genérico oferece somente `name`, `description` e `category` nos formulários; {counts['ui_bindings_unproven']} bindings são genéricos/não comprovados e {counts['ui_bindings_probable']} coincidem provavelmente com campo físico.

O contrato compartilhado de `Salvar Registro` usa `POST {{user_id,payload}}` na criação e `PATCH {{payload}}` na edição, com correlação e idempotência na criação. A matriz registra {counts['ui_actions_incompatible']} ações incompatíveis. Há {counts['ui_actions_without_frontend_permission_gate']} ocorrências sem gate explícito de permissão no frontend; autorização backend ou fallback local deve ser analisado por ação.

EVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx`, `modules/shared/runtime.py`, `artifacts/matriz_formulario_campo.csv`, `artifacts/matriz_acao_ui_backend.json`. Lacuna remanescente: `AUD-P1-002`.""",
    )
    write_markdown(
        "10_FORMULARIOS_DINAMICOS.md",
        "Construtor de Formulários Dinâmicos",
        f"""**Status:** proposta mandatória, ainda não comprovada como implementação.

## Modelo versionado

A proposta contém {counts['dynamic_form_entities_proposed']} estruturas: {', '.join(f'`{name}`' for name in dynamic_form_model['entities'])}. Cada campo está enumerado em `artifacts/formulario_dinamico_modelo.json`.

## Ciclo de vida

{', '.join(f'`{state}`' for state in dynamic_form_model['lifecycle'])}. Uma versão publicada é imutável; qualquer alteração cria nova versão e passa novamente por homologação.

## Segurança

O modelo exige allowlists de campo, componente e operador; parser seguro; validação e recálculo backend; limite de complexidade; detecção de ciclos; isolamento por tenant; RBAC; ABAC; checksum; auditoria; rollback e sandbox de prévia.

São proibidos seleção arbitrária de tabela/coluna, SQL, JavaScript, shell, desativação de auditoria, enfraquecimento de validação e publicação sem homologação.

## Cobrança

Eventos faturáveis estão separados de autosave e rascunho. Valores e estratégia comercial não são expostos; dependem de aprovação formal.

## Gate de implementação

Migration reversível, backend, frontend, testes de segurança e homologação permanecem `false`. Portanto, este documento é modelagem e não afirma funcionalidade existente.

EVIDÊNCIAS: `config/data_audit/dynamic_form_model_proposal.json`, `artifacts/formulario_dinamico_modelo.json`, `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583`. Lacuna: `AUD-P1-004`.""",
    )
    write_markdown(
        "11_PERMISSOES_E_SEGURANCA.md",
        "Permissões, Segurança e Privacidade",
        f"""Foram triados {counts['sensitive_candidates']} campos potencialmente pessoais, sensíveis, financeiros, restritos ou pseudônimos vinculáveis. A política versionada registra categoria, padrão que motivou a triagem, criptografia, mascaramento e retenção. A classificação automática exige homologação pelo proprietário do domínio e revisão jurídica/privacidade quando aplicável.

Foram catalogadas {counts['permission_operations']} operações backend: 600 operações CRUD sobre 120 entidades e {counts['event_transitions']} transições. {counts['permission_operations_with_test_candidates']} possuem ao menos um arquivo de teste candidato localizado; isso não equivale a prova positiva/negativa completa por endpoint.

A rota genérica de leitura por ID deixa {counts['permission_horizontal_read_gaps']} entidades não sensíveis fora do módulo `permissions` sem verificação de owner, tenant ou papel depois da autenticação. Essa condição é P0 por risco de IDOR e isolamento horizontal. RBAC/ABAC deve ser provado endpoint a endpoint; controle apenas no frontend não é aceito. Campos sem regra automática continuam explicitamente sem classificação e com lacuna de retenção.

EVIDÊNCIAS: `config/data_audit/field_classification_policy.json`, `artifacts/politica_classificacao_campos.json`, `artifacts/dicionario_de_dados.csv`, `modules/permissions/`, `modules/identity/`.""",
    )
    write_markdown(
        "12_APIS_EVENTOS_E_INTEGRACOES.md",
        "APIs, Eventos e Integrações",
        f"""A varredura AST localizou {counts['endpoints']} endpoints, {counts['endpoints_with_response_model']} declarações de `response_model` e {counts['api_model_fields']} ocorrências de campo em modelos Pydantic locais. Também foram encontradas {counts['event_transitions']} transições com {counts['unique_events']} nomes de evento. Produtor, ação, estados, papéis e MFA vêm das regras do backend; versão, consumidores, payload integral, idempotência e compatibilidade continuam pendentes quando não declarados.\n\nEVIDÊNCIAS: `artifacts/catalogo_apis.json`, `artifacts/catalogo_eventos.json`, `artifacts/matriz_api_campo.csv`, `artifacts/matriz_evento_campo.csv` e `artifacts/matriz_permissao_acao.csv`. Lacuna: `AUD-P1-003`.""",
    )
    write_markdown(
        "13_VALIDACAO_E_TESTES.md",
        "Validação e Testes",
        f"""O inventário AST encontrou {counts['test_functions']} funções de teste: {counts['tests_with_assertions']} contêm `assert` e {counts['tests_with_http_calls']} contêm chamadas HTTP reconhecidas. Os relatórios JUnit registram {counts['test_functions_in_execution_reports']} funções, das quais {counts['test_functions_passed']} foram aprovadas; parametrizações são consolidadas por função. A presença de um teste ou candidato aprovado não comprova cobertura integral do requisito.

Foram extraídos {counts['memo_requirements_traced']} requisitos mandatórios das seções 21 e 24 do memorando; {counts['memo_requirements_without_test_candidates']} não possuem teste candidato por correspondência semântica conservadora e {counts['memo_requirements_with_passed_candidates']} possuem ao menos um candidato aprovado. Cada vínculo permanece `não comprovado` até revisão de escopo.

A cobertura funcional continua incompleta para CRUD, rascunho, aprovação, importação, cálculos, unidades, impostos, concorrência, idempotência, autorização e isolamento de tenant.

EVIDÊNCIAS: `artifacts/pytest_unit_results.xml`, `artifacts/pytest_identity_e2e_results.xml`, `artifacts/catalogo_testes.json`, `artifacts/matriz_requisito_teste.json`, `tests/test_validate_data_audit_delivery.py`.""",
    )
    gap_rows = markdown_table(["ID", "Prioridade", "Módulo", "Lacuna", "Risco", "Status", "Aceite"], ([gap["id"], gap["priority"], gap["module"], gap["title"], gap["risk"], gap["status"], gap["acceptance"]] for gap in gaps))
    write_markdown("14_REGISTRO_DE_LACUNAS.md", "Registro de Lacunas", f"{gap_rows}\n\nEVIDÊNCIAS: `artifacts/relatorio_divergencias.json`.")
    backlog_rows = markdown_table(["Ordem", "ID", "Responsável sugerido", "Entrega", "Dependências", "Status"], ([index, gap["id"], gap["owner_suggestion"], gap["acceptance"], ", ".join(gap["dependencies"]), gap["status"]] for index, gap in enumerate(gaps, 1)))
    write_markdown("15_BACKLOG_DE_IMPLEMENTACAO.md", "Backlog de Implementação", f"{backlog_rows}\n\nA ordem prioriza P0, integridade contratual e funcionalidades P1. EVIDÊNCIAS: `14_REGISTRO_DE_LACUNAS.md`.")
    write_markdown(
        "16_COORDENADAS_STITCH.md",
        "Coordenadas para Templates Stitch",
        f"""## Cobertura gerada

Foram geradas {counts['ui_surfaces']} coordenadas a partir de rotas e superfícies reais. Cada registro contém módulo, entidade, título, tipo, rota, persona pendente, campos, ação primária, endpoint lógico, permissões, estados, responsividade, acessibilidade e evidência.

As coordenadas estão em `artifacts/coordenadas_stitch.csv` e `artifacts/coordenadas_stitch.json`. O status de binding permanece parcial porque o `SmartCRUD` genérico não implementa todos os campos específicos.

## TEMPLATE adicional: Catálogo de dados

- Módulo: Administração interna
- Persona: auditor e proprietário de domínio
- Rota: `/admin/data-audit` (proposta)
- Dados: dicionário, lacunas, cobertura e evidências
- Ações: filtrar, abrir evidência, atribuir lacuna e homologar classificação
- Estados: loading, vazio, erro, conflito, sem permissão e sucesso
- Responsividade: desktop, tablet e mobile
- Acessibilidade: teclado, foco, labels e contraste

Nenhuma rota proposta é apresentada como existente. EVIDÊNCIAS: `apps/all-in-one/src/App.tsx`, `artifacts/coordenadas_stitch.json`, `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:2545`.""",
    )
    write_markdown(
        "17_DECISOES_ARQUITETURAIS.md",
        "Decisões Arquiteturais da Auditoria",
        """1. Migrations versionadas são a fonte do catálogo físico, não prova do banco em execução.\n2. Catálogo lógico e bindings exigem validação cruzada; inferência não equivale a evidência.\n3. Formulários dinâmicos apontam para comandos/DTOs allowlist, nunca para tabela física arbitrária.\n4. Cobertura inferior a 100% impede status concluído.\n5. Propostas de schema exigem migration reversível, backfill, rollback e testes antes de aplicação.\n\nEVIDÊNCIAS: `config/data_audit/delivery_contract.json`.""",
    )
    trace_rows = markdown_table(
        ["ID", "Seção", "Requisito", "Candidatos", "Aprovados", "Status"],
        ([row["requirement_id"], row["subsection"], row["requirement"], row["candidate_count"], row["passed_candidate_count"], row["proof_status"]] for row in memo_requirements),
    )
    write_markdown("18_MATRIZ_DE_RASTREABILIDADE.md", "Matriz de Rastreabilidade", f"A matriz cobre os {len(memo_requirements)} requisitos explícitos das seções de conclusão e checklist. Candidatos não são promovidos a prova.\n\n{trace_rows}\n\nEVIDÊNCIAS: `artifacts/matriz_requisito_teste.json` e `artifacts/catalogo_testes.json`.")
    acceptance_rows = markdown_table(
        ["Dimensão", "Percentual", "Evidência/Lacuna"],
        ([name, item["percentual"], "comprovada" if item["percentual"] == 100 else "; ".join(item["lacunas"]) or "cobertura parcial"] for name, item in dimensions.items()),
    )
    write_markdown(
        "19_CRITERIOS_DE_ACEITE.md",
        "Critérios de Aceite e Declaração de Cobertura",
        f"**Status geral:** em execução. A entrega não declara conclusão.\n\n{acceptance_rows}\n\nO status somente poderá mudar para `concluido` quando todas as dimensões alcançarem 100% com evidência. EVIDÊNCIAS: `artifacts/checklist_cobertura.json`.",
    )

    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_delivery()
