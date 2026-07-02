from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from modules.shared.domain_rules import ResourceRule, event_for_create, rule_for
from modules.shared.runtime import create_module_app


ROOT = Path(__file__).resolve().parents[1]


def load_module_catalog() -> dict:
    return json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))


def get_primary_resource(module_slug: str) -> str | None:
    catalog = load_module_catalog()
    for module in catalog["modules"]:
        if module["slug"] == module_slug:
            if not module["entities"]:
                return None
            return module["entities"][0]
    raise ValueError(f"Module {module_slug} not found in catalog")


def sample_geo_point() -> dict[str, float]:
    return {"latitude": -23.5505, "longitude": -46.6333}


def resolve_entity_id(payload: dict[str, object]) -> str | None:
    for key in ("company_id", "business_id", "store_id", "wallet_id", "resume_id"):
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def generate_payload(rule: ResourceRule, user_id: str) -> dict[str, object]:
    payload: dict[str, object] = {"user_id": user_id}
    for field in rule.required_fields:
        if field in payload:
            continue
        if field == "company_status":
            payload[field] = "active"
        elif field == "recruiter_visibility":
            payload[field] = "business_recruiters"
        elif field == "wallet_type":
            payload[field] = "personal"
        elif field == "service_type":
            payload[field] = "package"
        elif field == "vehicle_type":
            payload[field] = "car"
        elif field == "category":
            payload[field] = "maintenance"
        elif field == "employment_type":
            payload[field] = "full_time"
        elif field == "origin" or field == "destination":
            payload[field] = sample_geo_point()
        elif field == "scopes":
            payload[field] = ["orders:read"]
        elif field == "definition":
            payload[field] = {"widgets": []}
        elif field == "address":
            payload[field] = {
                "street": "Rua Exemplo",
                "city": "Sao Paulo",
                "state": "SP",
                "zip_code": "01000-000",
            }
        elif field == "risk_score":
            payload[field] = 0.42
        elif field == "health_identifier":
            payload[field] = f"health-{uuid4().hex[:8]}"
        elif field == "device_fingerprint":
            payload[field] = f"device-{uuid4().hex[:8]}"
        elif field == "case_number":
            payload[field] = f"CASE-{uuid4().hex[:10].upper()}"
        elif field == "client_name":
            payload[field] = "Integration Client"
        elif field == "client_id_hash":
            payload[field] = uuid4().hex
        elif field == "secret_reference":
            payload[field] = f"secret-{uuid4().hex[:8]}"
        elif field == "cnpj":
            payload[field] = "12345678000195"
        elif field == "root_cnpj":
            payload[field] = "12345678"
        elif field == "headline":
            payload[field] = "Test Headline"
        elif field == "title":
            payload[field] = "Test Title"
        elif field == "content":
            payload[field] = "Test Content"
        elif field == "description":
            payload[field] = "Test Description"
        elif field == "message":
            payload[field] = "Test Message"
        elif field == "name":
            payload[field] = "Test Name"
        elif "document_cnpj" in field:
            payload[field] = "12345678000195"
        elif "document" in field:
            payload[field] = "123456789"
        elif "hash" in field:
            payload[field] = uuid4().hex
        elif "amount" in field:
            payload[field] = "100.00"
        elif "price" in field:
            payload[field] = "100.00"
        elif "total" in field:
            payload[field] = "100.00"
        elif "id" in field:
            payload[field] = str(uuid4())
        else:
            payload[field] = "default"
    return payload


def get_evented_transition(rule: ResourceRule) -> tuple[str, object] | None:
    for name, transition in rule.transitions.items():
        if transition.event and rule.initial_status in transition.source:
            return name, transition
    return None


@pytest.mark.parametrize("module_slug", [m["slug"] for m in load_module_catalog()["modules"]])
def test_creating_primary_resource_generates_correct_event(module_slug: str) -> None:
    primary_resource = get_primary_resource(module_slug)
    if not primary_resource:
        pytest.skip(f"Module {module_slug} has no entities.")

    try:
        rule = rule_for(module_slug, primary_resource)
    except Exception:
        pytest.skip(f"Could not find rule for {primary_resource} in {module_slug}")

    app = create_module_app(module_slug)
    store = app.extra["store"]
    creator_user_id = str(uuid4())
    payload = generate_payload(rule, creator_user_id)
    entity_id = resolve_entity_id(payload)
    expected_routing_key = event_for_create(module_slug, primary_resource)

    created = store.create(
        primary_resource,
        creator_user_id,
        entity_id,
        rule.initial_status,
        payload,
        creator_user_id,
        rule.unique_fields,
        expected_routing_key,
        None,
    )

    assert created["resource_type"] == primary_resource
    assert created["payload"] == payload

    outbox = store.outbox()
    assert any(
        event["routing_key"] == expected_routing_key and event["resource_id"] == created["id"]
        for event in outbox
    ), f"No event found in outbox for {module_slug} ({primary_resource})"


@pytest.mark.parametrize("module_slug", [m["slug"] for m in load_module_catalog()["modules"]])
def test_creating_primary_resource_transition_emits_event_when_defined(module_slug: str) -> None:
    primary_resource = get_primary_resource(module_slug)
    if not primary_resource:
        pytest.skip(f"Module {module_slug} has no entities.")

    try:
        rule = rule_for(module_slug, primary_resource)
    except Exception:
        pytest.skip(f"Could not find rule for {primary_resource} in {module_slug}")

    evented_transition = get_evented_transition(rule)
    if not evented_transition:
        pytest.skip(f"No evented transition found for {module_slug} ({primary_resource})")

    transition_name, transition = evented_transition
    app = create_module_app(module_slug)
    store = app.extra["store"]
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

    updated = store.update(
        created,
        dict(created["payload"]),
        transition.target,
        creator_user_id,
        transition_name,
        transition.event,
    )

    assert updated["status"] == transition.target
    assert any(
        event["routing_key"] == transition.event and event["resource_id"] == created["id"]
        for event in store.outbox()
    ), f"No transition event found in outbox for {module_slug} ({primary_resource})"
