#!/usr/bin/env python3
"""Inventário determinístico de ativos de dados para a Governança Fase 0."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/relatorios/governanca/f0_1_inventory.json"
SQL_TABLE = re.compile(r"(?i)create\s+table\s+(?:if\s+not\s+exists\s+)?([\w.\"]+)")
SQL_INDEX = re.compile(r"(?i)create\s+(?:unique\s+)?index\s+")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def classify(path: Path) -> str:
    text = relative(path).lower()
    if "migration" in text and path.suffix == ".sql": return "postgres_migration"
    if path.name in {"package.json", "package-lock.json"}: return "npm_manifest"
    if path.name in {"requirements.txt", "requirements-dev.txt", "pyproject.toml"}: return "python_manifest"
    if path.suffix in {".yaml", ".yml"} and "openapi" in text: return "openapi"
    if "mongo" in text: return "mongodb"
    if "redis" in text: return "redis"
    if "sqlite" in text or path.suffix in {".db", ".sqlite", ".sqlite3"}: return "sqlite"
    if "event" in text: return "event_contract"
    if "storage" in text or "bucket" in text: return "object_or_browser_storage"
    return "other"


def main() -> int:
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    categories = Counter(classify(path) for path in files)
    migrations = [p for p in files if classify(p) == "postgres_migration"]
    tables: set[str] = set()
    indexes = 0
    for path in migrations:
        text = path.read_text(encoding="utf-8", errors="ignore")
        tables.update(match.replace('"', "").lower() for match in SQL_TABLE.findall(text))
        indexes += len(SQL_INDEX.findall(text))
    payload = {
        "schema_version": "1.0.0",
        "scope": "F0.1 reproducible repository inventory",
        "status_legend": ["implemented", "partial", "planned", "conditional", "divergent"],
        "summary": {
            "repository_files": len(files),
            "postgres_migration_files": len(migrations),
            "postgres_declared_tables": len(tables),
            "postgres_declared_indexes": indexes,
            "categories": dict(sorted(categories.items())),
        },
        "assets": {
            "postgres_migrations": sorted(relative(p) for p in migrations),
            "postgres_tables": sorted(tables),
        },
        "limitations": [
            "Inventário estático do repositório, sem alegar equivalência ao ambiente produtivo.",
            "Owners e consumidores serão enriquecidos nos lotes seguintes.",
            "Nenhum dado real, segredo ou conteúdo de banco é coletado."
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Inventário F0.1 gravado em {relative(OUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
