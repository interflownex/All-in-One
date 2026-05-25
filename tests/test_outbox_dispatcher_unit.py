from datetime import datetime, timezone
from uuid import uuid4

from modules.shared.outbox_dispatcher import publication_message


def test_jobs_document_publication_uses_safe_allowlist() -> None:
    message = publication_message(
        {
            "id": uuid4(),
            "routing_key": "jobs.resume.ctps_imported",
            "schema_version": 1,
            "aggregate_type": "resume_documents",
            "aggregate_id": uuid4(),
            "correlation_id": uuid4(),
            "entity_id": None,
            "created_at": datetime.now(timezone.utc),
            "payload": {
                "resume_id": str(uuid4()),
                "document_type": "ctps_digital_pdf",
                "sha256": "hash",
                "storage_key": "private-key",
                "raw_document_text": "private text",
            },
        }
    )
    assert message["payload"]["sha256"] == "hash"
    assert "storage_key" not in message["payload"]
    assert "raw_document_text" not in message["payload"]


def test_unknown_domain_publishes_no_unreviewed_payload() -> None:
    message = publication_message(
        {
            "id": uuid4(),
            "routing_key": "health.record.created",
            "schema_version": 1,
            "aggregate_type": "medical_records",
            "aggregate_id": uuid4(),
            "correlation_id": uuid4(),
            "entity_id": None,
            "created_at": datetime.now(timezone.utc),
            "payload": {"patient_record": "must not publish"},
        }
    )
    assert message["payload"] == {}
