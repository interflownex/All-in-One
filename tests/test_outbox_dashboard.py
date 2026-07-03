from __future__ import annotations

import json
from pathlib import Path

from modules.shared.outbox_dispatcher import OutboxMetrics, prometheus_metrics


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PANEL_TITLES = {
    "Pendentes",
    "Prontos para retry",
    "Publicados",
    "Falhas retryable",
    "Maior retry observado",
    "Idade do pendente mais antigo",
    "Tendencia do backlog",
    "Tendencia de publicacoes e falhas",
}
REQUIRED_METRICS = {
    "all_in_one_outbox_pending",
    "all_in_one_outbox_due",
    "all_in_one_outbox_published_total",
    "all_in_one_outbox_failed_retryable_total",
    "all_in_one_outbox_max_retry_count",
    "all_in_one_outbox_oldest_pending_age_seconds",
}


def load_dashboard() -> dict:
    return json.loads((ROOT / "config" / "observability" / "outbox_dashboard.json").read_text(encoding="utf-8"))


def load_prometheus_dashboard_manifest() -> str:
    return (ROOT / "infra" / "kubernetes" / "base" / "outbox-dashboard.yaml").read_text(encoding="utf-8")


def test_outbox_dashboard_has_expected_identity_and_panels() -> None:
    dashboard = load_dashboard()

    assert dashboard["uid"] == "outbox-dispatcher"
    assert dashboard["title"] == "All-in-One - Outbox Dispatcher"
    assert dashboard["refresh"] == "30s"
    assert dashboard["time"] == {"from": "now-6h", "to": "now"}
    assert set(dashboard["tags"]) == {"all-in-one", "outbox", "operations"}

    panels = dashboard["panels"]
    assert len(panels) >= 8
    assert REQUIRED_PANEL_TITLES.issubset({panel["title"] for panel in panels})


def test_outbox_dashboard_mentions_required_metrics() -> None:
    dashboard = load_dashboard()

    expressions = {
        target["expr"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if isinstance(target, dict) and target.get("expr")
    }

    for metric in REQUIRED_METRICS:
        assert any(metric in expr for expr in expressions), metric


def test_outbox_dashboard_matches_worker_prometheus_metrics() -> None:
    dashboard = load_dashboard()
    dashboard_expressions = {
        target["expr"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if isinstance(target, dict) and target.get("expr")
    }
    worker_metrics = {
        line.split(" ", maxsplit=1)[0]
        for line in prometheus_metrics(OutboxMetrics()).splitlines()
        if line.startswith("all_in_one_outbox_")
    }
    dashboard_metrics = {
        metric
        for expr in dashboard_expressions
        for metric in worker_metrics
        if metric in expr
    }

    assert dashboard_metrics == worker_metrics
    assert all(any(metric in expr for metric in worker_metrics) for expr in dashboard_expressions)


def test_outbox_dashboard_is_materialized_as_kubernetes_configmap() -> None:
    manifest = load_prometheus_dashboard_manifest()

    assert "kind: ConfigMap" in manifest
    assert 'grafana_dashboard: "1"' in manifest
    assert "outbox-dispatcher-dashboard.json" in manifest
    assert "All-in-One - Outbox Dispatcher" in manifest
    assert "all_in_one_outbox_pending" in manifest
    assert "all_in_one_outbox_due" in manifest
