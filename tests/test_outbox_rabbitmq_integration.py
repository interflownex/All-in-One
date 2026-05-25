import json
import os
from uuid import uuid4

import pika
import psycopg
import pytest
from psycopg.types.json import Jsonb

from modules.shared.outbox_dispatcher import OutboxDispatcher, OutboxSettings


POSTGRES_DSN = os.getenv("ALL_IN_ONE_OUTBOX_POSTGRES_TEST_DSN")
RABBITMQ_URL = os.getenv("ALL_IN_ONE_RABBITMQ_TEST_URL")
pytestmark = pytest.mark.skipif(
    not POSTGRES_DSN or not RABBITMQ_URL,
    reason="DSNs PostgreSQL e RabbitMQ de integracao nao configuradas.",
)


def create_event(payload: dict) -> str:
    event_id = uuid4()
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """INSERT INTO audit.domain_events
               (id, routing_key, aggregate_type, aggregate_id, payload)
               VALUES (%s, 'jobs.resume.ctps_imported', 'resume_documents', %s, %s)""",
            (event_id, uuid4(), Jsonb(payload)),
        )
    return str(event_id)


def test_dispatcher_publishes_minimized_payload_once_and_records_delivery() -> None:
    exchange = f"all-in-one.test.{uuid4()}"
    settings = OutboxSettings(POSTGRES_DSN, RABBITMQ_URL, exchange=exchange, batch_size=100)
    event_id = create_event(
        {
            "resume_id": str(uuid4()),
            "document_type": "ctps_digital_pdf",
            "sha256": "safe-hash",
            "evidence_status": "validated_by_document_import",
            "official_verification_status": "not_officially_verified",
            "extraction_status": "completed",
            "storage_key": "must-not-leave-private-vault",
            "raw_document_text": "must-not-leave-private-vault",
        }
    )
    rabbit = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = rabbit.channel()
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    queue = channel.queue_declare(queue="", exclusive=True).method.queue
    channel.queue_bind(exchange=exchange, queue=queue, routing_key="jobs.#")
    dispatcher = OutboxDispatcher(settings)
    try:
        first = dispatcher.publish_batch()
        second = dispatcher.publish_batch()
        assert first.published >= 1
        assert first.failed == 0
        assert second.published == 0
        messages: dict[str, dict] = {}
        while True:
            method, _, body = channel.basic_get(queue=queue, auto_ack=True)
            if method is None:
                break
            message = json.loads(body)
            messages[message["event_id"]] = message
        message = messages[event_id]
        assert message["payload"]["sha256"] == "safe-hash"
        assert "storage_key" not in message["payload"]
        assert "raw_document_text" not in message["payload"]
        with psycopg.connect(POSTGRES_DSN) as connection:
            status = connection.execute(
                "SELECT status, published_at FROM audit.domain_events WHERE id = %s", (event_id,)
            ).fetchone()
            assert status[0] == "published"
            assert status[1] is not None
            assert connection.execute(
                """SELECT COUNT(*) FROM audit.event_deliveries
                   WHERE event_id = %s AND delivery_status = 'publisher_confirmed'""",
                (event_id,),
            ).fetchone()[0] == 1
    finally:
        dispatcher.close()
        rabbit.close()


def test_dispatcher_leaves_failed_event_pending_for_retry() -> None:
    event_id = create_event({"resume_id": str(uuid4()), "sha256": "retry-hash"})
    dispatcher = OutboxDispatcher(
        OutboxSettings(POSTGRES_DSN, "amqp://guest:guest@127.0.0.1:1/%2F", exchange="all-in-one.unreachable", batch_size=1)
    )
    try:
        result = dispatcher.publish_batch()
        assert result.failed == 1
        with psycopg.connect(POSTGRES_DSN) as connection:
            event = connection.execute(
                "SELECT status, published_at FROM audit.domain_events WHERE id = %s", (event_id,)
            ).fetchone()
            assert event == ("pending", None)
            assert connection.execute(
                """SELECT COUNT(*) FROM audit.event_deliveries
                   WHERE event_id = %s AND delivery_status = 'failed_retryable'""",
                (event_id,),
            ).fetchone()[0] == 1
    finally:
        dispatcher.close()
