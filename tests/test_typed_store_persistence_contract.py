from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_every_declared_typed_store_target_exists_in_the_physical_catalog() -> None:
    dictionary = json.loads(
        (ROOT / "docs/data-audit/artifacts/dicionario_de_dados.json").read_text(
            encoding="utf-8"
        )
    )
    physical_tables = {
        f"{field['schema']}.{field['table']}" for field in dictionary["fields"]
    }
    missing: list[str] = []

    for path in sorted((ROOT / "modules/shared").glob("*_postgres_store.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            target = (
                node.target
                if isinstance(node, ast.AnnAssign)
                else node.targets[0]
                if len(node.targets) == 1
                else None
            )
            if not isinstance(target, ast.Name) or target.id not in {
                "TABLES",
                "tables",
            }:
                continue
            try:
                mapping = ast.literal_eval(node.value)
            except (TypeError, ValueError):
                continue
            if isinstance(mapping, dict):
                missing.extend(
                    f"{path.name}:{resource}->{table}"
                    for resource, table in mapping.items()
                    if table not in physical_tables
                )

    assert not missing, "Relações tipadas sem migration: " + ", ".join(missing)


def test_migration_026_is_reversible_for_every_created_relation() -> None:
    migration = (
        ROOT / "database/postgres/migrations/026_complete_typed_store_relations.sql"
    ).read_text(encoding="utf-8")
    rollback = (
        ROOT / "database/postgres/rollbacks/026_complete_typed_store_relations.down.sql"
    ).read_text(encoding="utf-8")
    created = {
        line.split()[5]
        for line in migration.splitlines()
        if line.startswith("CREATE TABLE IF NOT EXISTS ")
    }
    dropped = {
        line.removeprefix("DROP TABLE IF EXISTS ").rstrip(";")
        for line in rollback.splitlines()
        if line.startswith("DROP TABLE IF EXISTS ")
    }

    assert len(created) == 44
    assert created == dropped


def test_migration_027_is_reversible_for_legacy_adapter_relations() -> None:
    migration = (
        ROOT / "database/postgres/migrations/027_complete_legacy_adapter_relations.sql"
    ).read_text(encoding="utf-8")
    rollback = (
        ROOT
        / "database/postgres/rollbacks/027_complete_legacy_adapter_relations.down.sql"
    ).read_text(encoding="utf-8")
    created = {
        line.split()[5]
        for line in migration.splitlines()
        if line.startswith("CREATE TABLE IF NOT EXISTS ")
    }
    dropped = {
        line.removeprefix("DROP TABLE IF EXISTS ").rstrip(";")
        for line in rollback.splitlines()
        if line.startswith("DROP TABLE IF EXISTS ")
    }

    assert len(created) == 13
    assert created == dropped


def test_every_logical_entity_has_an_executable_physical_storage_decision() -> None:
    catalog = json.loads(
        (ROOT / "docs/data-audit/artifacts/catalogo_logico.json").read_text(
            encoding="utf-8"
        )
    )

    assert catalog["counts"]["logical_without_physical_table"] == 0
    assert all(entity["has_physical_table"] for entity in catalog["entities"])
    assert {entity["persistence_decision"] for entity in catalog["entities"]} <= {
        "typed_table",
        "typed_alias",
    }
