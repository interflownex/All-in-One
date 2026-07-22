from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID

import pika
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

SAFE_PAYLOAD_FIELDS: dict[str, frozenset[str]] = {
    "api_clients": frozenset({"client_name", "scopes"}),
    "carriers": frozenset({"coverage", "name"}),
    "companies": frozenset({"legal_name"}),
    "datasets": frozenset({"name", "refresh_mode"}),
    "delivery_requests": frozenset({"insurance_required", "service_type"}),
    "fiscal_documents": frozenset({"document_type"}),
    "folders": frozenset({"classification"}),
    "processes": frozenset({"name", "published", "version"}),
    "providers": frozenset({"category"}),
    "rides": frozenset({"vehicle_type"}),
    "roles": frozenset({"is_system", "name"}),
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
    "job_postings": frozenset(
        {"company_id", "title", "employment_type", "workplace_model"}
    ),
    "applications": frozenset({"job_posting_id", "resume_id"}),
    "resume_access_logs": frozenset({"resume_id", "business_id"}),
    "stores": frozenset({"name"}),
    "wallets": frozenset({"wallet_type"}),
    "warehouses": frozenset({"name"}),
    "valley_gold_ledger_entries": frozenset(
        {
            "merchant_business_id",
            "entry_type",
            "amount_gold_delta",
            "reference_type",
            "reference_id",
        }
    ),
    "pepita_grants": frozenset(
        {
            "order_id",
            "customer_user_id",
            "merchant_business_id",
            "pepitas",
            "grant_mode",
        }
    ),
    "discount_quotes": frozenset(
        {
            "catalog_product_id",
            "selected_percent",
            "pepitas_required",
            "discount_brl",
            "final_price_brl",
            "visibility_rule",
        }
    ),
    "valley_catalog_offers": frozenset(
        {
            "offer_id",
            "offer_type",
            "consumer_category",
            "title",
            "short_description",
            "consumer_friendly_label",
            "source_module",
            "source_resource_type",
            "source_entity_id",
            "business_id",
            "availability_status",
            "publication_status",
            "price_brl",
            "price_type",
            "price_amount",
            "currency",
            "benefits",
            "rewards",
            "region_label",
            "service_radius_km",
            "consumer_action",
            "primary_action_label",
            "company_type",
            "company_type_label",
            "company_category",
            "business_activity_id",
            "business_activity_label",
            "category_id",
            "availability_type",
            "stock_quantity",
            "service_duration_minutes",
            "compliance_status",
            "verified_seller",
        }
    ),
    "catalog_offers": frozenset(
        {
            "offer_id",
            "offer_type",
            "offer_type_label",
            "consumer_category",
            "title",
            "short_description",
            "consumer_friendly_label",
            "source_module",
            "source_resource_type",
            "source_entity_id",
            "business_id",
            "availability_status",
            "publication_status",
            "price_brl",
            "price_type",
            "price_amount",
            "currency",
            "benefits",
            "rewards",
            "region_label",
            "service_radius_km",
            "consumer_action",
            "primary_action_label",
            "company_type",
            "company_type_label",
            "company_category",
            "business_activity_id",
            "business_activity_label",
            "business_activity_consumer_label",
            "seller_context_label",
            "consumer_filter_text",
            "category_id",
            "availability_type",
            "stock_quantity",
            "service_duration_minutes",
            "compliance_status",
            "verified_seller",
        }
    ),
    "retention_decisions": frozenset(
        {
            "candidate_id",
            "module",
            "resource_type",
            "action",
            "decision_status",
            "job_name",
            "evidence",
        }
    ),
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
    retry_base_seconds: int = 5
    retry_max_seconds: int = 300

    @classmethod
    def from_environment(cls) -> OutboxSettings:
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
            poll_seconds=max(
                0.1, float(os.getenv("ALL_IN_ONE_OUTBOX_POLL_SECONDS", "1"))
            ),
            retry_base_seconds=max(
                1, int(os.getenv("ALL_IN_ONE_OUTBOX_RETRY_BASE_SECONDS", "5"))
            ),
            retry_max_seconds=max(
                1, int(os.getenv("ALL_IN_ONE_OUTBOX_RETRY_MAX_SECONDS", "300"))
            ),
        )


@dataclass
class DispatchSummary:
    selected: int = 0
    published: int = 0
    failed: int = 0


@dataclass(frozen=True)
class OutboxMetrics:
    pending: int = 0
    due: int = 0
    published: int = 0
    failed_retryable: int = 0
    max_retry_count: int = 0
    oldest_pending_age_seconds: float = 0.0


def publication_message(event: dict[str, Any]) -> dict[str, Any]:
    stored_payload = event.get("payload") or {}
    is_envelope = (
        isinstance(stored_payload, dict)
        and "event_id" in stored_payload
        and "payload" in stored_payload
    )
    source_payload = (
        stored_payload.get("payload") or {} if is_envelope else stored_payload
    )
    safe_fields = SAFE_PAYLOAD_FIELDS.get(event["aggregate_type"], frozenset())
    message = {
        "event_id": str(event["id"]),
        "routing_key": event["routing_key"],
        "schema_version": event["schema_version"],
        "aggregate_type": event["aggregate_type"],
        "aggregate_id": str(event["aggregate_id"]),
        "correlation_id": str(event["correlation_id"]),
        "entity_id": str(event["entity_id"]) if event.get("entity_id") else None,
        "payload": {
            key: source_payload[key]
            for key in sorted(safe_fields)
            if key in source_payload
        },
        "occurred_at": stored_payload.get("occurred_at")
        if is_envelope
        else event["created_at"].isoformat(),
    }
    if is_envelope:
        message.update(
            {
                "producer": stored_payload.get("producer"),
                "idempotency_key": stored_payload.get("idempotency_key"),
                "causation_id": stored_payload.get("causation_id"),
                "tenant_id": stored_payload.get("tenant_id"),
                "origin": stored_payload.get("origin"),
                "retention": stored_payload.get("retention"),
                "replay": stored_payload.get("replay"),
                "backward_compatibility": stored_payload.get("backward_compatibility"),
            }
        )
    return message


def prometheus_metrics(metrics: OutboxMetrics) -> str:
    values = {
        "all_in_one_outbox_pending": metrics.pending,
        "all_in_one_outbox_due": metrics.due,
        "all_in_one_outbox_published_total": metrics.published,
        "all_in_one_outbox_failed_retryable_total": metrics.failed_retryable,
        "all_in_one_outbox_max_retry_count": metrics.max_retry_count,
        "all_in_one_outbox_oldest_pending_age_seconds": metrics.oldest_pending_age_seconds,
    }
    return "".join(f"{name} {value}\n" for name, value in values.items())


def retry_observation(
    event: dict[str, Any],
    error: Exception,
    settings: OutboxSettings,
    now: datetime | None = None,
) -> dict[str, Any]:
    metadata = event.get("metadata") or {}
    retry_count = int(metadata.get("retry_count") or 0) + 1
    delay_seconds = min(
        settings.retry_max_seconds,
        settings.retry_base_seconds * (2 ** (retry_count - 1)),
    )
    observed_at = now or datetime.now(UTC)
    next_retry_at = observed_at + timedelta(seconds=delay_seconds)
    return {
        "retry_count": retry_count,
        "retry_delay_seconds": delay_seconds,
        "next_retry_at": next_retry_at.isoformat(),
        "last_error_type": type(error).__name__,
        "last_error": str(error)[:500],
        "retryable": True,
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
        self._rabbit_connection = pika.BlockingConnection(
            pika.URLParameters(self.settings.rabbitmq_url)
        )
        self._channel = self._rabbit_connection.channel()
        self._channel.exchange_declare(
            exchange=self.settings.exchange, exchange_type="topic", durable=True
        )
        self._channel.confirm_delivery()
        return self._channel

    def _publish_event(self, event: dict[str, Any]) -> dict[str, Any]:
        channel = self._publisher_channel()
        message_id = str(event["id"])
        accepted = channel.basic_publish(
            exchange=self.settings.exchange,
            routing_key=event["routing_key"],
            body=json.dumps(
                publication_message(event), default=_json_default, separators=(",", ":")
            ).encode("utf-8"),
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

    def collect_metrics(self) -> OutboxMetrics:
        with psycopg.connect(
            self.settings.postgres_dsn, row_factory=dict_row
        ) as connection:
            row = connection.execute(
                """SELECT
                       COUNT(*) FILTER (WHERE status = 'pending' AND published_at IS NULL) AS pending,
                       COUNT(*) FILTER (
                           WHERE status = 'pending'
                             AND published_at IS NULL
                             AND (
                                 metadata->>'next_retry_at' IS NULL
                                 OR (metadata->>'next_retry_at')::timestamptz <= NOW()
                             )
                       ) AS due,
                       COUNT(*) FILTER (WHERE status = 'published' OR published_at IS NOT NULL) AS published,
                       COALESCE(MAX((metadata->>'retry_count')::integer), 0) AS max_retry_count,
                       COALESCE(
                           EXTRACT(EPOCH FROM (NOW() - MIN(created_at) FILTER (WHERE status = 'pending' AND published_at IS NULL))),
                           0
                       ) AS oldest_pending_age_seconds
                   FROM audit.domain_events"""
            ).fetchone()
            failed = connection.execute(
                """SELECT COUNT(*) AS failed_retryable
                   FROM audit.event_deliveries
                   WHERE delivery_status = 'failed_retryable'"""
            ).fetchone()
        return OutboxMetrics(
            pending=int(row["pending"] or 0),
            due=int(row["due"] or 0),
            published=int(row["published"] or 0),
            failed_retryable=int(failed["failed_retryable"] or 0),
            max_retry_count=int(row["max_retry_count"] or 0),
            oldest_pending_age_seconds=float(row["oldest_pending_age_seconds"] or 0),
        )

    def publish_batch(self) -> DispatchSummary:
        summary = DispatchSummary()
        with psycopg.connect(
            self.settings.postgres_dsn, row_factory=dict_row
        ) as connection:
            for _ in range(self.settings.batch_size):
                stop_after_failure = False
                with connection.transaction():
                    event = connection.execute(
                        """SELECT *
                           FROM audit.domain_events
                           WHERE published_at IS NULL
                             AND status = 'pending'
                             AND (
                                 metadata->>'next_retry_at' IS NULL
                                 OR (metadata->>'next_retry_at')::timestamptz <= NOW()
                             )
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
                        response_metadata = retry_observation(
                            event, error, self.settings
                        )
                        connection.execute(
                            """INSERT INTO audit.event_deliveries
                               (user_id, event_id, destination, delivery_status, response_metadata, created_by)
                               VALUES (%s, %s, %s, 'failed_retryable', %s, %s)""",
                            (
                                event["user_id"],
                                event["id"],
                                self.settings.exchange,
                                Jsonb(response_metadata),
                                event["created_by"],
                            ),
                        )
                        connection.execute(
                            """UPDATE audit.domain_events
                               SET metadata = COALESCE(metadata, '{}'::jsonb) || %s
                               WHERE id = %s""",
                            (Jsonb(response_metadata), event["id"]),
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
