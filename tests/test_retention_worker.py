import json
from datetime import UTC, datetime
from uuid import uuid4

from modules.shared.retention_worker import (
    RetentionCandidate,
    RetentionPostgresSettings,
    anonymize_payload,
    candidate_from_postgres_row,
    decide_retention,
    decision_event_payload,
    process_candidates,
)

NOW = datetime(2026, 5, 31, 15, 0, tzinfo=UTC)


def candidate(**overrides: object) -> RetentionCandidate:
    data = {
        "module": "crm",
        "record_id": "lead-1",
        "resource_type": "leads",
        "subject_id": "user-1",
        "payload": {
            "name": "Pessoa",
            "email": "pessoa@example.com",
            "campaign": "local",
        },
        "legal_hold": [],
    }
    data.update(overrides)
    return RetentionCandidate.from_dict(data)


def test_anonymization_worker_redacts_sensitive_fields_and_keeps_business_context() -> (
    None
):
    decision = decide_retention(
        candidate(
            module="delivery",
            payload={"address": "Rua A", "route_id": "R-1", "customer_phone": "999"},
        ),
        "anonymization_worker_hourly",
        observed_at=NOW,
    )

    assert decision.status == "applied"
    assert decision.audit_event == "compliance.data.anonymized"
    assert decision.payload == {
        "address": "[anonymized]",
        "route_id": "R-1",
        "customer_phone": "[anonymized]",
    }
    assert decision.evidence["anonymization_method"] == "field_redaction"
    assert (
        decision.evidence["audit_event_id"]
        == "delivery:lead-1:anonymization_worker_hourly"
    )


def test_deletion_worker_emits_tombstone_and_receipt_hash() -> None:
    decision = decide_retention(
        candidate(module="vision", record_id="recording-1"),
        "deletion_worker_daily",
        observed_at=NOW,
    )

    assert decision.status == "applied"
    assert decision.audit_event == "compliance.data.deleted"
    assert decision.payload == {
        "deleted": True,
        "deleted_at": "2026-05-31T15:00:00+00:00",
    }
    assert len(decision.evidence["deletion_receipt_hash"]) == 64
    assert decision.evidence["record_selector_hash"]


def test_dry_run_keeps_payload_and_marks_decision_without_applying() -> None:
    original = {"name": "Pessoa", "email": "pessoa@example.com"}

    decision = decide_retention(
        candidate(payload=original),
        "deletion_worker_daily",
        dry_run=True,
        observed_at=NOW,
    )

    assert decision.status == "dry_run"
    assert decision.payload == original
    assert decision.audit_event == "compliance.data.deleted"


def test_legal_hold_blocks_destructive_or_anonymizing_actions() -> None:
    decision = decide_retention(
        candidate(
            module="finance", legal_hold=["ledger"], requested_action="delete_ledger"
        ),
        "deletion_worker_daily",
        observed_at=NOW,
    )

    assert decision.status == "blocked"
    assert decision.action == "legal_hold"
    assert decision.audit_event == "compliance.legal_hold.applied"
    assert decision.evidence["hold_reason"] == "ledger"


def test_forbidden_action_requires_legal_review_even_without_current_hold() -> None:
    blocked = decide_retention(
        candidate(module="health", requested_action="delete_medical_record"),
        "deletion_worker_daily",
        observed_at=NOW,
    )
    approved = decide_retention(
        candidate(
            module="health",
            requested_action="delete_medical_record",
            legal_review_approved=True,
        ),
        "deletion_worker_daily",
        observed_at=NOW,
    )

    assert blocked.status == "blocked"
    assert blocked.evidence["hold_reason"] == "legal_review_required"
    assert approved.status == "applied"
    assert approved.payload["deleted"] is True


def test_process_candidates_reuses_single_policy_timestamp_for_batch() -> None:
    decisions = process_candidates(
        [
            candidate(module="crm", record_id="lead-1"),
            candidate(module="bi", record_id="export-1"),
        ],
        "retention_review_daily",
        dry_run=True,
        observed_at=NOW,
    )

    assert [decision.status for decision in decisions] == ["dry_run", "dry_run"]
    assert {decision.evidence["job_run_id"] for decision in decisions} == {
        "retention_review_daily:20260531T150000Z"
    }


def test_anonymize_payload_handles_nested_values() -> None:
    payload = {
        "profile": {"document_number": "123", "city": "SP"},
        "items": [{"phone": "999", "sku": "A"}],
    }

    assert anonymize_payload(payload) == {
        "profile": {"document_number": "[anonymized]", "city": "SP"},
        "items": [{"phone": "[anonymized]", "sku": "A"}],
    }


def test_candidate_accepts_jsonl_style_payload() -> None:
    raw = json.loads(
        '{"module":"api_hub","record_id":"client-1","subject_id":"u","payload":{"api_key":"secret"},"legal_hold":[]}'
    )

    parsed = RetentionCandidate.from_dict(raw)

    assert parsed.module == "api_hub"
    assert parsed.resource_type == "resource"
    assert parsed.payload == {"api_key": "secret"}


def test_postgres_candidate_row_maps_to_retention_candidate() -> None:
    record_id = uuid4()
    subject_id = uuid4()

    parsed = candidate_from_postgres_row(
        {
            "module": "crm",
            "resource_id": record_id,
            "resource_type": "leads",
            "subject_id": subject_id,
            "payload": {"email": "lead@example.com"},
            "legal_hold": ["lead_origin_proof"],
            "requested_action": "delete_or_anonymize_opted_out_leads",
            "legal_review_approved": True,
        }
    )

    assert parsed.record_id == str(record_id)
    assert parsed.subject_id == str(subject_id)
    assert parsed.legal_hold == ["lead_origin_proof"]
    assert parsed.legal_review_approved is True


def test_decision_event_payload_exposes_only_operational_evidence() -> None:
    decision = decide_retention(
        candidate(module="crm"), "retention_review_daily", observed_at=NOW
    )

    payload = decision_event_payload(decision, "candidate-1")

    assert payload["candidate_id"] == "candidate-1"
    assert payload["decision_status"] == "reviewed"
    assert payload["evidence"]["policy_version"]
    assert payload["evidence"]["record_selector_hash"]
    assert "payload" not in payload
    assert "email" not in json.dumps(payload)


def test_postgres_settings_reads_retention_environment(monkeypatch) -> None:
    monkeypatch.setenv("ALL_IN_ONE_RETENTION_POSTGRES_DSN", "postgresql://retention")
    monkeypatch.setenv("ALL_IN_ONE_RETENTION_BATCH_SIZE", "5")

    settings = RetentionPostgresSettings.from_environment()

    assert settings.postgres_dsn == "postgresql://retention"
    assert settings.batch_size == 5
