import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOKS_PATH = ROOT / "config" / "operations" / "incident_response_runbooks.json"

REQUIRED_RUNBOOKS = {
    "security_sensitive_access",
    "payments_ledger_integrity",
    "outbox_delivery_failure",
    "retention_lgpd_failure",
    "backup_restore_dr",
    "slo_burn_rate",
}


def load_runbooks() -> dict:
    return json.loads(RUNBOOKS_PATH.read_text(encoding="utf-8"))


def test_incident_response_runbooks_cover_critical_classes_without_sensitive_payloads() -> None:
    catalog = load_runbooks()

    assert catalog["version"] == "2026-07-15"
    assert catalog["scope"] == "incident_response_runbooks"
    assert catalog["runbook_index"] == "docs/OPERATIONS.md#incidentes"
    assert catalog["notification_policy"]["include_sensitive_payload"] is False
    assert set(catalog["runbooks"]) == REQUIRED_RUNBOOKS

    for name, runbook in catalog["runbooks"].items():
        assert runbook["severity"] in {"critical", "high", "medium"}, name
        assert runbook["owner"], name
        assert runbook["domains"], name
        assert runbook["runbook"].startswith("docs/"), name
        assert runbook["trigger_signals"], name
        assert runbook["containment"], name
        assert runbook["recovery_validation"], name
        assert "incident_ticket" in runbook["evidence"], name
        assert "payload" not in " ".join(runbook["evidence"]).casefold(), name


def test_critical_incidents_require_postmortem_and_recovery_tests_exist() -> None:
    catalog = load_runbooks()

    for name, runbook in catalog["runbooks"].items():
        if runbook["severity"] == "critical":
            assert runbook["postmortem_required"] is True, name
        for validation in runbook["recovery_validation"]:
            if validation.startswith("python3 "):
                validation = validation.removeprefix("python3 ")
            if validation.endswith(".py"):
                assert (ROOT / validation).is_file(), validation


def test_incident_runbooks_reference_existing_operational_sections() -> None:
    catalog = load_runbooks()
    operations = (ROOT / "docs" / "OPERATIONS.md").read_text(encoding="utf-8")
    security = (ROOT / "docs" / "SECURITY.md").read_text(encoding="utf-8")

    assert "## Incidentes" in operations
    assert "## Backup, Restore E DR" in operations
    assert "## SLO E Alertas" in operations
    assert "### Runbook de incidentes da outbox" in operations
    assert "## Revisao De Permissoes Sensiveis" in security

    for runbook in catalog["runbooks"].values():
        if runbook["runbook"].startswith("docs/OPERATIONS.md"):
            anchor = runbook["runbook"].split("#", 1)[1]
            normalized = anchor.replace("-", " ").casefold()
            assert any(token in operations.casefold() for token in normalized.split()), runbook["runbook"]
