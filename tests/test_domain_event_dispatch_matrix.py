from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

from modules.shared.outbox_dispatcher import publication_message


ROOT = Path(__file__).resolve().parents[1]


def load_fixtures() -> dict:
    return json.loads((ROOT / "config" / "events" / "domain_event_fixtures.json").read_text(encoding="utf-8"))


def iter_dispatch_cases() -> list[tuple[str, dict[str, object]]]:
    fixtures = load_fixtures()
    cases: list[tuple[str, dict[str, object]]] = []

    for module_slug, module in fixtures["modules"].items():
        for event in module["events"]:
            cases.append((module_slug, event))

    return cases


@pytest.mark.parametrize(("module_slug", "fixture_event"), iter_dispatch_cases())
def test_domain_event_dispatch_matrix_publishes_minimal_payload(module_slug: str, fixture_event: dict[str, object]) -> None:
    assert module_slug == fixture_event["payload"]["module"]

    message = publication_message(
        {
            "id": UUID(str(fixture_event["event_id"])),
            "routing_key": fixture_event["routing_key"],
            "schema_version": fixture_event["schema_version"],
            "aggregate_type": fixture_event["aggregate_type"],
            "aggregate_id": fixture_event["aggregate_id"],
            "correlation_id": UUID(str(fixture_event["correlation_id"])),
            "entity_id": fixture_event["entity_id"],
            "created_at": datetime.fromisoformat(str(fixture_event["occurred_at"]).replace("Z", "+00:00")),
            "payload": fixture_event["payload"],
        }
    )

    assert message["event_id"] == fixture_event["event_id"]
    assert message["routing_key"] == fixture_event["routing_key"]
    assert message["schema_version"] == 1
    assert message["aggregate_type"] == fixture_event["aggregate_type"]
    assert message["aggregate_id"] == fixture_event["aggregate_id"]
    assert message["correlation_id"] == fixture_event["correlation_id"]
    assert message["entity_id"] == fixture_event["entity_id"]
    assert message["occurred_at"] == "2026-06-30T00:00:00+00:00"
    assert message["payload"] == {}
    assert "summary" not in json.dumps(message, ensure_ascii=False).casefold()
    assert "module" not in json.dumps(message, ensure_ascii=False).casefold()
