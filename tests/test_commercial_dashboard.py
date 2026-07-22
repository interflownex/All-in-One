from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PANEL_TITLES = {
    "Pedidos totais",
    "Pedidos pagos",
    "Pedidos concluidos",
    "Casos abertos",
    "Casos resolvidos",
    "Avaliacoes",
    "Nota media",
    "Conversao",
    "Tendencia de pedidos e suporte",
    "Tendencia de conversao e reputacao",
}
REQUIRED_METRICS = {
    "all_in_one_marketplace_orders_total",
    "all_in_one_marketplace_orders_paid",
    "all_in_one_marketplace_orders_completed",
    "all_in_one_marketplace_support_cases_total",
    "all_in_one_marketplace_support_cases_open",
    "all_in_one_marketplace_support_cases_resolved",
    "all_in_one_marketplace_reviews_total",
    "all_in_one_marketplace_average_rating",
    "all_in_one_marketplace_conversion_rate_percent",
}


def load_dashboard() -> dict:
    return json.loads((ROOT / "config" / "observability" / "commercial_dashboard.json").read_text(encoding="utf-8"))


def load_prometheus_dashboard_manifest() -> str:
    return (ROOT / "infra" / "kubernetes" / "base" / "commercial-dashboard.yaml").read_text(encoding="utf-8")


def test_commercial_dashboard_has_expected_identity_and_panels() -> None:
    dashboard = load_dashboard()

    assert dashboard["uid"] == "marketplace-commercial"
    assert dashboard["title"] == "All-in-One - Marketplace Comercial"
    assert dashboard["refresh"] == "30s"
    assert dashboard["time"] == {"from": "now-24h", "to": "now"}
    assert set(dashboard["tags"]) == {"all-in-one", "marketplace", "commercial"}

    panels = dashboard["panels"]
    assert len(panels) >= 10
    assert REQUIRED_PANEL_TITLES.issubset({panel["title"] for panel in panels})
    assert any(panel["type"] == "timeseries" for panel in panels)


def test_commercial_dashboard_mentions_required_metrics() -> None:
    dashboard = load_dashboard()

    expressions = {
        target["expr"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if isinstance(target, dict) and target.get("expr")
    }

    for metric in REQUIRED_METRICS:
        assert any(metric in expr for expr in expressions), metric


def test_commercial_dashboard_is_materialized_as_kubernetes_configmap() -> None:
    manifest = load_prometheus_dashboard_manifest()

    assert "kind: ConfigMap" in manifest
    assert 'grafana_dashboard: "1"' in manifest
    assert "commercial-dashboard.json" in manifest
    assert "All-in-One - Marketplace Comercial" in manifest
    assert "all_in_one_marketplace_orders_total" in manifest
    assert "all_in_one_marketplace_conversion_rate_percent" in manifest
