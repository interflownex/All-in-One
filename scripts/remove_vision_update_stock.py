#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TODAY = date(2026, 7, 25)
REMOVED_MODULE = "vision"

REMOVED_DIRS = [
    "modules/vision",
    "apps/all-in-one/src/pages/vision",
    "apps/all-in-one-business/src/pages/vision",
]

REMOVED_FILES = [
    "contracts/vision.md",
    "modules/shared/vision_postgres_store.py",
    "infra/kubernetes/base/vision.yaml",
    "tests/test_vision_event_catalog.py",
]

CURRENT_DOCS = [
    "README.md",
    "STATUS.md",
    "docs/EXECUTION_PLAN.md",
    "docs/INTEGRATION.md",
    "docs/VALLEY_CATALOG.md",
    "docs/REQUIREMENTS_TRACEABILITY.md",
    "docs/COMPLIANCE.md",
    "docs/Pendências Do desenvolvedor.md",
    "docs/Pendencias Do desenvolvedor.md",
]

COUNT_REPLACEMENTS = {
    "25 módulos": "24 módulos",
    "25 modulos": "24 modulos",
    "25 microserviços": "24 microserviços",
    "25 microservicos": "24 microservicos",
    "25 dashboards": "24 dashboards",
    "25 projetos": "24 projetos",
    "25 cards": "24 cards",
    "181 telas": "171 telas",
    "180/181": "170/171",
    "335 rotas": "325 rotas",
}

STOCK_NAME_REPLACEMENTS = {
    "STOCK Dropship Light": "STOCK",
    "Stock Dropship Light": "STOCK",
    "STOCK Dropship": "STOCK",
    "Stock Dropship": "STOCK",
    "Stock Light": "STOCK",
}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def remove_path(relative: str) -> None:
    path = ROOT / relative
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def prune_vision(value: Any) -> Any:
    marker = object()

    def visit(node: Any) -> Any:
        if isinstance(node, dict):
            identities = {
                str(node.get(key, "")).strip().lower()
                for key in ("slug", "module", "domain", "service", "name", "id")
            }
            if REMOVED_MODULE in identities:
                return marker
            result: dict[str, Any] = {}
            for key, item in node.items():
                key_lower = str(key).lower()
                if key_lower == REMOVED_MODULE or key_lower.startswith("vision."):
                    continue
                cleaned = visit(item)
                if cleaned is not marker:
                    result[key] = cleaned
            for count_key in ("module_count", "modules_count", "total_modules"):
                if isinstance(result.get(count_key), int):
                    result[count_key] = 24
            return result
        if isinstance(node, list):
            result = []
            for item in node:
                cleaned = visit(item)
                if cleaned is not marker:
                    result.append(cleaned)
            return result
        if isinstance(node, str):
            normalized = node.strip().lower()
            if normalized == REMOVED_MODULE or normalized.startswith("vision.") or normalized.startswith("/vision"):
                return marker
        return node

    cleaned = visit(value)
    return None if cleaned is marker else cleaned


def update_catalog() -> None:
    path = ROOT / "config/module_catalog.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    modules = [module for module in catalog.get("modules", []) if module.get("slug") != REMOVED_MODULE]
    for module in modules:
        if module.get("slug") == "stock":
            module["title"] = "STOCK"
            module["description"] = (
                "Catálogo curado de fornecedores homologados, sem estoque físico próprio, "
                "com pedido sob demanda, regras de preço, tracking e descontos por Pepitas. "
                "Entra na primeira etapa com AliExpress e CJ Dropshipping como fontes iniciais, "
                "sob operação controlada e expansão condicionada à qualidade."
            )
            module["monetization"] = (
                "Comissão ou margem negociada, destaque, taxa de operação e planos para lojistas; "
                "a expansão depende de prazo, devoluções, suporte e margem auditada."
            )
            module["roadmap_wave"] = 1
            module["initial_suppliers"] = ["AliExpress", "CJ Dropshipping"]
            module["operating_model"] = "pedido sob demanda sem estoque físico próprio"
    catalog["version"] = "0.2.0"
    catalog["module_count"] = len(modules)
    catalog["modules"] = modules
    write_text(path, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")


def update_json(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return
    cleaned = prune_vision(data)
    write_text(path, json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n")


def remove_lazy_vision_declarations(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if re.match(r"^const\s+Vision\w*\s*=", line):
            while index < len(lines):
                current = lines[index]
                index += 1
                if ";" in current:
                    break
            continue
        if re.match(r"^import\s+.*(?:/vision/|pages/vision)", line):
            index += 1
            continue
        output.append(line)
        index += 1
    return "".join(output)


def remove_vision_route_blocks(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    while index < len(lines):
        if "<Route" not in lines[index]:
            output.append(lines[index])
            index += 1
            continue

        block: list[str] = [lines[index]]
        index += 1
        if not block[0].strip().endswith("/>"):
            while index < len(lines):
                block.append(lines[index])
                closing = lines[index].strip()
                index += 1
                if closing == "/>" or closing.endswith("} />"):
                    break
        joined = "".join(block)
        if re.search(r'path=["\']/vision(?:/|["\'])', joined) or re.search(r"\bVision\w*", joined):
            continue
        output.extend(block)
    return "".join(output)


def update_app_router(relative: str) -> None:
    path = ROOT / relative
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = remove_lazy_vision_declarations(text)
    text = remove_vision_route_blocks(text)
    write_text(path, text)


def update_home() -> None:
    path = ROOT / "apps/all-in-one/src/pages/Home.tsx"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'^\s*\["vision",.*\n', "", text, flags=re.MULTILINE)
    text = text.replace(
        '["stock", "Estoque", "▤", "Produtos, saldos, reservas e rastreabilidade."],',
        '["stock", "STOCK", "▤", "Catálogo curado, fornecedores homologados, pedido sob demanda e tracking."],',
    )
    text = text.replace("<strong>25</strong>", "<strong>24</strong>")
    text = text.replace("<strong>181</strong>", "<strong>171</strong>")
    text = text.replace("25 capacidades que trabalham como uma so.", "24 capacidades que trabalham como uma só.")
    write_text(path, text)


def remove_single_line_active_references(path: Path) -> None:
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    cleaned: list[str] = []
    for line in lines:
        lower = line.lower()
        if "vision" not in lower:
            cleaned.append(line)
            continue
        stripped = line.strip()
        removable = any(
            marker in stripped
            for marker in ('"vision"', "'vision'", "vision.yaml", "modules/vision", "/vision/", "vision.")
        )
        if removable and not stripped.startswith(("#", "//", "/*", "*")):
            continue
        cleaned.append(line)
    write_text(path, "".join(cleaned))


def remove_yaml_service_block(path: Path, key: str) -> None:
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    output: list[str] = []
    index = 0
    pattern = re.compile(rf"^(\s*){re.escape(key)}:\s*(?:#.*)?$")
    while index < len(lines):
        match = pattern.match(lines[index].rstrip("\n"))
        if not match:
            output.append(lines[index])
            index += 1
            continue
        indent = len(match.group(1))
        index += 1
        while index < len(lines):
            raw = lines[index]
            stripped = raw.strip()
            current_indent = len(raw) - len(raw.lstrip(" "))
            if stripped and current_indent <= indent and not stripped.startswith("#"):
                break
            index += 1
    write_text(path, "".join(output))


def remove_markdown_vision_section(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    while index < len(lines):
        heading = re.match(r"^(#{1,6})\s+(?:\d+[.)]\s*)?Vision\b", lines[index], flags=re.IGNORECASE)
        if heading:
            level = len(heading.group(1))
            index += 1
            while index < len(lines):
                next_heading = re.match(r"^(#{1,6})\s+", lines[index])
                if next_heading and len(next_heading.group(1)) <= level:
                    break
                index += 1
            continue
        line_lower = lines[index].lower()
        if "| vision |" in line_lower or re.match(r"^\s*[-*]\s+vision\b", lines[index], re.IGNORECASE):
            index += 1
            continue
        output.append(lines[index])
        index += 1
    return "".join(output)


def update_current_document(path: Path) -> None:
    if not path.exists():
        return
    text = remove_markdown_vision_section(path.read_text(encoding="utf-8"))
    for old, new in COUNT_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in STOCK_NAME_REPLACEMENTS.items():
        text = text.replace(old, new)
    write_text(path, text)


def rename_25_module_documents() -> None:
    candidates = sorted(ROOT.rglob("*25_Modulos*"), key=lambda item: len(item.parts), reverse=True)
    for path in candidates:
        if ".git" in path.parts or not path.is_file():
            continue
        target = path.with_name(path.name.replace("25_Modulos", "24_Modulos"))
        if not target.exists():
            path.rename(target)


def create_database_removal_migration() -> None:
    migrations = ROOT / "database/postgres/migrations"
    if not migrations.exists():
        return
    numbers: list[int] = []
    for path in migrations.glob("[0-9][0-9][0-9]_*.sql"):
        try:
            numbers.append(int(path.name.split("_", 1)[0]))
        except ValueError:
            continue
    target = migrations / f"{max(numbers, default=0) + 1:03d}_remove_vision_module.sql"
    if target.exists():
        return
    sql = "\n".join(
        [
            "-- Remoção definitiva do módulo Vision do escopo ativo do All-in-One.",
            "-- Antes de aplicar em produção, confirme que qualquer dado necessário foi exportado.",
            "BEGIN;",
            "DROP SCHEMA IF EXISTS vision CASCADE;",
            "COMMIT;",
            "",
        ]
    )
    write_text(target, sql)


def create_authoritative_document() -> None:
    path = ROOT / "docs/DECISAO_24_MODULOS_STOCK_PRIMEIRA_ETAPA_2026-07-25.md"
    content = "\n".join(
        [
            "# Decisão oficial: 24 módulos e STOCK na primeira etapa",
            "",
            "**Projeto:** All-in-One + Valley  ",
            "**Data:** 25/07/2026  ",
            "**Classificação:** Conceito, comercial e técnico  ",
            "**Público:** gestão, investidores, comercial, desenvolvimento e equipe técnica",
            "",
            "## 1. Remoção do Vision",
            "",
            "O módulo **Vision — Câmeras, Monitoramento e Ocorrências** foi removido do escopo ativo.",
            "A plataforma passa de **25 para 24 módulos**. O site passa de **181 para 171 telas previstas** e de **335 para 325 rotas auditáveis estimadas**, considerando a retirada das dez superfícies do Vision.",
            "",
            "Referências em auditorias históricas permanecem somente como evidência do estado anterior. Elas não representam oferta, roadmap, orçamento ou funcionalidade vigente.",
            "",
            "## 2. Posição oficial do STOCK",
            "",
            "O nome oficial é exclusivamente **STOCK**. O módulo entra na **Onda 1**, junto com Marketplace e Finance.",
            "A operação inicial será controlada, sem estoque físico próprio, com catálogo curado, pedido sob demanda e acompanhamento humano.",
            "",
            "### Fontes iniciais",
            "",
            "1. AliExpress;",
            "2. CJ Dropshipping.",
            "",
            "### Dependências mínimas",
            "",
            "1. Identity;",
            "2. Business;",
            "3. API Hub;",
            "4. Marketplace;",
            "5. Finance.",
            "",
            "### Reservas de planejamento",
            "",
            "- custo único: R$ 28 mil a R$ 125 mil;",
            "- custo mensal: R$ 22 mil a R$ 80 mil;",
            "- capital de giro: R$ 20 mil a R$ 100 mil.",
            "",
            "Os valores são reservas internas de planejamento, não promessa de lucro nem proposta comercial.",
            "",
            "## 3. Nova distribuição das ondas",
            "",
            "- **Onda 1:** Identity, Business, API Hub, Marketplace, Finance, STOCK, Jobs, Permissions e AI Core.",
            "- **Onda 2:** Delivery, Services, Riders, Mobility e CRM.",
            "- **Onda 3:** BI, ERP, Document e BPM.",
            "- **Onda 4:** Health, HR, TMS, WMS, Property e Legal.",
            "",
            "Não existe mais Onda 5 vinculada ao Vision.",
            "",
        ]
    )
    write_text(path, content)


def create_execution_report() -> None:
    active_refs: list[str] = []
    ignored_prefixes = ("docs/data-audit/", "docs/relatorios/")
    suffixes = {".py", ".ts", ".tsx", ".js", ".json", ".yaml", ".yml", ".md"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "scripts/remove_vision_update_stock.py" or relative.startswith(ignored_prefixes):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(r"\bvision\b", text, re.IGNORECASE):
            active_refs.append(relative)

    report = ROOT / "docs/relatorios/remocao-vision/RELATORIO_REMOCAO_VISION_STOCK_2026-07-25.md"
    status = "sem referências ativas encontradas" if not active_refs else "referências residuais exigem revisão"
    lines = [
        "# Relatório de remoção do Vision e atualização do STOCK",
        "",
        f"**Data:** {TODAY.strftime('%d/%m/%Y')}",
        "**Branch:** codex/remover-vision-atualizar-stock-2026-07-25",
        "**Novo total:** 24 módulos",
        "**Telas previstas:** 171",
        "**Rotas estimadas:** 325",
        f"**Varredura:** {status}",
        "",
        "## Alterações executadas",
        "",
        "1. remoção do Vision do catálogo oficial;",
        "2. remoção das páginas, backend, contrato, store, teste e manifesto Kubernetes específicos;",
        "3. retirada das rotas do Vision nos aplicativos web;",
        "4. atualização da Home para 24 módulos e 171 telas;",
        "5. reposicionamento do STOCK na primeira etapa;",
        "6. criação de migração PostgreSQL para remoção do schema Vision;",
        "7. atualização da documentação vigente e preservação das auditorias históricas como evidência.",
        "",
        "## Referências residuais fora do histórico",
        "",
    ]
    lines.extend([f"- `{item}`" for item in active_refs] or ["- Nenhuma."])
    write_text(report, "\n".join(lines) + "\n")


def main() -> None:
    for relative in REMOVED_DIRS + REMOVED_FILES:
        remove_path(relative)

    update_catalog()

    for relative in (
        "config/events/domain_event_fixtures.json",
        "config/stitch/screen_manifest.json",
        "config/stitch/sync_state.json",
        "apps/all-in-one/src/config/entityFieldBindings.generated.json",
    ):
        path = ROOT / relative
        if path.exists():
            update_json(path)

    update_app_router("apps/all-in-one/src/App.tsx")
    update_app_router("apps/all-in-one-business/src/App.tsx")
    update_home()

    for relative in (
        "infra/kubernetes/base/kustomization.yaml",
        "scripts/generate_full_cloudbuild.py",
        "scripts/scaffold_modules.py",
        "scripts/stitch_orchestrator.py",
        "scripts/validate_repository.py",
        "scripts/validate_web_frontend.py",
        "modules/shared/runtime.py",
        "modules/shared/retention_worker.py",
        "modules/shared/domain_rules.py",
        "apps/all-in-one-business/src/modules/moduleRecommendationRules.ts",
        "apps/valley/src/App.tsx",
        "apps/valley/src/lib/valleyPlatform.ts",
    ):
        remove_single_line_active_references(ROOT / relative)

    remove_yaml_service_block(ROOT / "infra/docker/docker-compose.yml", "vision")

    for relative in CURRENT_DOCS:
        update_current_document(ROOT / relative)

    rename_25_module_documents()
    create_database_removal_migration()
    create_authoritative_document()
    create_execution_report()

    print("Remoção do Vision e atualização do STOCK aplicadas ao checkout.")


if __name__ == "__main__":
    main()
