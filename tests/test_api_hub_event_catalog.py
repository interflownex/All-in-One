import json
from pathlib import Path

from modules.shared.domain_rules import MODULE_ENTITIES, event_for_create, rule_for


ROOT = Path(__file__).resolve().parents[1]


API_HUB_EVENT_ALIASES = {
    "api_hub.api_client.created": "api.client.created",
    "api_hub.api_key.created": "api.key.created",
    "api_hub.webhook.created": "api.webhook.created",
    "api_hub.integration_run.created": "api.integration_run.created",
}


def test_api_hub_catalog_declares_runtime_domain_events() -> None:
    catalog = json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))
    api_hub_catalog = next(module for module in catalog["modules"] if module["slug"] == "api_hub")
    declared_events = set(api_hub_catalog["events"])

    runtime_events = set()
    for resource in MODULE_ENTITIES["api_hub"]:
        runtime_events.add(API_HUB_EVENT_ALIASES.get(event_for_create("api_hub", resource), event_for_create("api_hub", resource)))
        for transition in rule_for("api_hub", resource).transitions.values():
            if transition.event:
                runtime_events.add(transition.event)

    assert runtime_events <= declared_events
