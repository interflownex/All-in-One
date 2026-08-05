from __future__ import annotations

from uuid import uuid4

from platform_test_support import fresh_client_for


def actor_headers(user_id: str, idempotency_key: str | None = None) -> dict[str, str]:
    headers = {"X-Actor-User-Id": user_id, "X-Actor-Roles": "consumer"}
    if idempotency_key:
        headers["X-Idempotency-Key"] = idempotency_key
    return headers


def test_access_recovery_is_generic_and_hashes_device_fingerprint() -> None:
    identity = fresh_client_for("identity")
    nonce = uuid4().hex
    cpf = f"{int(nonce[:10], 16):011d}"[-11:]
    registered = identity.post(
        "/registrations",
        json={
            "full_name": "Usuario Recuperacao Valley",
            "cpf_document": cpf,
            "document_cpf": cpf,
            "email": f"{cpf}@cpf.valley.local",
            "phone_e164": "+5511999999999",
            "face_hash": f"face-{nonce}",
            "terms_accepted_at": "2026-08-04T12:00:00Z",
            "lgpd_consent_at": "2026-08-04T12:00:00Z",
        },
    )
    assert registered.status_code == 201, registered.text
    user = registered.json()
    fingerprint = "valley-recovery-device-001"

    known = identity.post(
        "/valley/access-recovery",
        json={"cpf": cpf, "device_fingerprint": fingerprint},
    )
    unknown = identity.post(
        "/valley/access-recovery",
        json={"cpf": "99999999999", "device_fingerprint": fingerprint},
    )

    assert known.status_code == 202
    assert unknown.status_code == 202
    assert known.json() == unknown.json()
    assert cpf not in known.text

    verifications = identity.get(
        "/resources/identity_verifications",
        headers=actor_headers(user["id"]),
    )
    assert verifications.status_code == 200
    recovery = next(
        item
        for item in verifications.json()
        if item["payload"].get("verification_type") == "access_recovery"
    )
    assert recovery["status"] == "PROCESSING"
    assert recovery["payload"]["device_fingerprint_hash"]
    assert len(recovery["payload"]["device_fingerprint_hash"]) == 64
    assert fingerprint not in str(recovery["payload"])


def test_feed_review_eligibility_returns_only_completed_purchase_for_owner() -> None:
    marketplace = fresh_client_for("marketplace")
    buyer_id = str(uuid4())
    other_user_id = str(uuid4())
    offer_id = f"marketplace:products:{uuid4()}"
    source_entity_id = str(uuid4())

    created = marketplace.post(
        "/resources/orders",
        headers=actor_headers(buyer_id, f"create-{uuid4()}"),
        json={
            "user_id": buyer_id,
            "payload": {
                "total_brl": "129.90",
                "offer_id": offer_id,
                "source_entity_id": source_entity_id,
                "source_module": "marketplace",
                "offer_title": "Produto comprado no feed",
            },
        },
    )
    assert created.status_code == 201, created.text
    order_id = created.json()["id"]

    before_delivery = marketplace.get(
        "/valley/feed/review-eligibility",
        headers=actor_headers(buyer_id),
    )
    assert before_delivery.status_code == 200
    assert before_delivery.json() == []

    paid = marketplace.post(
        f"/resources/orders/{order_id}/actions/pay",
        headers=actor_headers(buyer_id, f"pay-{uuid4()}"),
        json={"reason": "Pagamento confirmado", "payload": {}},
    )
    assert paid.status_code == 200, paid.text
    delivered = marketplace.post(
        f"/resources/orders/{order_id}/actions/deliver",
        headers=actor_headers(buyer_id, f"deliver-{uuid4()}"),
        json={"reason": "Entrega confirmada", "payload": {}},
    )
    assert delivered.status_code == 200, delivered.text

    eligible = marketplace.get(
        "/valley/feed/review-eligibility",
        headers=actor_headers(buyer_id),
    )
    assert eligible.status_code == 200
    assert eligible.json() == [
        {
            "id": order_id,
            "title": "Produto comprado no feed",
            "status": "delivered",
            "offer_id": offer_id,
            "source_entity_id": source_entity_id,
            "source_module": "marketplace",
            "can_review": True,
        }
    ]

    other_user = marketplace.get(
        "/valley/feed/review-eligibility",
        headers=actor_headers(other_user_id),
    )
    assert other_user.status_code == 200
    assert other_user.json() == []
