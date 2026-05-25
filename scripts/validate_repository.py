from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))
REQUIRED_MODULE_FILES = {
    "README.md",
    "main.py",
    "requirements.txt",
    "CONTRACT.md",
    "STATUS.md",
    "OPENAPI.yaml",
    "DATABASE.md",
    "EVENTS.md",
    "SECURITY.md",
    "MONETIZATION.md",
    "TESTS.md",
    "Dockerfile",
    "tests/test_health.py",
    "tests/test_contract.py",
    "tests/test_permissions.py",
    "tests/test_create_flow.py",
}
REQUIRED_SCHEMAS = {
    "identity", "business", "permissions", "marketplace", "stock", "delivery",
    "services", "mobility", "erp", "wms", "tms", "crm", "bpm", "document",
    "finance", "billing", "fiscal", "hr", "health", "vision", "legal",
    "property", "audit", "compliance", "notifications", "api_hub",
    "insurance", "bi", "ai_core", "jobs",
}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    modules = CATALOG["modules"]
    slugs = {module["slug"] for module in modules}
    if len(slugs) != 25:
        fail(f"Esperados 25 modulos; catalogo possui {len(slugs)}.", errors)
    for module in modules:
        base = ROOT / "modules" / module["slug"]
        for relative in REQUIRED_MODULE_FILES:
            if not (base / relative).is_file():
                fail(f"Ausente: modules/{module['slug']}/{relative}", errors)
        if not (ROOT / "contracts" / f"{module['slug']}.md").is_file():
            fail(f"Contrato ausente: {module['slug']}", errors)
    for app in CATALOG["apps"]:
        if not (ROOT / "apps" / app["slug"] / "README.md").is_file():
            fail(f"App ausente: {app['slug']}", errors)
    migrations = "\n".join(
        item.read_text(encoding="utf-8")
        for item in sorted((ROOT / "database" / "postgres" / "migrations").glob("*.sql"))
    )
    for schema in REQUIRED_SCHEMAS:
        if f"CREATE SCHEMA IF NOT EXISTS {schema}" not in migrations:
            fail(f"Schema PostgreSQL nao declarado: {schema}", errors)
    for needle in [
        "identity.users",
        "finance.wallets",
        "NUMERIC(18, 4)",
        "NUMERIC(18, 8)",
        "reject_immutable_change",
        "audit.logs",
        "jobs.resumes",
        "employment_provenance_integrity",
        "immutable_jobs_resume_access_logs",
    ]:
        if needle not in migrations:
            fail(f"Controle SQL ausente: {needle}", errors)
    for workflow in ["ci.yml", "security.yml", "database.yml", "openapi.yml", "autocommit.yml", "automerge.yml"]:
        if not (ROOT / ".github" / "workflows" / workflow).is_file():
            fail(f"Workflow ausente: {workflow}", errors)
    if errors:
        print("Validacao falhou:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Baseline valido: {len(slugs)} modulos, {len(CATALOG['apps'])} apps e controles centrais presentes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
