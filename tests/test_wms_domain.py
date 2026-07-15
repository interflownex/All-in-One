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


def test_wms_receiving_picking_and_dispatch_journey() -> None:
    client = client_for("wms")
    actor = str(uuid4())
    nonce = uuid4().hex

    warehouse = client.post(
        "/resources/warehouses",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "name": f"CD {nonce}",
                "description": "Centro de distribuicao auditavel",
            },
        },
    )
    assert warehouse.status_code == 201
    assert warehouse.json()["status"] == "active"

    bin_resource = client.post(
        "/resources/bins",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "warehouse_id": warehouse.json()["id"],
                "code": f"A-{nonce[:6]}",
            },
        },
    )
    assert bin_resource.status_code == 201
    assert bin_resource.json()["status"] == "active"

    inventory = client.post(
        "/resources/inventory",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "warehouse_id": warehouse.json()["id"],
                "bin_id": bin_resource.json()["id"],
                "sku": f"SKU-{nonce}",
                "quantity": "25",
                "received_at": "2026-07-15T11:00:00Z",
            },
        },
    )
    assert inventory.status_code == 201
    assert inventory.json()["status"] == "received"

    allocated = client.post(
        f"/resources/inventory/{inventory.json()['id']}/actions/allocate",
        headers=actor_headers(actor),
        json={"reason": "estoque reservado para pedido"},
    )
    assert allocated.status_code == 200
    assert allocated.json()["status"] == "allocated"

    picking = client.post(
        "/resources/picking_waves",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "warehouse_id": warehouse.json()["id"],
                "order_reference": f"ORDER-{nonce}",
                "sku": f"SKU-{nonce}",
                "quantity": "3",
            },
        },
    )
    assert picking.status_code == 201
    assert picking.json()["status"] == "open"

    picked = client.post(
        f"/resources/picking_waves/{picking.json()['id']}/actions/pick",
        headers=actor_headers(actor),
        json={"reason": "separacao confirmada no coletor sandbox"},
    )
    assert picked.status_code == 200
    assert picked.json()["status"] == "picked"

    denied_close = client.post(
        f"/resources/picking_waves/{picking.json()['id']}/actions/close",
        headers=actor_headers(actor),
        json={"reason": "fechamento sem MFA"},
    )
    assert denied_close.status_code == 403

    closed = client.post(
        f"/resources/picking_waves/{picking.json()['id']}/actions/close",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "picking conferido"},
    )
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"

    shipment = client.post(
        "/resources/shipments",
        headers=actor_headers(actor),
        json={
            "user_id": actor,
            "payload": {
                "warehouse_id": warehouse.json()["id"],
                "picking_wave_id": picking.json()["id"],
                "carrier_reference": f"CARRIER-{nonce}",
            },
        },
    )
    assert shipment.status_code == 201
    assert shipment.json()["status"] == "ready"

    denied_dispatch = client.post(
        f"/resources/shipments/{shipment.json()['id']}/actions/dispatch",
        headers=actor_headers(actor),
        json={"reason": "despacho sem MFA"},
    )
    assert denied_dispatch.status_code == 403

    dispatched = client.post(
        f"/resources/shipments/{shipment.json()['id']}/actions/dispatch",
        headers=actor_headers(actor, mfa_verified=True),
        json={"reason": "doca liberada e carga conferida"},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["status"] == "dispatched"

    outbox = client.get("/events/outbox", headers=actor_headers(actor, "auditor"))
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "wms.warehouse.created",
        "wms.bin.created",
        "wms.inventory.received",
        "wms.inventory.allocated",
        "wms.picking.created",
        "wms.picking.completed",
        "wms.picking.closed",
        "wms.shipment.created",
        "wms.shipment.dispatched",
    } <= routing_keys
