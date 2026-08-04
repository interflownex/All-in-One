#!/usr/bin/env python3
"""Generate and verify the Phase 0 static data inventory.

This scanner intentionally reports repository evidence only. It does not claim
that a database, bucket, queue, or external service is configured or compliant.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "config" / "compliance" / "fase0_baseline.json"
POLICY_PATH = ROOT / "config" / "autonomy" / "regulatory_data_execution_policy.json"
INVENTORY_PATH = ROOT / "docs" / "governance" / "generated" / "fase0_inventory.json"
REPORT_PATH = ROOT / "docs" / "governance" / "generated" / "F0_INVENTORY_BASELINE.md"
MIGRATIONS_DIR = ROOT / "database" / "postgres" / "migrations"

TEXT_SUFFIXES = {
    ".cfg", ".conf", ".env.example", ".html", ".ini", ".java", ".js", ".json",
    ".jsx", ".kt", ".kts", ".md", ".mjs", ".py", ".sql", ".toml", ".ts",
    ".tsx", ".txt", ".yaml", ".yml",
}
EXCLUDED_PARTS = {
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "build",
    "coverage", "dist", "node_modules", "target",
}
MAX_TEXT_BYTES = 2_000_000
IDENT = r'(?:"[^"]+"|[A-Za-z_][A-Za-z0-9_$]*)'
QUALIFIED_IDENT = rf'{IDENT}(?:\s*\.\s*{IDENT})?'
CREATE_TABLE_RE = re.compile(
    rf"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>{QUALIFIED_IDENT})\s*\(",
    re.IGNORECASE,
)
CREATE_SCHEMA_RE = re.compile(
    rf"\bCREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>{IDENT})",
    re.IGNORECASE,
)
ALTER_TABLE_RE = re.compile(
    rf"\bALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?(?P<name>{QUALIFIED_IDENT})(?P<body>.*)",
    re.IGNORECASE | re.DOTALL,
)
ADD_COLUMN_RE = re.compile(
    rf"^\s*ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>{IDENT})\b",
    re.IGNORECASE,
)
INDEX_RE = re.compile(
    rf"\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>{IDENT})",
    re.IGNORECASE,
)
REFERENCE_RE = re.compile(r"\bREFERENCES\s+" + QUALIFIED_IDENT, re.IGNORECASE)

MARKERS: dict[str, tuple[str, ...]] = {
    "mongodb": ("mongodb://", "mongodb+srv://", "pymongo", "motor.motor_asyncio", "mongoclient"),
    "redis": ("redis://", "rediss://", "import redis", "from redis", "redis.asyncio"),
    "sqlite": ("sqlite://", "sqlite3", ".sqlite", ".db"),
    "object_storage": ("google.cloud.storage", "boto3", "s3://", "gs://", "firebase_storage", "cloud storage"),
    "browser_storage": ("localstorage", "sessionstorage", "indexeddb"),
    "queues": ("rabbitmq", "pika", "kafka", "routing_key", "outbox"),
    "events": ("event_type", "domain_event", "causation_id", "correlation_id"),
}
ROUTE_RE = re.compile(r"@\s*(?:app|router)\.(?:get|post|put|patch|delete|options|head)\s*\(", re.IGNORECASE)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _strip_sql_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", " ", text)


def _normalize_identifier(value: str) -> str:
    return value.replace('"', "").replace(" ", "").lower()


def _split_qualified(value: str) -> tuple[str, str]:
    normalized = _normalize_identifier(value)
    if "." in normalized:
        schema, table = normalized.split(".", 1)
        return schema, table
    return "public", normalized


def _balanced_body(text: str, opening: int) -> tuple[str, int]:
    depth = 0
    quote: str | None = None
    i = opening
    while i < len(text):
        char = text[i]
        if quote:
            if char == quote:
                if quote == "'" and i + 1 < len(text) and text[i + 1] == "'":
                    i += 2
                    continue
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[opening + 1 : i], i
        i += 1
    raise ValueError("Unbalanced CREATE TABLE body")


def _split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    i = 0
    while i < len(value):
        char = value[i]
        if quote:
            current.append(char)
            if char == quote:
                if quote == "'" and i + 1 < len(value) and value[i + 1] == "'":
                    current.append(value[i + 1])
                    i += 2
                    continue
                quote = None
        elif char in {"'", '"'}:
            quote = char
            current.append(char)
        elif char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth = max(0, depth - 1)
            current.append(char)
        elif char == "," and depth == 0:
            chunk = "".join(current).strip()
            if chunk:
                parts.append(chunk)
            current = []
        else:
            current.append(char)
        i += 1
    chunk = "".join(current).strip()
    if chunk:
        parts.append(chunk)
    return parts


def _column_name(definition: str) -> str | None:
    candidate = definition.strip()
    if not candidate:
        return None
    upper = candidate.upper()
    if upper.startswith(
        ("CONSTRAINT ", "PRIMARY ", "FOREIGN ", "UNIQUE ", "CHECK ", "EXCLUDE ", "LIKE ")
    ):
        return None
    match = re.match(rf"^(?P<name>{IDENT})\s+", candidate)
    return _normalize_identifier(match.group("name")) if match else None


def extract_sql_assets(text: str) -> dict[str, Any]:
    """Return schemas, tables, columns, indexes and reference count from SQL."""
    clean = _strip_sql_comments(text)
    schemas = {_normalize_identifier(m.group("name")) for m in CREATE_SCHEMA_RE.finditer(clean)}
    tables: dict[str, set[str]] = {}

    for match in CREATE_TABLE_RE.finditer(clean):
        body, _ = _balanced_body(clean, match.end() - 1)
        schema, table = _split_qualified(match.group("name"))
        logical = f"{schema}.{table}"
        columns = tables.setdefault(logical, set())
        for definition in _split_top_level(body):
            column = _column_name(definition)
            if column:
                columns.add(column)
        schemas.add(schema)

    for statement in clean.split(";"):
        match = ALTER_TABLE_RE.search(statement)
        if not match:
            continue
        schema, table = _split_qualified(match.group("name"))
        logical = f"{schema}.{table}"
        columns = tables.setdefault(logical, set())
        for definition in _split_top_level(match.group("body")):
            add = ADD_COLUMN_RE.match(definition)
            if add:
                columns.add(_normalize_identifier(add.group("name")))
        schemas.add(schema)

    return {
        "schemas": sorted(schemas),
        "tables": {name: sorted(columns) for name, columns in sorted(tables.items())},
        "indexes": sorted({_normalize_identifier(m.group("name")) for m in INDEX_RE.finditer(clean)}),
        "references": len(REFERENCE_RE.findall(clean)),
    }


def _iter_text_files(root: Path):
    generated_root = root / "docs" / "governance" / "generated"
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if generated_root in path.parents:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".env.example"}:
            continue
        try:
            if path.stat().st_size > MAX_TEXT_BYTES:
                continue
        except OSError:
            continue
        yield path


def _static_evidence(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    marker_paths: dict[str, set[str]] = {key: set() for key in MARKERS}
    marker_hits: dict[str, int] = {key: 0 for key in MARKERS}
    route_paths: set[str] = set()
    route_count = 0

    for path in _iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        relative = path.relative_to(root).as_posix()
        lowered = text.lower()
        for category, markers in MARKERS.items():
            hits = sum(lowered.count(marker) for marker in markers)
            if hits:
                marker_hits[category] += hits
                marker_paths[category].add(relative)
        routes = len(ROUTE_RE.findall(text))
        if routes:
            route_count += routes
            route_paths.add(relative)

    non_relational = {
        category: {
            "status": "partial_static_evidence" if marker_paths[category] else "not_detected",
            "marker_hits": marker_hits[category],
            "evidence_paths": sorted(marker_paths[category]),
        }
        for category in sorted(MARKERS)
    }
    api = {
        "status": "partial_static_evidence" if route_count else "not_detected",
        "route_decorators": route_count,
        "evidence_paths": sorted(route_paths),
    }
    return non_relational, api


def build_inventory(root: Path = ROOT) -> dict[str, Any]:
    baseline = _load_json(root / BASELINE_PATH.relative_to(ROOT))
    policy = _load_json(root / POLICY_PATH.relative_to(ROOT))

    migration_entries: list[dict[str, Any]] = []
    schemas: set[str] = set()
    tables: dict[str, set[str]] = {}
    indexes: set[str] = set()
    references = 0

    migrations_dir = root / MIGRATIONS_DIR.relative_to(ROOT)
    for path in sorted(migrations_dir.glob("*.sql")):
        assets = extract_sql_assets(path.read_text(encoding="utf-8"))
        schemas.update(assets["schemas"])
        for table, columns in assets["tables"].items():
            tables.setdefault(table, set()).update(columns)
        indexes.update(assets["indexes"])
        references += int(assets["references"])
        migration_entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _sha256(path),
                "schemas": assets["schemas"],
                "tables": assets["tables"],
                "indexes": assets["indexes"],
                "references": assets["references"],
            }
        )

    module_contracts = sorted(
        path.relative_to(root).as_posix()
        for path in (root / "modules").glob("*/DATABASE.md")
        if path.is_file()
    )
    non_relational, api = _static_evidence(root)

    target = baseline["target"]
    field_registry_contract = root / "config" / "compliance" / "field_registry.json"
    physical_registry = any(
        "compliance.field_registry" in entry["tables"] for entry in migration_entries
    )

    return {
        "schema_version": "1.0.0",
        "source_issue": baseline["source_issue"],
        "orchestrator_issue": baseline["orchestrator_issue"],
        "source_baseline_sha": baseline["source_main_sha"],
        "evidence_scope": baseline["scope"],
        "runtime_database_connected": baseline["runtime_database_connected"],
        "target": target,
        "policy": {
            "source_blueprint_version": policy["source_blueprint_version"],
            "field_registration_before_migration": policy["rules"]["field_registration_before_migration"],
            "same_head_sha_gates": policy["delivery"]["same_head_sha_gates"],
        },
        "postgres": {
            "status": "implemented_repository_evidence",
            "migration_count": len(migration_entries),
            "schema_count": len(schemas),
            "table_count": len(tables),
            "column_count": sum(len(columns) for columns in tables.values()),
            "index_count": len(indexes),
            "reference_count": references,
            "schemas": sorted(schemas),
            "tables": {name: sorted(columns) for name, columns in sorted(tables.items())},
            "migrations": migration_entries,
        },
        "module_database_contracts": {
            "status": "implemented_repository_evidence",
            "count": len(module_contracts),
            "paths": module_contracts,
        },
        "non_relational": non_relational,
        "api": api,
        "delta": [
            {
                "capability": "repository_inventory",
                "status": "implemented",
                "evidence": "docs/governance/generated/fase0_inventory.json",
            },
            {
                "capability": "field_registry_contract",
                "status": "implemented" if field_registry_contract.exists() else "planned",
                "evidence": "config/compliance/field_registry.json",
            },
            {
                "capability": "physical_compliance_field_registry",
                "status": "implemented" if physical_registry else "planned",
                "evidence": "database/postgres/migrations",
            },
            {
                "capability": "runtime_database_reconciliation",
                "status": "conditional",
                "evidence": "Requires a real non-production DSN and owner approval",
            },
            {
                "capability": "target_702_logical_tables",
                "status": "planned",
                "evidence": "No indiscriminate physical creation is authorized",
            },
            {
                "capability": "owner_confirmation_all_assets",
                "status": "partial",
                "evidence": f"{len(module_contracts)} module DATABASE.md contracts detected",
            },
        ],
    }


def render_report(inventory: dict[str, Any]) -> str:
    postgres = inventory["postgres"]
    lines = [
        "# Fase 0 - Inventário Estático da Main",
        "",
        "**Projeto:** All in One + Valley  ",
        "**Classificação:** Pendências / Técnico / Equipe Técnica  ",
        f"**Issue executora:** #{inventory['source_issue']}  ",
        f"**SHA congelado:** `{inventory['source_baseline_sha']}`  ",
        "**Escopo da evidência:** repositório estático, sem conexão a banco ou serviços externos  ",
        "",
        "## Resumo PostgreSQL",
        "",
        f"- migrations SQL: **{postgres['migration_count']}**",
        f"- schemas detectados: **{postgres['schema_count']}**",
        f"- tabelas detectadas: **{postgres['table_count']}**",
        f"- colunas detectadas: **{postgres['column_count']}**",
        f"- índices detectados: **{postgres['index_count']}**",
        f"- referências detectadas: **{postgres['reference_count']}**",
        "",
        "## Ativos transversais",
        "",
        f"- contratos `modules/*/DATABASE.md`: **{inventory['module_database_contracts']['count']}**",
        f"- rotas API detectadas por decorador: **{inventory['api']['route_decorators']}**",
    ]
    for category, evidence in inventory["non_relational"].items():
        lines.append(
            f"- {category}: **{evidence['status']}**, "
            f"{len(evidence['evidence_paths'])} arquivo(s) com evidência"
        )
    lines.extend(
        [
            "",
            "## Delta atual x alvo",
            "",
            "| Capacidade | Estado | Evidência |",
            "|---|---|---|",
        ]
    )
    for row in inventory["delta"]:
        lines.append(f"| `{row['capability']}` | **{row['status']}** | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## Limites desta evidência",
            "",
            "- Não comprova dados existentes em ambientes externos.",
            "- Não comprova RLS, ABAC, retenção, descarte, DNS, credenciais ou homologação.",
            "- Não autoriza criação física das 702 tabelas lógicas.",
            "- A reconciliação runtime permanece condicional a DSN não produtivo e aprovação de owner.",
            "",
        ]
    )
    return "\n".join(lines)


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_outputs(root: Path = ROOT) -> None:
    inventory = build_inventory(root)
    inventory_path = root / INVENTORY_PATH.relative_to(ROOT)
    report_path = root / REPORT_PATH.relative_to(ROOT)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text(_canonical_json(inventory), encoding="utf-8")
    report_path.write_text(render_report(inventory), encoding="utf-8")


def check_outputs(root: Path = ROOT) -> list[str]:
    inventory = build_inventory(root)
    expected_inventory = _canonical_json(inventory)
    expected_report = render_report(inventory)
    errors: list[str] = []
    inventory_path = root / INVENTORY_PATH.relative_to(ROOT)
    report_path = root / REPORT_PATH.relative_to(ROOT)
    if not inventory_path.exists():
        errors.append(f"missing generated inventory: {inventory_path.relative_to(root)}")
    elif inventory_path.read_text(encoding="utf-8") != expected_inventory:
        errors.append("generated inventory is stale; run scripts/compliance_inventory.py --write")
    if not report_path.exists():
        errors.append(f"missing generated report: {report_path.relative_to(root)}")
    elif report_path.read_text(encoding="utf-8") != expected_report:
        errors.append("generated report is stale; run scripts/compliance_inventory.py --write")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated evidence")
    mode.add_argument("--check", action="store_true", help="verify committed evidence")
    mode.add_argument("--print", action="store_true", dest="print_inventory", help="print JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write:
        write_outputs()
        print(f"Wrote {INVENTORY_PATH.relative_to(ROOT)} and {REPORT_PATH.relative_to(ROOT)}")
        return 0
    if args.print_inventory:
        print(_canonical_json(build_inventory()), end="")
        return 0
    errors = check_outputs()
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 0 inventory is synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
