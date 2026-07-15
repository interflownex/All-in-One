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


def test_crm_lead_opportunity_activity_and_campaign_journey() -> None:
    client = client_for("crm")
    actor = str(uuid4())
    nonce = uuid4().hex

    lead = client.post(
        "/resources/leads",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "name": f"Lead {nonce}",
                "source": "landing-page",
            },
        },
    )
    assert lead.status_code == 201
    assert lead.json()["status"] == "new"

    qualified = client.post(
        f"/resources/leads/{lead.json()['id']}/actions/qualify",
        headers=actor_headers(actor),
        json={"reason": "perfil aderente ao ICP"},
    )
    assert qualified.status_code == 200
    assert qualified.json()["status"] == "qualified"

    activity = client.post(
        "/resources/activities",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "lead_id": lead.json()["id"],
                "activity_type": "call",
                "scheduled_at": "2026-07-15T14:00:00Z",
            },
        },
    )
    assert activity.status_code == 201
    assert activity.json()["status"] == "scheduled"

    completed_activity = client.post(
        f"/resources/activities/{activity.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "call realizada e registrada"},
    )
    assert completed_activity.status_code == 200
    assert completed_activity.json()["status"] == "completed"

    opportunity = client.post(
        "/resources/opportunities",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "lead_id": lead.json()["id"],
                "title": "Proposta Enterprise",
                "expected_value_brl": "1299.00",
            },
        },
    )
    assert opportunity.status_code == 201
    assert opportunity.json()["status"] == "open"

    denied_proposal = client.post(
        f"/resources/opportunities/{opportunity.json()['id']}/actions/propose",
        headers=actor_headers(actor),
        json={"reason": "proposta sem MFA"},
    )
    assert denied_proposal.status_code == 403

    proposed = client.post(
        f"/resources/opportunities/{opportunity.json()['id']}/actions/propose",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "proposta aprovada comercialmente"},
    )
    assert proposed.status_code == 200
    assert proposed.json()["status"] == "proposal_sent"

    won = client.post(
        f"/resources/opportunities/{opportunity.json()['id']}/actions/win",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "cliente aceitou a proposta"},
    )
    assert won.status_code == 200
    assert won.json()["status"] == "won"

    negative_opportunity = client.post(
        "/resources/opportunities",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "lead_id": lead.json()["id"],
                "title": "Valor invalido",
                "expected_value_brl": "-1.00",
            },
        },
    )
    assert negative_opportunity.status_code == 422

    campaign = client.post(
        "/resources/campaigns",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "campaign_key": f"camp-{nonce}",
                "channel": "email",
            },
        },
    )
    assert campaign.status_code == 201
    assert campaign.json()["status"] == "draft"

    denied_launch = client.post(
        f"/resources/campaigns/{campaign.json()['id']}/actions/launch",
        headers=actor_headers(actor),
        json={"reason": "campanha sem MFA"},
    )
    assert denied_launch.status_code == 403

    launched = client.post(
        f"/resources/campaigns/{campaign.json()['id']}/actions/launch",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "segmentacao revisada"},
    )
    assert launched.status_code == 200
    assert launched.json()["status"] == "active"

    closed_campaign = client.post(
        f"/resources/campaigns/{campaign.json()['id']}/actions/close",
        headers=actor_headers(actor),
        json={"reason": "campanha encerrada"},
    )
    assert closed_campaign.status_code == 200
    assert closed_campaign.json()["status"] == "closed"

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "crm.lead.created",
        "crm.lead.qualified",
        "crm.activity.created",
        "crm.activity.completed",
        "crm.opportunity.created",
        "crm.opportunity.proposed",
        "crm.opportunity.won",
        "crm.campaign.created",
        "crm.campaign.launched",
        "crm.campaign.closed",
    } <= routing_keys
