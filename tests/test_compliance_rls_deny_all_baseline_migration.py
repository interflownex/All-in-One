from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database" / "postgres" / "migrations" / "036_compliance_rls_deny_all_baseline.sql"
ROLLBACK = ROOT / "database" / "postgres" / "rollbacks" / "036_compliance_rls_deny_all_baseline.sql"
ACCESS_ASSETS = ROOT / "config" / "compliance" / "access_assets.v1.json"


def test_rls_baseline_is_transactional_and_reversible() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")

    assert migration.startswith("BEGIN;\n")
    assert migration.rstrip().endswith("COMMIT;")
    assert rollback.startswith("BEGIN;\n")
    assert rollback.rstrip().endswith("COMMIT;")

    for table in ("compliance.catalog_versions", "compliance.field_registry"):
        assert f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;" in migration
        assert f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;" in migration
        assert f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;" in rollback
        assert f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;" in rollback


def test_rls_baseline_is_fail_closed_without_premature_policies() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")

    assert "CREATE POLICY" not in migration
    assert "BYPASSRLS" not in migration
    assert "GRANT" not in migration
    assert "SECURITY DEFINER" not in migration
    assert migration.count("ENABLE ROW LEVEL SECURITY") == 2
    assert migration.count("FORCE ROW LEVEL SECURITY") == 2


def test_access_asset_registry_matches_the_rls_baseline() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")
    registry = json.loads(ACCESS_ASSETS.read_text(encoding="utf-8"))

    assets = {item["asset"]: item for item in registry["assets"]}
    assert assets

    for table, asset in assets.items():
        assert asset["access_mode"] == "deny_all"
        assert asset["rls_required"] is True
        assert asset["force_rls_required"] is True
        assert asset["production_activation_blocked"] is True
        assert f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;" in migration
        assert f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;" in migration
        assert f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;" in rollback
        assert f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;" in rollback

    enabled_tables = {
        line.removeprefix("ALTER TABLE ").removesuffix(" ENABLE ROW LEVEL SECURITY;")
        for line in migration.splitlines()
        if line.startswith("ALTER TABLE ") and line.endswith(" ENABLE ROW LEVEL SECURITY;")
    }
    forced_tables = {
        line.removeprefix("ALTER TABLE ").removesuffix(" FORCE ROW LEVEL SECURITY;")
        for line in migration.splitlines()
        if line.startswith("ALTER TABLE ") and line.endswith(" FORCE ROW LEVEL SECURITY;")
    }

    assert enabled_tables == set(assets)
    assert forced_tables == set(assets)
