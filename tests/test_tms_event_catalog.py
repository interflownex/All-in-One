import json
from pathlib import Path

from modules.shared.domain_rules import MODULE_ENTITIES, event_for_create, rule_for


ROOT = Path(__file__).resolve().parents[1]


def test_tms_catalog_declares_runtime_domain_events() -> None:
    catalog = json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))
    tms_catalog = next(module for module in catalog["modules"] if module["slug"] == "tms")
    declared_events = set(tms_catalog["events"])

    runtime_events = set()
    for resource in MODULE_ENTITIES["tms"]:
        runtime_events.add(event_for_create("tms", resource))
        for transition in rule_for("tms", resource).transitions.values():
            if transition.event:
                runtime_events.add(transition.event)

    assert runtime_events <= declared_events
