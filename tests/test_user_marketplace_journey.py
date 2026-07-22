from uuid import uuid4

from platform_test_support import fresh_client_for


def actor_headers(user_id: str) -> dict[str, str]:
    return {"X-Actor-User-Id": user_id}


def test_user_identity_wallet_marketplace_order_journey() -> None:
    identity = fresh_client_for("identity")
    finance = fresh_client_for("finance")
    marketplace = fresh_client_for("marketplace")
    nonce = uuid4().hex
    phone_suffix = str(int(nonce[:8], 16)).zfill(10)[-10:]

    registration = identity.post(
        "/registrations",
        json={
            "full_name": "Cliente Marketplace",
            "cpf_document": f"CPF-{nonce[:12]}",
            "email": f"buyer-{nonce}@example.test",
            "phone_e164": f"+55{phone_suffix}",
            "face_hash": f"face-{nonce}",
            "terms_accepted_at": "2026-05-30T10:00:00Z",
            "lgpd_consent_at": "2026-05-30T10:00:00Z",
        },
    )
    assert registration.status_code == 201
    user_id = registration.json()["id"]
    headers = actor_headers(user_id)

    wallet = finance.post(
        "/resources/wallets",
        headers=headers,
        json={
            "user_id": user_id,
            "payload": {"wallet_type": "consumer", "currency": "BRL"},
        },
    )
    assert wallet.status_code == 201
    wallet_id = wallet.json()["id"]

    wallets = finance.get(f"/wallets/{user_id}", headers=headers)
    assert wallets.status_code == 200
    assert any(item["id"] == wallet_id for item in wallets.json())

    seller_id = str(uuid4())
    store_id = str(uuid4())
    store_reference = "store-marketplace"
    escrow_reference = "escrow-marketplace"
    escrow = finance.post(
        "/resources/escrows",
        headers={**headers, "X-Idempotency-Key": f"escrow-{nonce}"},
        json={
            "user_id": user_id,
            "payload": {
                "wallet_id": wallet_id,
                "beneficiary_user_id": seller_id,
                "amount_brl": "99.90",
                "release_condition": {"type": "delivery_confirmation"},
            },
        },
    )
    assert escrow.status_code == 201
    escrow_id = escrow.json()["id"]
    assert escrow_id
    assert escrow.json()["status"] == "created"

    order = marketplace.post(
        "/resources/orders",
        headers={**headers, "X-Idempotency-Key": f"order-{nonce}"},
        json={
            "user_id": user_id,
            "entity_id": store_id,
            "payload": {
                "store_id": store_reference,
                "escrow_id": escrow_reference,
                "total_brl": "99.90",
                "items": [
                    {"sku": "SKU-MARKETPLACE", "quantity": 1, "unit_brl": "99.90"}
                ],
            },
        },
    )
    assert order.status_code == 201
    order_id = order.json()["id"]
    assert order.json()["status"] == "created"

    paid = marketplace.post(
        f"/resources/orders/{order_id}/actions/pay",
        headers=headers,
        json={"reason": "pagamento autorizado via escrow"},
    )
    assert paid.status_code == 200
    assert paid.json()["status"] == "paid"
    assert paid.json()["payload"]["escrow_id"] == escrow_reference

    audit = marketplace.get(
        "/events/outbox",
        headers={"X-Actor-User-Id": user_id, "X-Actor-Roles": "auditor"},
    )
    assert audit.status_code == 200
    assert any(
        event["routing_key"] == "marketplace.order.paid" for event in audit.json()
    )
