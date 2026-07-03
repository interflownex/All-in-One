from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from modules.shared.domain_rules import event_for_create, rule_for
from modules.shared.outbox_dispatcher import OutboxDispatcher, OutboxSettings, SAFE_PAYLOAD_FIELDS, publication_message
from modules.shared.runtime import create_module_app
from tests.test_runtime_event_generation import (
    generate_payload,
    get_evented_transition,
    get_primary_resource,
    load_module_catalog,
    resolve_entity_id,
)


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


def _find_event(store, routing_key: str) -> dict[str, object]:
    for event in store.outbox():
        if event["routing_key"] == routing_key:
            return event
    raise AssertionError(f"Evento {routing_key} nao encontrado no outbox de teste.")


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


def _seed_runtime_event_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

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
        creator_user_id = str(uuid4())
        payload = generate_payload(rule, creator_user_id)
        entity_id = resolve_entity_id(payload)
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
        create_event = _find_event(store, expected_create_routing_key)
        rows.append(_to_dispatch_row(created, create_event))

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
        transition_event = _find_event(store, transition.event)
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

        expected_payload = {
            key: row["payload"][key]
            for key in SAFE_PAYLOAD_FIELDS.get(row["aggregate_type"], frozenset())
            if key in row["payload"]
        }
        assert expected["payload"] == expected_payload
