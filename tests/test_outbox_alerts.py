import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ALERTS = {
    "OutboxBacklogHigh",
    "OutboxOldestPendingTooOld",
    "OutboxRetryableFailuresHigh",
    "OutboxDueWithoutDeliveries",
}


def load_alerts() -> dict:
    return json.loads(
        (ROOT / "config" / "observability" / "outbox_alerts.json").read_text(
            encoding="utf-8"
        )
    )


def load_prometheus_rule() -> str:
    return (ROOT / "infra" / "kubernetes" / "base" / "outbox-alerting.yaml").read_text(
        encoding="utf-8"
    )


def load_dashboard() -> dict:
    return json.loads(
        (ROOT / "config" / "observability" / "outbox_dashboard.json").read_text(
            encoding="utf-8"
        )
    )


def test_outbox_alerts_cover_backlog_staleness_failures_and_delivery_gap() -> None:
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


def test_outbox_alert_expressions_reference_exported_metrics() -> None:
    alerts = load_alerts()["alerts"]

    assert "all_in_one_outbox_pending" in alerts["OutboxBacklogHigh"]["expr"]
    assert (
        "all_in_one_outbox_oldest_pending_age_seconds"
        in alerts["OutboxOldestPendingTooOld"]["expr"]
    )
    assert (
        "all_in_one_outbox_failed_retryable_total"
        in alerts["OutboxRetryableFailuresHigh"]["expr"]
    )
    assert "all_in_one_outbox_due" in alerts["OutboxDueWithoutDeliveries"]["expr"]
    assert (
        "all_in_one_outbox_published_total"
        in alerts["OutboxDueWithoutDeliveries"]["expr"]
    )


def test_outbox_alerts_are_materialized_as_prometheus_rule_and_alertmanager_route() -> (
    None
):
    alerts = load_alerts()["alerts"]
    manifest = load_prometheus_rule()

    assert "kind: PrometheusRule" in manifest
    assert "kind: AlertmanagerConfig" in manifest
    assert "receiver: platform-oncall" in manifest
    for alert_name, alert in alerts.items():
        assert f"alert: {alert_name}" in manifest
        assert alert["expr"] in manifest
        assert f"for: {alert['for']}" in manifest
        assert f"severity: {alert['severity']}" in manifest
        assert "runbook_url: docs/OPERATIONS.md#outbox" in manifest


def test_outbox_alerting_manifest_is_included_in_base_kustomization() -> None:
    kustomization = (
        ROOT / "infra" / "kubernetes" / "base" / "kustomization.yaml"
    ).read_text(encoding="utf-8")

    assert "outbox-alerting.yaml" in kustomization


def test_outbox_dashboard_covers_all_exported_operational_metrics() -> None:
    dashboard = load_dashboard()
    panels = dashboard["dashboard"]["panels"]
    expressions = " ".join(panel["expr"] for panel in panels)

    assert dashboard["scope"] == "outbox-dispatcher"
    assert dashboard["dashboard"]["uid"] == "all-in-one-outbox-dispatcher"
    assert len(panels) >= 6
    assert "all_in_one_outbox_pending" in expressions
    assert "all_in_one_outbox_due" in expressions
    assert "all_in_one_outbox_published_total" in expressions
    assert "all_in_one_outbox_failed_retryable_total" in expressions
    assert "all_in_one_outbox_max_retry_count" in expressions
    assert "all_in_one_outbox_oldest_pending_age_seconds" in expressions
