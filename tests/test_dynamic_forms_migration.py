from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "database/postgres/migrations/028_dynamic_forms_governance.sql"
ROLLBACK = ROOT / "database/postgres/rollbacks/028_dynamic_forms_governance.down.sql"

REQUIRED_TABLES = {
    "field_catalog",
    "field_bindings",
    "form_definitions",
    "form_versions",
    "form_blocks",
    "form_fields",
    "form_calculations",
    "form_validations",
    "form_visibility_rules",
    "form_permissions",
    "form_homologations",
    "form_publications",
    "form_submissions",
    "form_submission_values",
    "form_billing_events",
}


def test_dynamic_forms_migration_materializes_every_governed_entity() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    for table in REQUIRED_TABLES:
        assert f"CREATE TABLE forms.{table}" in source
        assert f"DROP TABLE IF EXISTS forms.{table}" in ROLLBACK.read_text(
            encoding="utf-8"
        )


def test_dynamic_forms_migration_enforces_tenant_idempotency_and_review() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    assert "UNIQUE (tenant_id, idempotency_key)" in source
    assert "idx_form_definitions_tenant_status" in source
    assert "idx_form_submissions_tenant_status" in source
    assert (
        "published_by IS NOT NULL AND approved_at IS NOT NULL AND checksum IS NOT NULL"
        in source
    )
    assert "immutable_published_form_version" in source
    assert "immutable_published_fields" in source
    assert "Versao publicada e imutavel" in source


def test_dynamic_forms_migration_forbids_executable_or_physical_bindings() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    assert "authorized_binding !~*" in source
    assert "logical_path !~*" in source
    assert "arbitrary_sql" not in source
    assert "javascript TEXT" not in source
    assert "transformation IN ('identity', 'trim', 'lowercase'" in source


def test_dynamic_forms_migration_has_safe_calculation_and_component_allowlists() -> (
    None
):
    source = MIGRATION.read_text(encoding="utf-8")
    assert "operation IN ('sum', 'subtract', 'multiply', 'divide'" in source
    assert "component IN ('text', 'textarea', 'number', 'decimal'" in source
    assert "division_by_zero_handling" in source
    assert "precision BETWEEN 0 AND 12" in source


def test_dynamic_forms_rollback_is_transactional_and_removes_schema_last() -> None:
    source = ROLLBACK.read_text(encoding="utf-8")
    assert source.startswith("BEGIN;")
    assert source.rstrip().endswith("COMMIT;")
    assert source.rfind("DROP SCHEMA IF EXISTS forms") > source.rfind(
        "DROP TABLE IF EXISTS forms.field_catalog"
    )
