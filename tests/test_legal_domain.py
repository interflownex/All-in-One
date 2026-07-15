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


def test_legal_case_deadline_alert_and_completion_journey() -> None:
    client = client_for("legal")
    actor = str(uuid4())
    nonce = uuid4().hex

    case = client.post(
        "/resources/cases",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "case_number": f"LEGAL-{nonce}",
                "case_type": "consumer",
                "opened_at": "2026-07-15",
                "title": "Prazo juridico auditavel",
                "risk_brl": "1500.00",
            },
        },
    )
    assert case.status_code == 201

    deadline = client.post(
        "/resources/deadlines",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "case_id": case.json()["id"],
                "deadline_type": "appeal",
                "due_at": "2026-07-31T17:00:00Z",
            },
        },
    )
    assert deadline.status_code == 201
    assert deadline.json()["status"] == "pending"

    denied_alert = client.post(
        f"/resources/deadlines/{deadline.json()['id']}/actions/alert",
        headers=actor_headers(actor),
        json={"reason": "alerta sem MFA"},
    )
    assert denied_alert.status_code == 403

    alerted = client.post(
        f"/resources/deadlines/{deadline.json()['id']}/actions/alert",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "prazo critico confirmado"},
    )
    assert alerted.status_code == 200
    assert alerted.json()["status"] == "alerted"

    completed = client.post(
        f"/resources/deadlines/{deadline.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "manifestacao protocolada"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    missing_due_at = client.post(
        "/resources/deadlines",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "case_id": case.json()["id"],
                "deadline_type": "appeal",
            },
        },
    )
    assert missing_due_at.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "legal.case.created",
        "legal.deadline.created",
        "legal.deadline.alerted",
        "legal.deadline.completed",
    } <= routing_keys
