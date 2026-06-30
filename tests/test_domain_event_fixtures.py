from __future__ import annotations

import json
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVENT_BULLET_PATTERN = re.compile(r"^\s*-\s*`([^`]+)`\s*$", re.MULTILINE)


def load_catalog() -> dict:
    return json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))


def load_fixtures() -> dict:
    return json.loads((ROOT / "config" / "events" / "domain_event_fixtures.json").read_text(encoding="utf-8"))


def extract_event_keys(path: Path) -> list[str]:
    return EVENT_BULLET_PATTERN.findall(path.read_text(encoding="utf-8"))


def test_domain_event_fixtures_match_catalog_module_docs_and_global_contract() -> None:
    catalog = load_catalog()
    fixtures = load_fixtures()
    docs_events_text = (ROOT / "docs" / "EVENTS.md").read_text(encoding="utf-8")

    assert fixtures["version"] == "2026-06-30"
    assert fixtures["source_catalog"] == "config/module_catalog.json"
    assert fixtures["source_catalog_version"] == catalog["version"]
    assert fixtures["exchange"] == "all-in-one.domain"
    assert fixtures["module_count"] == len(catalog["modules"])

    fixture_modules = fixtures["modules"]
    assert set(fixture_modules) == {module["slug"] for module in catalog["modules"]}

    total_events = 0

    for module in catalog["modules"]:
        slug = module["slug"]
        expected_events = list(module.get("events", []))
        total_events += len(expected_events)

        module_doc_events = extract_event_keys(ROOT / "modules" / slug / "EVENTS.md")
        assert module_doc_events == expected_events, slug

        fixture_module = fixture_modules[slug]
        assert fixture_module["title"] == module["title"]
        assert fixture_module["routing_keys"] == expected_events

        fixture_events = fixture_module["events"]
        assert len(fixture_events) == len(expected_events)
        assert [event["routing_key"] for event in fixture_events] == expected_events

        for index, event in enumerate(fixture_events, start=1):
            assert event["event_id"]
            assert event["correlation_id"]
            assert event["schema_version"] == 1
            assert event["occurred_at"] == "2026-06-30T00:00:00Z"
            assert event["routing_key"] == expected_events[index - 1]
            assert event["aggregate_type"] == event["routing_key"].rsplit(".", 1)[0]
            assert event["aggregate_id"] == f"{slug}-fixture-{index:02d}"
            assert event["entity_id"] == f"{slug}-fixture-{index:02d}"
            assert event["actor_user_id"] == f"{slug}-fixture-actor"
            assert event["event_id"] != event["correlation_id"]
            uuid.UUID(event["event_id"])
            uuid.UUID(event["correlation_id"])
            assert event["payload"] == {
                "module": slug,
                "routing_key": event["routing_key"],
                "summary": f"Fixture de evento do modulo {module['title']}",
            }
            assert "secret" not in json.dumps(event["payload"], ensure_ascii=False).casefold()

    assert fixtures["event_count"] == total_events
    assert "valley.gold.ledger.posted" in docs_events_text
