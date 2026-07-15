import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLO_CATALOG = ROOT / "config" / "observability" / "slo_catalog.json"
OUTBOX_ALERTS = ROOT / "config" / "observability" / "outbox_alerts.json"
RETENTION_ALERTS = ROOT / "config" / "observability" / "retention_alerts.json"

REQUIRED_SLOS = {
    "api_hub_gateway_availability",
    "identity_auth_latency_p95",
    "finance_ledger_write_success",
    "outbox_delivery_freshness",
    "retention_decision_timeliness",
    "jobs_document_vault_access_audit",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_slo_catalog_defines_critical_services_without_sensitive_payloads() -> None:
    catalog = load_json(SLO_CATALOG)

    assert catalog["version"] == "2026-07-15"
    assert catalog["metric_source"] == "kubernetes-prometheus"
    assert catalog["runbook_index"] == "docs/OPERATIONS.md#slo-e-alertas"
    assert catalog["notification_policy"]["include_sensitive_payload"] is False
    assert set(catalog["slo_targets"]) == REQUIRED_SLOS

    for name, slo in catalog["slo_targets"].items():
        assert slo["service"], name
        assert slo["objective"], name
        assert slo["window"], name
        assert slo["sli"], name
        assert slo["promql"], name
        assert slo["runbook"].startswith("docs/OPERATIONS.md#"), name
        assert "incident_ticket" in slo["evidence"], name
        assert "payload" not in " ".join(slo["evidence"]).casefold(), name
        assert slo["burn_rate_alerts"], name
        for alert in slo["burn_rate_alerts"]:
            assert alert["severity"] in {"critical", "high", "medium"}, name
            assert alert["expr"], name
            assert alert["for"].endswith("m"), name
            assert 1 <= alert["response_sla_minutes"] <= 240, name


def test_slo_catalog_reuses_materialized_outbox_and_retention_alerts() -> None:
    catalog = load_json(SLO_CATALOG)["slo_targets"]
    outbox = load_json(OUTBOX_ALERTS)["alerts"]
    retention = load_json(RETENTION_ALERTS)["alerts"]

    outbox_alert = catalog["outbox_delivery_freshness"]["burn_rate_alerts"][0]
    retention_alert = catalog["retention_decision_timeliness"]["burn_rate_alerts"][0]

    assert outbox_alert["materialized_alert"] == "OutboxOldestPendingTooOld"
    assert outbox_alert["expr"] == outbox["OutboxOldestPendingTooOld"]["expr"]
    assert outbox_alert["for"] == outbox["OutboxOldestPendingTooOld"]["for"]
    assert outbox_alert["response_sla_minutes"] == outbox["OutboxOldestPendingTooOld"]["response_sla_minutes"]

    assert retention_alert["materialized_alert"] == "RetentionOldestCandidateTooOld"
    assert retention_alert["expr"] == retention["RetentionOldestCandidateTooOld"]["expr"]
    assert retention_alert["for"] == retention["RetentionOldestCandidateTooOld"]["for"]
    assert retention_alert["response_sla_minutes"] == retention["RetentionOldestCandidateTooOld"]["response_sla_minutes"]
