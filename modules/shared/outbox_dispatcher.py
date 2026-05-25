from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID

import pika
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


SAFE_PAYLOAD_FIELDS: dict[str, frozenset[str]] = {
    "resumes": frozenset({"recruiter_visibility"}),
    "resume_documents": frozenset(
        {
            "resume_id",
            "document_type",
            "sha256",
            "evidence_status",
            "official_verification_status",
            "extraction_status",
        }
    ),
    "employment_records": frozenset(
        {
            "resume_id",
            "source_document_id",
            "source_type",
            "evidence_status",
            "official_verification_status",
            "is_informal_activity",
            "visible_to_recruiter",
        }
    ),
    "job_postings": frozenset({"company_id", "title", "employment_type", "workplace_model"}),
    "applications": frozenset({"job_posting_id", "resume_id"}),
    "resume_access_logs": frozenset({"resume_id", "business_id"}),
}


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime, UUID)):
        return value.isoformat() if hasattr(value, "isoformat") else str(value)
    return str(value)


@dataclass(frozen=True)
class OutboxSettings:
    postgres_dsn: str
    rabbitmq_url: str
    exchange: str = "all-in-one.domain"
    batch_size: int = 100
    poll_seconds: float = 1.0

    @classmethod
    def from_environment(cls) -> "OutboxSettings":
        postgres_dsn = (
            os.getenv("ALL_IN_ONE_OUTBOX_POSTGRES_DSN")
            or os.getenv("ALL_IN_ONE_JOBS_POSTGRES_DSN")
            or os.getenv("ALL_IN_ONE_POSTGRES_DSN")
        )
        rabbitmq_url = os.getenv("ALL_IN_ONE_RABBITMQ_URL")
        if not postgres_dsn:
            raise RuntimeError("ALL_IN_ONE_OUTBOX_POSTGRES_DSN nao configurada.")
        if not rabbitmq_url:
            raise RuntimeError("ALL_IN_ONE_RABBITMQ_URL nao configurada.")
        return cls(
            postgres_dsn=postgres_dsn,
            rabbitmq_url=rabbitmq_url,
            exchange=os.getenv("ALL_IN_ONE_OUTBOX_EXCHANGE", "all-in-one.domain"),
            batch_size=max(1, int(os.getenv("ALL_IN_ONE_OUTBOX_BATCH_SIZE", "100"))),
            poll_seconds=max(0.1, float(os.getenv("ALL_IN_ONE_OUTBOX_POLL_SECONDS", "1"))),
        )


@dataclass
class DispatchSummary:
    selected: int = 0
    published: int = 0
    failed: int = 0


def publication_message(event: dict[str, Any]) -> dict[str, Any]:
    source_payload = event.get("payload") or {}
    safe_fields = SAFE_PAYLOAD_FIELDS.get(event["aggregate_type"], frozenset())
    return {
        "event_id": str(event["id"]),
        "routing_key": event["routing_key"],
        "schema_version": event["schema_version"],
        "aggregate_type": event["aggregate_type"],
        "aggregate_id": str(event["aggregate_id"]),
        "correlation_id": str(event["correlation_id"]),
        "entity_id": str(event["entity_id"]) if event.get("entity_id") else None,
        "payload": {key: source_payload[key] for key in sorted(safe_fields) if key in source_payload},
        "occurred_at": event["created_at"].isoformat(),
    }


class OutboxDispatcher:
    """Publishes committed domain events and records immutable delivery attempts."""

    def __init__(self, settings: OutboxSettings) -> None:
        self.settings = settings
        self._rabbit_connection: pika.BlockingConnection | None = None
        self._channel: pika.adapters.blocking_connection.BlockingChannel | None = None

    def close(self) -> None:
        if self._rabbit_connection and self._rabbit_connection.is_open:
            self._rabbit_connection.close()
        self._rabbit_connection = None
        self._channel = None

    def _publisher_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if self._channel and self._channel.is_open:
            return self._channel
        self._rabbit_connection = pika.BlockingConnection(pika.URLParameters(self.settings.rabbitmq_url))
        self._channel = self._rabbit_connection.channel()
        self._channel.exchange_declare(exchange=self.settings.exchange, exchange_type="topic", durable=True)
        self._channel.confirm_delivery()
        return self._channel

    def _publish_event(self, event: dict[str, Any]) -> dict[str, Any]:
        channel = self._publisher_channel()
        message_id = str(event["id"])
        accepted = channel.basic_publish(
            exchange=self.settings.exchange,
            routing_key=event["routing_key"],
            body=json.dumps(publication_message(event), default=_json_default, separators=(",", ":")).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                content_encoding="utf-8",
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=message_id,
                correlation_id=str(event["correlation_id"]),
                type=event["routing_key"],
                headers={"schema_version": event["schema_version"]},
            ),
        )
        if accepted is False:
            raise RuntimeError("RabbitMQ rejeitou confirmacao de publicacao.")
        return {
            "exchange": self.settings.exchange,
            "routing_key": event["routing_key"],
            "message_id": message_id,
            "publisher_confirmed": True,
        }

    def publish_batch(self) -> DispatchSummary:
        summary = DispatchSummary()
        with psycopg.connect(self.settings.postgres_dsn, row_factory=dict_row) as connection:
            for _ in range(self.settings.batch_size):
                stop_after_failure = False
                with connection.transaction():
                    event = connection.execute(
                        """SELECT *
                           FROM audit.domain_events
                           WHERE published_at IS NULL AND status = 'pending'
                           ORDER BY created_at, id
                           FOR UPDATE SKIP LOCKED
                           LIMIT 1"""
                    ).fetchone()
                    if event is None:
                        break
                    summary.selected += 1
                    try:
                        response_metadata = self._publish_event(event)
                    except Exception as error:
                        self.close()
                        connection.execute(
                            """INSERT INTO audit.event_deliveries
                               (user_id, event_id, destination, delivery_status, response_metadata, created_by)
                               VALUES (%s, %s, %s, 'failed_retryable', %s, %s)""",
                            (
                                event["user_id"],
                                event["id"],
                                self.settings.exchange,
                                Jsonb({"error_type": type(error).__name__, "retryable": True}),
                                event["created_by"],
                            ),
                        )
                        summary.failed += 1
                        stop_after_failure = True
                    else:
                        connection.execute(
                            """UPDATE audit.domain_events
                               SET published_at = NOW(), status = 'published'
                               WHERE id = %s AND published_at IS NULL""",
                            (event["id"],),
                        )
                        connection.execute(
                            """INSERT INTO audit.event_deliveries
                               (user_id, event_id, destination, delivery_status, response_metadata, created_by)
                               VALUES (%s, %s, %s, 'publisher_confirmed', %s, %s)""",
                            (
                                event["user_id"],
                                event["id"],
                                self.settings.exchange,
                                Jsonb(response_metadata),
                                event["created_by"],
                            ),
                        )
                        summary.published += 1
                if stop_after_failure:
                    break
        return summary
