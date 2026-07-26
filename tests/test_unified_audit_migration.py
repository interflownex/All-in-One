from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database/postgres/migrations/029_unified_immutable_audit.sql"
ROLLBACK = ROOT / "database/postgres/rollbacks/029_unified_immutable_audit.down.sql"


def test_audit_migration_materializes_context_read_integrity_and_retention() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    for column in (
        "tenant_id",
        "company_id",
        "actor_role",
        "session_id",
        "device_id",
        "origin",
        "channel",
        "changed_fields",
        "reason",
        "correlation_id",
        "causation_id",
        "occurred_at",
        "result",
        "error_detail",
        "authorization",
        "approval_id",
        "approved_by",
        "previous_hash",
        "row_hash",
        "exported",
        "printed",
        "shared",
        "retention_until",
    ):
        if column == "authorization":
            assert '"authorization" TEXT' in source
        else:
            assert f"{column} " in source
    assert "WHERE action = 'sensitive_read'" in source
    assert "idx_audit_logs_tenant_occurred" in source
    assert "SHA-256" in source


def test_audit_migration_preserves_the_existing_append_only_trigger() -> None:
    prior = (
        ROOT / "database/postgres/migrations/005_audit_events_api_security.sql"
    ).read_text(encoding="utf-8")
    assert "CREATE TRIGGER immutable_audit_logs" in prior
    assert "DROP TRIGGER" not in MIGRATION.read_text(encoding="utf-8")


def test_audit_rollback_is_transactional_and_removes_only_added_contract() -> None:
    source = ROLLBACK.read_text(encoding="utf-8")
    assert source.startswith("BEGIN;")
    assert source.rstrip().endswith("COMMIT;")
    assert "DROP TABLE" not in source
    assert "DROP COLUMN IF EXISTS row_hash" in source
