from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database" / "postgres" / "migrations" / "035_compliance_access_context.sql"
ROLLBACK = ROOT / "database" / "postgres" / "rollbacks" / "035_compliance_access_context.sql"


def test_access_context_migration_is_transactional_and_reversible() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")

    assert migration.startswith("BEGIN;\n")
    assert migration.rstrip().endswith("COMMIT;")
    assert rollback.startswith("BEGIN;\n")
    assert rollback.rstrip().endswith("COMMIT;")

    expected_functions = (
        "compliance.require_access_context",
        "compliance.current_tenant_id",
        "compliance.current_subject_id",
        "compliance.current_processing_purpose",
    )
    for function in expected_functions:
        assert f"FUNCTION {function}" in migration
        assert f"FUNCTION IF EXISTS {function}" in rollback


def test_access_context_is_fail_closed_and_uuid_validated() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")

    for setting in (
        "app.tenant_id",
        "app.subject_id",
        "app.subject_type",
        "app.processing_purpose",
        "app.request_id",
    ):
        assert f"current_setting('{setting}', true)" in migration

    assert migration.count("USING ERRCODE = '28000'") >= 5
    assert "tenant_value::uuid" in migration
    assert "subject_value::uuid" in migration
    assert "request_value::uuid" in migration
    assert "SECURITY DEFINER" not in migration
    assert migration.count("SECURITY INVOKER") == 4
    assert migration.count("SET search_path = pg_catalog, compliance") == 4


def test_context_contract_restricts_subjects_purposes_and_public_execute() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")

    for subject_type in ("user", "service", "support", "auditor"):
        assert f"'{subject_type}'" in migration

    for purpose in (
        "service_delivery",
        "security",
        "compliance",
        "support",
        "data_subject_request",
    ):
        assert f"'{purpose}'" in migration

    assert migration.count("REVOKE ALL ON FUNCTION") == 4
    assert migration.count("FROM PUBLIC") == 4
    assert "BYPASSRLS" not in migration
    assert "CREATE POLICY" not in migration
    assert "ENABLE ROW LEVEL SECURITY" not in migration
