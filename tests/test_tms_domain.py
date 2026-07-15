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


def test_tms_freight_pod_and_audit_journey() -> None:
    client = client_for("tms")
    actor = str(uuid4())
    nonce = uuid4().hex

    carrier = client.post(
        "/resources/carriers",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "name": f"Transportadora {nonce}",
                "coverage": ["sp", "rj"],
            },
        },
    )
    assert carrier.status_code == 201
    assert carrier.json()["status"] == "pending_review"

    route = client.post(
        "/resources/routes",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "origin": "Sao Paulo",
                "destination": "Rio de Janeiro",
                "distance_km": "430",
                "eta_minutes": "360",
            },
        },
    )
    assert route.status_code == 201
    assert route.json()["status"] == "planned"

    freight = client.post(
        "/resources/freights",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "carrier_id": carrier.json()["id"],
                "route_id": route.json()["id"],
                "freight_brl": "890.90",
                "toll_brl": "120.00",
                "scheduled_at": "2026-07-15T12:00:00Z",
            },
        },
    )
    assert freight.status_code == 201
    assert freight.json()["status"] == "quoted"

    denied_approval = client.post(
        f"/resources/freights/{freight.json()['id']}/actions/approve",
        headers=actor_headers(actor),
        json={"reason": "frete sem MFA"},
    )
    assert denied_approval.status_code == 403

    approved = client.post(
        f"/resources/freights/{freight.json()['id']}/actions/approve",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "frete validado com tabela sandbox"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    dispatched = client.post(
        f"/resources/freights/{freight.json()['id']}/actions/dispatch",
        headers=actor_headers(actor),
        json={"reason": "coleta iniciada"},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["status"] == "in_transit"

    completed = client.post(
        f"/resources/freights/{freight.json()['id']}/actions/complete",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "entrega concluida com canhoto"},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    pod = client.post(
        "/resources/proofs_of_delivery",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "freight_id": freight.json()["id"],
                "file_sha256": "6" * 64,
                "storage_key": f"vault/tms/{nonce}/pod.pdf",
                "delivered_at": "2026-07-15T18:00:00Z",
            },
        },
    )
    assert pod.status_code == 201
    assert pod.json()["status"] == "recorded"

    public_pod = client.post(
        "/resources/proofs_of_delivery",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "freight_id": freight.json()["id"],
                "file_sha256": "5" * 64,
                "storage_key": "https://public.example/pod.pdf",
                "delivered_at": "2026-07-15T18:00:00Z",
            },
        },
    )
    assert public_pod.status_code == 422

    audit = client.post(
        "/resources/freight_audits",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "freight_id": freight.json()["id"],
                "audit_result": "matched",
                "audited_at": "2026-07-15T19:00:00Z",
            },
        },
    )
    assert audit.status_code == 201
    assert audit.json()["status"] == "reviewed"

    denied_audit_close = client.post(
        f"/resources/freight_audits/{audit.json()['id']}/actions/close",
        headers=actor_headers(actor),
        json={"reason": "auditoria sem MFA"},
    )
    assert denied_audit_close.status_code == 403

    closed_audit = client.post(
        f"/resources/freight_audits/{audit.json()['id']}/actions/close",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "frete conciliado com POD"},
    )
    assert closed_audit.status_code == 200
    assert closed_audit.json()["status"] == "closed"

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "tms.carrier.created",
        "tms.route.created",
        "tms.freight.created",
        "tms.freight.approved",
        "tms.freight.dispatched",
        "tms.freight.completed",
        "tms.delivery.proved",
        "tms.freight.audit_created",
        "tms.freight.audit_closed",
    } <= routing_keys
