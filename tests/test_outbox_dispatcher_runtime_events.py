from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pika
import psycopg
import pytest
from psycopg.rows import dict_row

from modules.shared.domain_rules import event_for_create, rule_for
from modules.shared.outbox_dispatcher import OutboxDispatcher, OutboxSettings, SAFE_PAYLOAD_FIELDS, publication_message
from modules.shared.runtime import create_module_app
from all_in_one_test_support.runtime_event_generation import (
    generate_payload,
    get_evented_transition,
    get_primary_resource,
    load_module_catalog,
    resolve_entity_id,
)

POSTGRES_DSN = (
    os.getenv("ALL_IN_ONE_OUTBOX_POSTGRES_TEST_DSN")
    or os.getenv("ALL_IN_ONE_POSTGRES_MATRIX_DSN")
    or os.getenv("ALL_IN_ONE_JOBS_POSTGRES_TEST_DSN")
)
RABBITMQ_URL = os.getenv("ALL_IN_ONE_RABBITMQ_TEST_URL")


class _FakeResult:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def fetchone(self) -> dict[str, object] | None:
        return self._row


class _FakeTransaction:
    def __init__(self, connection: "_FakeConnection") -> None:
        self._connection = connection

    def __enter__(self) -> "_FakeConnection":
        return self._connection

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


class _FakeConnection:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows
        self._current: dict[str, object] | None = None
        self.published_rows: list[dict[str, object]] = []
        self.deliveries: list[dict[str, object]] = []

    def __enter__(self) -> "_FakeConnection":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def transaction(self) -> _FakeTransaction:
        return _FakeTransaction(self)

    def execute(self, sql, params=None) -> _FakeResult:
        query = str(sql)
        if "FROM audit.domain_events" in query and "FOR UPDATE SKIP LOCKED" in query:
            while self._rows:
                candidate = self._rows.pop(0)
                if candidate.get("published_at") is None and candidate.get("status") == "pending":
                    self._current = candidate
                    return _FakeResult(candidate)
            self._current = None
            return _FakeResult(None)

        if "INSERT INTO audit.event_deliveries" in query:
            delivery_status = "publisher_confirmed" if "publisher_confirmed" in query else "failed_retryable"
            self.deliveries.append(
                {
                    "delivery_status": delivery_status,
                    "params": params,
                }
            )
            return _FakeResult(None)

        if "UPDATE audit.domain_events" in query:
            if self._current is not None:
                if "published_at = NOW()" in query:
                    published_row = dict(self._current)
                    published_row["published_at"] = datetime.now(UTC)
                    published_row["status"] = "published"
                    self.published_rows.append(published_row)
                elif params and len(params) == 2:
                    metadata, event_id = params
                    if str(self._current["id"]) == str(event_id):
                        current_metadata = dict(self._current.get("metadata") or {})
                        current_metadata.update(dict(metadata))
                        self._current["metadata"] = current_metadata
            return _FakeResult(None)

        raise AssertionError(f"SQL inesperado no fake dispatcher: {query}")


class _FakeChannel:
    def __init__(self) -> None:
        self.messages: list[dict[str, object]] = []

    def basic_publish(self, exchange, routing_key, body, properties):
        self.messages.append(
            {
                "exchange": exchange,
                "routing_key": routing_key,
                "body": body,
                "properties": properties,
            }
        )
        return True


def _runtime_store(module_slug: str):
    return create_module_app(module_slug).extra["store"]


def _find_event(store, routing_key: str, resource_id: str | None = None) -> dict[str, object]:
    if POSTGRES_DSN and resource_id is not None:
        with psycopg.connect(POSTGRES_DSN, row_factory=dict_row) as connection:
            event = connection.execute(
                """SELECT *
                   FROM audit.domain_events
                   WHERE routing_key = %s AND aggregate_id = %s
                   ORDER BY created_at DESC
                   LIMIT 1""",
                (routing_key, resource_id),
            ).fetchone()
            if event is not None:
                return event

    for event in store.outbox():
        if event["routing_key"] == routing_key and (resource_id is None or str(event.get("resource_id")) == str(resource_id)):
            return event
    suffix = f" e resource_id {resource_id}" if resource_id else ""
    raise AssertionError(f"Evento {routing_key}{suffix} nao encontrado no outbox de teste.")


def _to_dispatch_row(resource: dict[str, object], event: dict[str, object]) -> dict[str, object]:
    payload = event["payload"]
    if isinstance(payload, str):
        payload = json.loads(payload)
    return {
        "id": UUID(str(event["id"])),
        "routing_key": event["routing_key"],
        "schema_version": 1,
        "aggregate_type": resource["resource_type"],
        "aggregate_id": UUID(str(resource["id"])),
        "user_id": UUID(str(event["user_id"])),
        "entity_id": UUID(str(resource["entity_id"])) if resource.get("entity_id") else None,
        "actor_user_id": UUID(str(event["actor_user_id"])),
        "correlation_id": UUID(str(event["correlation_id"])),
        "payload": dict(payload),
        "status": "pending",
        "metadata": {},
        "created_at": datetime.fromisoformat(str(event["created_at"])),
        "published_at": None,
        "created_by": UUID(str(event["actor_user_id"])),
    }


def _normalize_runtime_seed_payload(
    module_slug: str,
    payload: dict[str, object],
    user_id: str,
    anchors: dict[str, str] | None = None,
) -> dict[str, object]:
    normalized = dict(payload)
    anchors = anchors or {}
    if "email" in normalized:
        normalized["email"] = f"seed-{user_id.replace('-', '')[:12]}@all-in-one.test"

    if module_slug == "identity":
        normalized.setdefault("cpf_document", normalized.get("document_cpf") or f"CPF-{uuid4().hex[:12]}")
        normalized.setdefault("document_cpf", normalized["cpf_document"])
        normalized.setdefault("birth_date", "1990-01-01")
        normalized.setdefault("phone_e164", f"+55{str(int(user_id.replace('-', '')[:10], 16))[-10:]}")
        normalized.setdefault("face_hash", f"face-{user_id}")
        normalized.setdefault("liveness_score", 0.9999)
        normalized.setdefault("terms_accepted_at", datetime.now(UTC).isoformat())
        normalized.setdefault("lgpd_consent_at", datetime.now(UTC).isoformat())
    elif module_slug == "business":
        normalized["cnpj"] = f"{uuid4().int % 10**14:014d}"
        normalized["root_cnpj"] = normalized["cnpj"][:8]
    elif module_slug == "api_hub":
        normalized.setdefault("client_id_hash", uuid4().hex)
        normalized.setdefault("secret_reference", f"secret-{uuid4().hex[:8]}")

    for key in list(normalized):
        if key == "user_id" or key.endswith("_user_id"):
            normalized[key] = user_id
        elif key in {"company_id", "business_id", "merchant_business_id"} and anchors.get("company_id"):
            normalized[key] = anchors["company_id"]
        elif key == "wallet_id" and anchors.get("wallet_id"):
            normalized[key] = anchors["wallet_id"]
        elif key == "resume_id" and anchors.get("resume_id"):
            normalized[key] = anchors["resume_id"]
    return normalized


def _seed_runtime_event_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    shared_user_id: str | None = None
    anchors: dict[str, str] = {}

    for module in load_module_catalog()["modules"]:
        module_slug = module["slug"]
        primary_resource = get_primary_resource(module_slug)
        if not primary_resource:
            continue

        try:
            rule = rule_for(module_slug, primary_resource)
        except Exception:
            continue

        store = _runtime_store(module_slug)
        creator_user_id = shared_user_id or str(uuid4())
        payload = _normalize_runtime_seed_payload(module_slug, generate_payload(rule, creator_user_id), creator_user_id, anchors)
        entity_id = resolve_entity_id(payload)
        if module_slug == "riders" and anchors.get("company_id"):
            entity_id = anchors["company_id"]
        if entity_id is None and anchors.get("company_id"):
            entity_id = anchors["company_id"]
        expected_create_routing_key = event_for_create(module_slug, primary_resource)
        created = store.create(
            primary_resource,
            creator_user_id,
            entity_id,
            rule.initial_status,
            payload,
            creator_user_id,
            rule.unique_fields,
            expected_create_routing_key,
            None,
        )
        create_event = _find_event(store, expected_create_routing_key, created["id"])
        rows.append(_to_dispatch_row(created, create_event))
        if module_slug == "identity" and shared_user_id is None:
            shared_user_id = str(created["id"])
        if module_slug == "business" and primary_resource == "companies":
            anchors["company_id"] = str(created["id"])
        elif module_slug == "finance" and primary_resource == "wallets":
            anchors["wallet_id"] = str(created["id"])
        elif module_slug == "marketplace" and primary_resource == "stores":
            anchors["store_id"] = str(created["id"])
        elif module_slug == "jobs" and primary_resource == "resumes":
            anchors["resume_id"] = str(created["id"])

        evented_transition = get_evented_transition(rule)
        if not evented_transition:
            continue

        transition_name, transition = evented_transition
        updated = store.update(
            created,
            dict(created["payload"]),
            transition.target,
            creator_user_id,
            transition_name,
            transition.event,
        )
        transition_event = _find_event(store, transition.event, updated["id"])
        rows.append(_to_dispatch_row(updated, transition_event))

    return sorted(rows, key=lambda row: (row["created_at"], str(row["id"])))


def test_dispatcher_publishes_real_runtime_events_with_safe_payload(monkeypatch) -> None:
    rows = _seed_runtime_event_rows()
    fake_connection = _FakeConnection([dict(row) for row in rows])
    fake_channel = _FakeChannel()
    settings = OutboxSettings(
        postgres_dsn="postgresql://dispatcher-runtime-test",
        rabbitmq_url="amqp://dispatcher-runtime-test",
        exchange="all-in-one.runtime.test",
        batch_size=100,
    )
    dispatcher = OutboxDispatcher(settings)
    dispatcher._publisher_channel = lambda: fake_channel  # type: ignore[method-assign]
    import modules.shared.outbox_dispatcher as dispatcher_module

    monkeypatch.setattr(dispatcher_module.psycopg, "connect", lambda *args, **kwargs: fake_connection)

    summary = dispatcher.publish_batch()

    assert summary.selected == len(rows)
    assert summary.published == len(rows)
    assert summary.failed == 0
    assert len(fake_channel.messages) == len(rows)
    assert len(fake_connection.deliveries) == len(rows)
    assert len(fake_connection.published_rows) == len(rows)

    published_by_event_id = {
        UUID(message["properties"].message_id): message
        for message in fake_channel.messages
    }
    for row in rows:
        expected = publication_message(row)
        message = published_by_event_id[UUID(str(row["id"]))]
        assert message["exchange"] == "all-in-one.runtime.test"
        assert message["routing_key"] == row["routing_key"]
        assert message["properties"].type == row["routing_key"]
        assert message["properties"].message_id == str(row["id"])
        assert message["properties"].correlation_id == str(row["correlation_id"])
        assert message["properties"].headers["schema_version"] == 1
        assert json.loads(message["body"].decode("utf-8")) == expected

        stored_payload = row["payload"]
        source_payload = (
            stored_payload.get("payload") or {}
            if isinstance(stored_payload, dict)
            and "event_id" in stored_payload
            and "payload" in stored_payload
            else stored_payload
        )
        expected_payload = {
            key: source_payload[key]
            for key in SAFE_PAYLOAD_FIELDS.get(row["aggregate_type"], frozenset())
            if key in source_payload
        }
        assert expected["payload"] == expected_payload


def test_publication_message_masks_payment_refund_reason() -> None:
    event = {
        "id": uuid4(),
        "routing_key": "payment.refunded",
        "schema_version": 1,
        "aggregate_type": "payment",
        "aggregate_id": uuid4(),
        "correlation_id": uuid4(),
        "entity_id": None,
        "payload": {
            "payment_id": "pay-123",
            "amount_brl": "99.9000",
            "provider_environment": "sandbox",
            "idempotency_key_hash": "idem-hash",
            "reason_hash": "reason-hash",
            "reason": "chargeback solicitado",
            "authorization_code": "segredo-nao-publicar",
        },
        "created_at": datetime.now(UTC),
    }

    message = publication_message(event)

    assert message["payload"] == {
        "amount_brl": "99.9000",
        "idempotency_key_hash": "idem-hash",
        "payment_id": "pay-123",
        "provider_environment": "sandbox",
        "reason_hash": "reason-hash",
    }
    assert "reason" not in message["payload"]
    assert "authorization_code" not in message["payload"]


def _clear_audit_outbox(postgres_dsn: str) -> None:
    del postgres_dsn


def _set_module_postgres_dsns(monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> None:
    for module in load_module_catalog()["modules"]:
        monkeypatch.setenv(f"ALL_IN_ONE_{module['slug'].upper()}_POSTGRES_DSN", postgres_dsn)


@pytest.mark.skipif(not POSTGRES_DSN or not RABBITMQ_URL, reason="DSNs PostgreSQL e RabbitMQ de integracao nao configuradas.")
def test_dispatcher_publishes_real_runtime_events_for_all_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_module_postgres_dsns(monkeypatch, POSTGRES_DSN)  # type: ignore[arg-type]
    _clear_audit_outbox(POSTGRES_DSN)  # type: ignore[arg-type]

    rows = _seed_runtime_event_rows()
    assert rows, "Nenhum evento real foi gerado a partir do catalogo."

    exchange = f"all-in-one.runtime.real.{uuid4()}"
    settings = OutboxSettings(
        postgres_dsn=POSTGRES_DSN,
        rabbitmq_url=RABBITMQ_URL,
        exchange=exchange,
        batch_size=max(1000, len(rows) + 10),
    )
    dispatcher = OutboxDispatcher(settings)
    rabbit = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = rabbit.channel()
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    queue = channel.queue_declare(queue="", exclusive=True).method.queue
    channel.queue_bind(exchange=exchange, queue=queue, routing_key="#")

    try:
        summary = dispatcher.publish_batch()

        assert summary.selected == len(rows)
        assert summary.published == len(rows)
        assert summary.failed == 0

        messages: dict[str, tuple[object, dict[str, object]]] = {}
        while True:
            method, properties, body = channel.basic_get(queue=queue, auto_ack=True)
            if method is None:
                break
            message = json.loads(body)
            messages[message["event_id"]] = (properties, message)

        assert len(messages) == len(rows)

        with psycopg.connect(POSTGRES_DSN) as connection:
            for row in rows:
                row_id = str(row["id"])
                properties, message = messages[row_id]
                expected = publication_message(row)
                assert properties.message_id == row_id
                assert properties.correlation_id == str(row["correlation_id"])
                assert properties.headers["schema_version"] == row["schema_version"]
                assert message == expected
                status = connection.execute(
                    "SELECT status, published_at FROM audit.domain_events WHERE id = %s",
                    (row_id,),
                ).fetchone()
                assert status[0] == "published"
                assert status[1] is not None
                assert (
                    connection.execute(
                        """SELECT COUNT(*)
                           FROM audit.event_deliveries
                           WHERE event_id = %s AND delivery_status = 'publisher_confirmed'""",
                        (row_id,),
                    ).fetchone()[0]
                    == 1
                )
    finally:
        dispatcher.close()
        rabbit.close()
