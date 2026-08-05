from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database" / "postgres" / "migrations" / "036_compliance_rls_deny_all_baseline.sql"
ROLLBACK = ROOT / "database" / "postgres" / "rollbacks" / "036_compliance_rls_deny_all_baseline.sql"


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
