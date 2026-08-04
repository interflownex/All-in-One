from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "database"
    / "postgres"
    / "migrations"
    / "034_compliance_field_registry.sql"
)
ROLLBACK = (
    ROOT
    / "database"
    / "postgres"
    / "rollbacks"
    / "034_compliance_field_registry.sql"
)
REGISTRY = ROOT / "config" / "compliance" / "field_registry.v1.json"


def _load_validator():
    path = ROOT / "scripts/validate_compliance_catalog.py"
    spec = importlib.util.spec_from_file_location(
        "compliance_validator_migration", path
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_and_rollback_are_transactional_and_reversible() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")

    assert migration.startswith("BEGIN;\n")
    assert migration.rstrip().endswith("COMMIT;")
    assert "CREATE TABLE IF NOT EXISTS compliance.catalog_versions" in migration
    assert "CREATE TABLE IF NOT EXISTS compliance.field_registry" in migration
    assert "idx_compliance_field_registry_field_id" in migration
    assert "idx_compliance_field_registry_asset_field" in migration
    assert "jsonb_typeof(lineage) = 'array'" in migration
    assert "jsonb_typeof(bundle_ids) = 'array'" in migration
    assert "metadata JSONB" not in migration

    assert rollback.startswith("BEGIN;\n")
    assert rollback.rstrip().endswith("COMMIT;")
    assert rollback.index("DROP TABLE IF EXISTS compliance.field_registry") < (
        rollback.index("DROP TABLE IF EXISTS compliance.catalog_versions")
    )


def test_registry_covers_every_column_created_by_migration() -> None:
    validator = _load_validator()
    migration = MIGRATION.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    created = {
        item
        for item in validator.parse_columns(migration)
        if item[0]
        in {"compliance.catalog_versions", "compliance.field_registry"}
    }
    registered = {
        (item["asset"].lower(), item["field"].lower())
        for item in registry["fields"]
    }

    assert len(created) == 33
    assert created == registered


def test_seed_contains_every_catalogued_field_and_frozen_baseline() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert registry["baseline_sha"] in migration
    assert "'1.0.0'" in migration
    for field in registry["fields"]:
        assert field["field_id"] in migration


def test_registry_contains_no_unclassified_or_unowned_field() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert registry["fields"]
    assert all(item["owner"] for item in registry["fields"])
    assert all(item["purpose"] for item in registry["fields"])
    assert all(item["legal_basis"] for item in registry["fields"])
    assert all(item["bundle_ids"] for item in registry["fields"])
    assert all(item["status"] == "implemented" for item in registry["fields"])
