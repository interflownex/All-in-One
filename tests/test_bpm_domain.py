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


def test_bpm_sla_timer_escalation_and_completion_journey() -> None:
    client = client_for("bpm")
    actor = str(uuid4())
    nonce = uuid4().hex

    sla_policy = client.post(
        "/resources/sla_policies",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "policy_key": f"onboarding-{nonce}",
                "response_minutes": "45",
                "escalation_role": "compliance_officer",
            },
        },
    )
    assert sla_policy.status_code == 201
    assert sla_policy.json()["status"] == "active"

    workflow = client.post(
        "/resources/workflow_instances",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "process_key": f"onboarding-{nonce}",
                "sla_policy_id": sla_policy.json()["id"],
                "started_at": "2026-07-15T07:30:00Z",
            },
        },
    )
    assert workflow.status_code == 201
    assert workflow.json()["status"] == "running"

    task = client.post(
        "/resources/tasks",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "workflow_instance_id": workflow.json()["id"],
                "assignee_user_id": actor,
                "due_at": "2026-07-15T08:15:00Z",
                "sla_policy_id": sla_policy.json()["id"],
                "title": "Validar onboarding com SLA",
            },
        },
    )
    assert task.status_code == 201
    assert task.json()["status"] == "open"

    denied_escalation = client.post(
        f"/resources/tasks/{task.json()['id']}/actions/escalate",
        headers=actor_headers(actor),
        json={"reason": "SLA vencido sem MFA"},
    )
    assert denied_escalation.status_code == 403

    escalated = client.post(
        f"/resources/tasks/{task.json()['id']}/actions/escalate",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "SLA vencido e escalado"},
    )
    assert escalated.status_code == 200
    assert escalated.json()["status"] == "escalated"

    completed = client.post(
        f"/resources/tasks/{task.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "Pendencia resolvida dentro da trilha auditavel"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "bpm.sla_policy.published",
        "bpm.process.started",
        "bpm.task.created",
        "bpm.task.escalated",
        "bpm.task.completed",
    } <= routing_keys
