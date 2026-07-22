from uuid import UUID, uuid4

from platform_test_support import fresh_client_for


def actor_headers(user_id: str, roles: str = "") -> dict[str, str]:
    headers = {"X-Actor-User-Id": user_id}
    if roles:
        headers["X-Actor-Roles"] = roles
    return headers


def test_mutation_outbox_uses_request_correlation_id() -> None:
    marketplace = fresh_client_for("marketplace")
    user_id = str(uuid4())
    correlation_id = str(uuid4())
    nonce = uuid4().hex

    created = marketplace.post(
        "/resources/orders",
        headers={
            **actor_headers(user_id),
            "X-Idempotency-Key": f"order-{nonce}",
            "X-Correlation-Id": correlation_id,
        },
        json={
            "user_id": user_id,
            "payload": {
                "store_id": "store-correlation",
                "escrow_id": "escrow-correlation",
                "total_brl": "49.90",
                "items": [
                    {"sku": "SKU-CORRELATION", "quantity": 1, "unit_brl": "49.90"}
                ],
            },
        },
    )

    assert created.status_code == 201
    outbox = marketplace.get(
        "/events/outbox", headers=actor_headers(user_id, "auditor")
    )
    assert outbox.status_code == 200
    order_created = [
        event
        for event in outbox.json()
        if event["routing_key"] == "marketplace.order.created"
    ]
    assert order_created
    assert order_created[0]["correlation_id"] == correlation_id


def test_mutation_without_header_generates_valid_correlation_id() -> None:
    services = fresh_client_for("services")
    provider_id = str(uuid4())

    created = services.post(
        "/resources/providers",
        headers=actor_headers(provider_id),
        json={"user_id": provider_id, "payload": {"category": "maintenance"}},
    )

    assert created.status_code == 201
    outbox = services.get(
        "/events/outbox", headers=actor_headers(provider_id, "auditor")
    )
    assert outbox.status_code == 200
    provider_created = [
        event
        for event in outbox.json()
        if event["routing_key"] == "services.provider.created"
    ]
    assert provider_created
    UUID(provider_created[0]["correlation_id"])


def test_invalid_correlation_id_is_rejected_before_mutation() -> None:
    delivery = fresh_client_for("delivery")
    user_id = str(uuid4())

    response = delivery.post(
        "/resources/delivery_requests",
        headers={
            **actor_headers(user_id),
            "X-Idempotency-Key": f"delivery-{uuid4().hex}",
            "X-Correlation-Id": "not-a-uuid",
        },
        json={
            "user_id": user_id,
            "payload": {
                "service_type": "package",
                "origin": {"lat": -23.5505, "lng": -46.6333},
                "destination": {"lat": -23.5617, "lng": -46.6559},
                "quoted_brl": "32.50",
                "declared_value_brl": "120.00",
            },
        },
    )

    assert response.status_code == 422
