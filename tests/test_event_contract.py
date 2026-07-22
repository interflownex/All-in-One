from __future__ import annotations

import json
from pathlib import Path

from modules.shared.event_contract import (
    EVENT_SCHEMA_VERSION,
    REDACTED_VALUE,
    build_event_envelope,
    sanitize_event_payload,
)
from modules.shared.store import SQLiteStore


ROOT = Path(__file__).resolve().parents[1]


def test_sanitize_event_payload_redacts_nested_credentials() -> None:
    sanitized, redacted = sanitize_event_payload(
        {
            "name": "registro permitido",
            "password": "senha-em-texto",
            "nested": {"api-key": "chave-em-texto", "secret_reference": "cofre://segredo"},
            "items": [{"authorization": "Bearer proibido"}],
        }
    )

    assert sanitized == {
        "name": "registro permitido",
        "password": REDACTED_VALUE,
        "nested": {"api-key": REDACTED_VALUE, "secret_reference": REDACTED_VALUE},
        "items": [{"authorization": REDACTED_VALUE}],
    }
    assert redacted == [
        "payload.password",
        "payload.nested.api-key",
        "payload.nested.secret_reference",
        "payload.items[0].authorization",
    ]
    serialized = json.dumps(sanitized)
    assert "senha-em-texto" not in serialized
    assert "chave-em-texto" not in serialized
    assert "Bearer proibido" not in serialized


def test_build_event_envelope_declares_required_contract() -> None:
    envelope = build_event_envelope(
        module="identity",
        routing_key="identity.user.created",
        actor_user_id="actor-1",
        correlation_id="correlation-1",
        causation_id="command-1",
        occurred_at="2026-07-22T00:00:00+00:00",
        item={
            "id": "user-1",
            "resource_type": "users",
            "user_id": "user-1",
            "entity_id": "tenant-1",
            "idempotency_key": "request-1",
            "payload": {"display_name": "Pessoa", "access_token": "proibido"},
        },
    )

    assert envelope["schema_version"] == EVENT_SCHEMA_VERSION
    assert envelope["producer"] == "identity"
    assert envelope["event_name"] == "identity.user.created"
    assert envelope["aggregate_type"] == "users"
    assert envelope["aggregate_id"] == "user-1"
    assert envelope["idempotency_key"] == "request-1"
    assert envelope["correlation_id"] == "correlation-1"
    assert envelope["causation_id"] == "command-1"
    assert envelope["tenant_id"] == "tenant-1"
    assert envelope["occurred_at"] == "2026-07-22T00:00:00+00:00"
    assert envelope["payload"]["access_token"] == REDACTED_VALUE
    assert envelope["retention"]["days"] == 2555
    assert envelope["replay"]["deduplicate_by"] == "event_id"
    assert envelope["backward_compatibility"]["policy"] == "additive"


def test_sqlite_outbox_persists_envelope_and_original_idempotency() -> None:
    store = SQLiteStore("identity")
    item = store.create(
        resource_type="users",
        user_id="user-1",
        entity_id="tenant-1",
        status="active",
        payload={"display_name": "Pessoa", "password": "proibido"},
        actor="actor-1",
        unique_fields=(),
        event="identity.user.created",
        idempotency_key="request-1",
    )

    event = store.outbox()[0]
    envelope = json.loads(event["payload"])
    assert envelope["aggregate_id"] == item["id"]
    assert envelope["idempotency_key"] == "request-1"
    assert envelope["correlation_id"] == event["correlation_id"]
    assert envelope["payload"]["password"] == REDACTED_VALUE


def test_every_persisted_domain_event_uses_the_shared_contract() -> None:
    producers = []
    for path in (ROOT / "modules" / "shared").glob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "INSERT INTO audit.domain_events" in source:
            producers.append(path.name)
            assert "build_event_envelope" in source, path.name
            assert "schema_version" in source, path.name
    assert producers
