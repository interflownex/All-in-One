from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ALERTS = {
    "MarketplaceOrdersPaidStalled",
    "MarketplaceConversionLow",
    "MarketplaceSupportBacklogHigh",
    "MarketplaceReputationLow",
    "MarketplaceDisputesUnresolvedHigh",
}


def load_alerts() -> dict:
    return json.loads((ROOT / "config" / "observability" / "commercial_alerts.json").read_text(encoding="utf-8"))


def load_prometheus_rule() -> str:
    return (ROOT / "infra" / "kubernetes" / "base" / "commercial-alerting.yaml").read_text(encoding="utf-8")


def test_commercial_alerts_cover_conversion_support_reputation_and_dispute_backlog() -> None:
    alerts = load_alerts()

    assert set(alerts["alerts"]) == REQUIRED_ALERTS
    assert alerts["scope"] == "marketplace-commercial"
    assert alerts["runbook"] == "docs/OPERATIONS.md#observabilidade-comercial"
    assert alerts["notification_policy"]["include_sensitive_payload"] is False


def test_commercial_alerts_have_prometheus_expr_sla_and_evidence() -> None:
    alerts = load_alerts()

    for name, alert in alerts["alerts"].items():
        assert alert["severity"] in {"critical", "high", "medium"}
        assert alert["expr"], name
        assert alert["for"].endswith("m"), name
        assert 1 <= alert["response_sla_minutes"] <= 240, name
        assert "incident_ticket" in alert["evidence"], name
        assert "payload" not in " ".join(alert["evidence"]).casefold(), name


def test_commercial_alert_expressions_reference_expected_signals() -> None:
    alerts = load_alerts()["alerts"]

    assert "all_in_one_marketplace_orders_paid" in alerts["MarketplaceOrdersPaidStalled"]["expr"]
    assert "all_in_one_marketplace_conversion_rate_percent" in alerts["MarketplaceConversionLow"]["expr"]
    assert "all_in_one_marketplace_support_cases_open" in alerts["MarketplaceSupportBacklogHigh"]["expr"]
    assert "all_in_one_marketplace_average_rating" in alerts["MarketplaceReputationLow"]["expr"]
    assert "all_in_one_marketplace_support_cases_resolved" in alerts["MarketplaceDisputesUnresolvedHigh"]["expr"]


def test_commercial_alerts_are_materialized_as_prometheus_rule_and_alertmanager_route() -> None:
    alerts = load_alerts()["alerts"]
    manifest = load_prometheus_rule()

    assert "kind: PrometheusRule" in manifest
    assert "kind: AlertmanagerConfig" in manifest
    assert "receiver: business-oncall" in manifest
    assert "receiver: platform-oncall" in manifest
    for alert_name, alert in alerts.items():
        assert f"alert: {alert_name}" in manifest
        assert alert["expr"] in manifest
        assert f"for: {alert['for']}" in manifest
        assert f"severity: {alert['severity']}" in manifest
        assert "runbook_url: docs/OPERATIONS.md#observabilidade-comercial" in manifest
