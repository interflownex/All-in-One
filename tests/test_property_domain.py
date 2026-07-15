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


def test_property_lease_and_maintenance_journey() -> None:
    client = client_for("property")
    actor = str(uuid4())
    tenant = str(uuid4())
    nonce = uuid4().hex

    property_resource = client.post(
        "/resources/properties",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "address": f"Rua Locacao {nonce}, 100",
                "property_type": "apartment",
            },
        },
    )
    assert property_resource.status_code == 201

    lease = client.post(
        "/resources/leases",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "property_id": property_resource.json()["id"],
                "tenant_user_id": tenant,
                "starts_at": "2026-08-01",
                "rent_amount_brl": "2500.00",
                "deposit_amount_brl": "2500.00",
            },
        },
    )
    assert lease.status_code == 201
    assert lease.json()["status"] == "draft"

    denied_activation = client.post(
        f"/resources/leases/{lease.json()['id']}/actions/activate",
        headers=actor_headers(actor),
        json={"reason": "ativacao sem MFA"},
    )
    assert denied_activation.status_code == 403

    activated = client.post(
        f"/resources/leases/{lease.json()['id']}/actions/activate",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "contrato assinado e vistoria concluida"},
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"

    maintenance = client.post(
        "/resources/maintenance_orders",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "property_id": property_resource.json()["id"],
                "issue_type": "plumbing",
                "requested_at": "2026-07-15T09:00:00Z",
                "estimated_cost_brl": "350.00",
            },
        },
    )
    assert maintenance.status_code == 201
    assert maintenance.json()["status"] == "requested"

    scheduled = client.post(
        f"/resources/maintenance_orders/{maintenance.json()['id']}/actions/schedule",
        headers=actor_headers(actor),
        json={"reason": "prestador disponivel"},
    )
    assert scheduled.status_code == 200
    assert scheduled.json()["status"] == "scheduled"

    denied_completion = client.post(
        f"/resources/maintenance_orders/{maintenance.json()['id']}/actions/complete",
        headers=actor_headers(actor),
        json={"reason": "conclusao sem MFA"},
    )
    assert denied_completion.status_code == 403

    completed = client.post(
        f"/resources/maintenance_orders/{maintenance.json()['id']}/actions/complete",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "reparo vistoriado e aceito"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    rejected_negative_rent = client.post(
        "/resources/leases",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "property_id": property_resource.json()["id"],
                "tenant_user_id": tenant,
                "starts_at": "2026-08-01",
                "rent_amount_brl": "-1.00",
            },
        },
    )
    assert rejected_negative_rent.status_code == 422

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "property.lease.created",
        "property.lease.activated",
        "property.maintenance.requested",
        "property.maintenance.scheduled",
        "property.maintenance.completed",
    } <= routing_keys
