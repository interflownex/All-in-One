import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ALERTS = {
    "OutboxPublishStalled",
    "OutboxBacklogHigh",
    "OutboxDueHigh",
    "OutboxRetryFailuresHigh",
    "OutboxOldestPendingTooOld",
}


def load_alerts() -> dict:
    return json.loads((ROOT / "config" / "observability" / "outbox_alerts.json").read_text(encoding="utf-8"))


def load_prometheus_rule() -> str:
    return (ROOT / "infra" / "kubernetes" / "base" / "outbox-alerting.yaml").read_text(encoding="utf-8")


def test_outbox_alerts_cover_publish_stall_backlog_retry_failure_and_age() -> None:
    alerts = load_alerts()

    assert set(alerts["alerts"]) == REQUIRED_ALERTS
    assert alerts["scope"] == "outbox-dispatcher"
    assert alerts["runbook"] == "docs/OPERATIONS.md#outbox"
    assert alerts["notification_policy"]["include_sensitive_payload"] is False


def test_outbox_alerts_have_prometheus_expr_sla_and_evidence() -> None:
    alerts = load_alerts()

    for name, alert in alerts["alerts"].items():
        assert alert["severity"] in {"critical", "high", "medium"}
        assert alert["expr"], name
        assert alert["for"].endswith("m"), name
        assert 1 <= alert["response_sla_minutes"] <= 240, name
        assert "incident_ticket" in alert["evidence"], name
        assert "payload" not in " ".join(alert["evidence"]).casefold(), name


def test_outbox_alert_expressions_reference_expected_signals() -> None:
    alerts = load_alerts()["alerts"]

    assert "all_in_one_outbox_published_total" in alerts["OutboxPublishStalled"]["expr"]
    assert "all_in_one_outbox_pending" in alerts["OutboxBacklogHigh"]["expr"]
    assert "all_in_one_outbox_due" in alerts["OutboxDueHigh"]["expr"]
    assert "all_in_one_outbox_failed_retryable_total" in alerts["OutboxRetryFailuresHigh"]["expr"]
    assert "all_in_one_outbox_oldest_pending_age_seconds" in alerts["OutboxOldestPendingTooOld"]["expr"]


def test_outbox_alerts_are_materialized_as_prometheus_rule_and_alertmanager_route() -> None:
    alerts = load_alerts()["alerts"]
    manifest = load_prometheus_rule()

    assert "kind: PrometheusRule" in manifest
    assert "kind: AlertmanagerConfig" in manifest
    assert "receiver: operations-oncall" in manifest
    assert "receiver: platform-oncall" in manifest
    for alert_name, alert in alerts.items():
        assert f"alert: {alert_name}" in manifest
        assert alert["expr"] in manifest
        assert f"for: {alert['for']}" in manifest
        assert f"severity: {alert['severity']}" in manifest
        assert "runbook_url: docs/OPERATIONS.md#outbox" in manifest
