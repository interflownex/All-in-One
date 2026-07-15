from uuid import uuid4

from platform_test_support import client_for


def actor_headers(
    user_id: str,
    roles: str = "owner",
    *,
    mfa: bool = False,
) -> dict[str, str]:
    headers = {"X-Actor-User-Id": user_id, "X-Actor-Roles": roles}
    if mfa:
        headers["X-MFA-Verified"] = "true"
    return headers


def test_create_and_approve_flow():
    client = client_for("business")
    actor = str(uuid4())
    headers = {"X-Actor-User-Id": actor}
    created = client.post(
        "/create",
        headers=headers,
        json={"user_id": actor, "payload": {"source": "test"}},
    )
    assert created.status_code == 201
    resource_id = created.json()["id"]
    approved = client.post(
        "/approve",
        headers=headers,
        json={"id": resource_id, "reason": "validated in test"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


def test_business_membership_invite_and_role_assignment_flow() -> None:
    client = client_for("business")
    owner_id = str(uuid4())
    invited_user_id = str(uuid4())
    company_id = str(uuid4())

    invited = client.post(
        "/resources/user_company_memberships",
        headers=actor_headers(owner_id),
        json={
            "user_id": invited_user_id,
            "entity_id": company_id,
            "payload": {
                "company_id": company_id,
                "role": "hr_manager",
                "department": "People",
                "invitation_channel": "email",
            },
        },
    )

    assert invited.status_code == 201
    membership = invited.json()
    assert membership["status"] == "invited"
    assert membership["entity_id"] == company_id
    assert membership["payload"]["role"] == "hr_manager"

    outbox = client.get("/events/outbox", headers=actor_headers(owner_id))
    assert outbox.status_code == 200
    assert any(
        event["routing_key"] == "business.user.invited"
        for event in outbox.json()
    )

    denied = client.post(
        f"/resources/user_company_memberships/{membership['id']}/actions/activate",
        headers=actor_headers(owner_id),
        json={"reason": "confirmacao operacional do convite"},
    )
    assert denied.status_code == 403

    activated = client.post(
        f"/resources/user_company_memberships/{membership['id']}/actions/activate",
        headers=actor_headers(owner_id, mfa=True),
        json={"reason": "confirmacao operacional do convite"},
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"

    outbox_after_activation = client.get(
        "/events/outbox",
        headers=actor_headers(owner_id),
    )
    assert outbox_after_activation.status_code == 200
    assert any(
        event["routing_key"] == "business.role.assigned"
        for event in outbox_after_activation.json()
    )
