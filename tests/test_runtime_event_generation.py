from uuid import uuid4

import pytest

from modules.shared.domain_rules import event_for_create, rule_for
from modules.shared.runtime import create_module_app
from all_in_one_test_support.runtime_event_generation import (
    generate_payload,
    get_evented_transition,
    get_primary_resource,
    load_module_catalog,
    resolve_entity_id,
)


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
