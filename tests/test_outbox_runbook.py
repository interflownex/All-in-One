from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_outbox_alerts_point_to_actionable_runbook() -> None:
    alerts = json.loads((ROOT / "config/observability/outbox_alerts.json").read_text(encoding="utf-8"))
    operations = (ROOT / "docs/OPERATIONS.md").read_text(encoding="utf-8")

    assert alerts["runbook"] == "docs/OPERATIONS.md#outbox"
    assert "### Runbook de incidentes da outbox" in operations
    for alert_name in alerts["alerts"]:
        assert alert_name in operations


def test_outbox_runbook_preserves_sensitive_payload_boundary() -> None:
    operations = (ROOT / "docs/OPERATIONS.md").read_text(encoding="utf-8")

    required_evidence = {
        "pending_count",
        "due_count",
        "oldest_pending_age_seconds",
        "failed_retryable_delta",
        "published_delta",
        "event_selector_hash",
        "last_error_type",
    }
    for evidence in required_evidence:
        assert evidence in operations
    assert "logs do dispatcher sem payload" in operations
    assert "nao alterar eventos manualmente" in operations
    assert "deduplicar por `event_id`" in operations
