from __future__ import annotations

from uuid import uuid4

from modules.shared.domain_rules import event_for_create
from modules.shared.store import SQLiteStore


def _exercise_completion_event(module: str, resource_type: str, payload: dict[str, object], expected_routing_key: str) -> None:
    store = SQLiteStore(module, ":memory:")
    user_id = str(uuid4())
    actor_user_id = str(uuid4())

    created = store.create(
        resource_type,
        user_id,
        None,
        "draft",
        payload,
        actor_user_id,
        (),
        event_for_create(module, resource_type),
        None,
    )
    approved = store.update(created, created["payload"], "approved", actor_user_id, "approve")
    store.update(approved, approved["payload"], "completed", actor_user_id, "complete", expected_routing_key)

    assert any(event["routing_key"] == expected_routing_key for event in store.outbox())


def test_ai_core_model_runs_emit_completed_event() -> None:
    _exercise_completion_event(
        "ai_core",
        "model_runs",
        {"source": "teste"},
        "ai_core.model_run.completed",
    )


def test_api_hub_integration_runs_emit_completed_event() -> None:
    _exercise_completion_event(
        "api_hub",
        "integration_runs",
        {
            "integration_type": "prompt-run",
            "provider_name": "local_mock_ai_response",
        },
        "api_hub.integration_run.completed",
    )
