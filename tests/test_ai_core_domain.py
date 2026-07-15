from __future__ import annotations

from uuid import uuid4

from platform_test_support import client_for


def actor_headers(
    user_id: str,
    roles: str = "administrator",
    *,
    mfa_verified: bool = False,
) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": roles,
        "X-MFA-Verified": "true" if mfa_verified else "false",
    }


def test_ai_core_provider_model_run_cost_and_memory_journey() -> None:
    client = client_for("ai_core")
    actor = str(uuid4())
    nonce = uuid4().hex

    memory = client.post(
        "/resources/ai_memories",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "memory_key": f"context-{nonce}",
                "summary": "Memoria autorizada para execucao sandbox",
            },
        },
    )
    assert memory.status_code == 201
    assert memory.json()["status"] == "draft"

    indexed = client.post(
        f"/resources/ai_memories/{memory.json()['id']}/actions/index",
        headers=actor_headers(actor),
        json={"reason": "memoria validada para indice local"},
    )
    assert indexed.status_code == 200
    assert indexed.json()["status"] == "indexed"

    model_run = client.post(
        "/resources/model_runs",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "provider_adapter": "sandbox_openai_compatible",
                "provider_name": "sandbox-ai",
                "model_name": "gpt-sandbox-mini",
                "prompt_tokens": "512",
                "completion_tokens": "128",
                "estimated_cost_brl": "0.84",
                "requested_at": "2026-07-15T10:30:00Z",
            },
        },
    )
    assert model_run.status_code == 201
    assert model_run.json()["status"] == "requested"

    completed = client.post(
        f"/resources/model_runs/{model_run.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "provider sandbox retornou resposta controlada"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    denied_cost_approval = client.post(
        f"/resources/model_runs/{model_run.json()['id']}/actions/approve_cost",
        headers=actor_headers(actor),
        json={"reason": "custo sem MFA"},
    )
    assert denied_cost_approval.status_code == 403

    approved_cost = client.post(
        f"/resources/model_runs/{model_run.json()['id']}/actions/approve_cost",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "custo aprovado contra tabela sandbox"},
    )
    assert approved_cost.status_code == 200
    assert approved_cost.json()["status"] == "cost_approved"

    negative_cost = client.post(
        "/resources/model_runs",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "provider_adapter": "sandbox_openai_compatible",
                "provider_name": "sandbox-ai",
                "model_name": "gpt-sandbox-mini",
                "prompt_tokens": "1",
                "completion_tokens": "1",
                "estimated_cost_brl": "-0.01",
                "requested_at": "2026-07-15T10:30:00Z",
            },
        },
    )
    assert negative_cost.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "ai.memory.created",
        "ai.memory.indexed",
        "ai.model_run.requested",
        "ai.model_run.completed",
        "ai.model_run.cost_approved",
    } <= routing_keys
