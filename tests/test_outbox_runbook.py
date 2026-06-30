from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_operations() -> str:
    return (ROOT / "docs" / "OPERATIONS.md").read_text(encoding="utf-8")


def test_outbox_runbook_documents_triage_recovery_and_safety() -> None:
    operations = load_operations()
    start = operations.index("## Outbox")
    end = operations.index("## Retencao LGPD")
    outbox_section = operations[start:end]

    assert "### Runbook de incidentes" in outbox_section
    assert "OutboxPublishStalled" in outbox_section
    assert "OutboxBacklogHigh" in outbox_section
    assert "OutboxDueHigh" in outbox_section
    assert "OutboxRetryFailuresHigh" in outbox_section
    assert "OutboxOldestPendingTooOld" in outbox_section
    assert "audit.event_deliveries" in outbox_section
    assert "retry_count" in outbox_section
    assert "next_retry_at" in outbox_section
    assert "last_error_type" in outbox_section
    assert "publisher_confirmed" in outbox_section
    assert "payload sensivel" in outbox_section
