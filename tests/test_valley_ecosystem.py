from uuid import uuid4

from platform_test_support import fresh_client_for


def actor_headers(
    user_id: str,
    roles: str = "owner",
    *,
    business_id: str | None = None,
    business_status: str = "active",
    business_plan: str | None = None,
    business_cnpj: str | None = None,
    valley_master: bool = False,
    scopes: str = "",
) -> dict[str, str]:
    headers = {"X-Actor-User-Id": user_id, "X-Actor-Roles": roles, "X-Actor-Scopes": scopes}
    if business_id:
        headers["X-Business-Id"] = business_id
        headers["X-Business-Status"] = business_status
    if business_plan:
        headers["X-Business-Plan"] = business_plan
    if business_cnpj:
        headers["X-Business-CNPJ"] = business_cnpj
    if valley_master:
        headers["X-Valley-Master-Account"] = "true"
    return headers


def test_valley_business_essential_plan_and_local_inventory_acl() -> None:
    business = fresh_client_for("business")
    marketplace = fresh_client_for("marketplace")
    merchant_id = str(uuid4())
    business_id = str(uuid4())
    cnpj = "12345678000199"

    blocked_branch = business.post(
        "/resources/branches",
        headers=actor_headers(
            merchant_id,
            "owner",
            business_id=business_id,
            business_plan="essential",
            business_cnpj=cnpj,
        ),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "cnpj": "12345678000270",
                "root_cnpj": "12345678000270",
                "legal_name": "Filial Bloqueada",
            },
        },
    )
    assert blocked_branch.status_code == 403

    blocked_global_product = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-valley-local",
                "sku": "SKU-GLOBAL-BLOCKED",
                "name": "Produto global indevido",
                "price_brl": "59.90",
                "stock_location_type": "dropshipping",
                "inventory_source": "global_stock",
            },
        },
    )
    assert blocked_global_product.status_code == 403

    local_product = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-valley-local",
                "sku": "SKU-LOCAL-ALPHA",
                "name": "Produto local",
                "price_brl": "59.90",
                "stock_location_type": "local_physical",
                "stock_quantity": 4,
            },
        },
    )
    assert local_product.status_code == 201
    assert local_product.json()["payload"]["stock_location_type"] == "local_physical"


def test_stock_global_import_is_master_only_and_discounts_hide_unavailable_tiers() -> None:
    stock = fresh_client_for("stock")
    user_id = str(uuid4())

    denied = stock.post(
        "/resources/catalog_products",
        headers=actor_headers(user_id, "merchant"),
        json={
            "user_id": user_id,
            "payload": {
                "supplier_id": "amazon",
                "external_sku": "AMZ-DENIED",
                "name": "Produto Stock",
                "list_price_brl": "200.00",
            },
        },
    )
    assert denied.status_code == 403

    master = stock.post(
        "/resources/catalog_products",
        headers=actor_headers(user_id, "valley_master", valley_master=True),
        json={
            "user_id": user_id,
            "payload": {
                "supplier_id": "amazon",
                "external_sku": "AMZ-MASTER",
                "name": "Produto Stock",
                "list_price_brl": "200.00",
            },
        },
    )
    assert master.status_code == 201

    options = stock.post(
        "/valley/checkout/discount-options",
        json={"price_brl": "200.00", "user_pepitas_balance": 250},
    )
    assert options.status_code == 200
    assert [item["percent"] for item in options.json()["available_discount_options"]] == [10, 20]
    assert options.json()["hidden_unavailable_options"] == 1

    hidden_quote = stock.post(
        "/valley/checkout/discount-quotes",
        headers={**actor_headers(user_id), "X-Idempotency-Key": f"quote-hidden-{uuid4().hex}"},
        json={"price_brl": "200.00", "user_pepitas_balance": 250, "selected_percent": 50},
    )
    assert hidden_quote.status_code == 403

    quote = stock.post(
        "/valley/checkout/discount-quotes",
        headers={**actor_headers(user_id), "X-Idempotency-Key": f"quote-{uuid4().hex}"},
        json={"price_brl": "200.00", "user_pepitas_balance": 500, "selected_percent": 50},
    )
    assert quote.status_code == 201
    assert quote.json()["payload"]["final_price_brl"] == "100.00"


def test_stock_supplier_order_lifecycle_records_tracking_events() -> None:
    stock = fresh_client_for("stock")
    operator_id = str(uuid4())
    nonce = uuid4().hex
    headers = actor_headers(operator_id, "valley_master", valley_master=True)

    order = stock.post(
        "/resources/supplier_orders",
        headers={**headers, "X-Idempotency-Key": f"supplier-order-{nonce}"},
        json={
            "user_id": operator_id,
            "payload": {
                "supplier_id": "supplier-sandbox",
                "catalog_product_id": "catalog-product-sandbox",
                "external_order_id": f"EXT-{nonce}",
                "cost_brl": "42.10",
            },
        },
    )
    assert order.status_code == 201
    assert order.json()["status"] == "created"

    acknowledged = stock.post(
        f"/resources/supplier_orders/{order.json()['id']}/actions/acknowledge",
        headers=headers,
        json={"reason": "Pedido aceito pelo fornecedor sandbox"},
    )
    assert acknowledged.status_code == 200
    assert acknowledged.json()["status"] == "acknowledged"

    shipped = stock.post(
        f"/resources/supplier_orders/{order.json()['id']}/actions/ship",
        headers=headers,
        json={
            "reason": "Coleta confirmada",
            "payload": {
                "tracking_code": f"TRK-{nonce}",
                "tracking_url": "https://tracking.example.test/supplier",
                "carrier": "Fornecedor Sandbox",
            },
        },
    )
    assert shipped.status_code == 200
    assert shipped.json()["status"] == "shipped"
    assert shipped.json()["payload"]["tracking_code"] == f"TRK-{nonce}"

    delivered = stock.post(
        f"/resources/supplier_orders/{order.json()['id']}/actions/deliver",
        headers=headers,
        json={"reason": "Pedido entregue pelo fornecedor"},
    )
    assert delivered.status_code == 200
    assert delivered.json()["status"] == "delivered"

    outbox = stock.get("/events/outbox", headers=actor_headers(operator_id, "auditor"))
    assert outbox.status_code == 200
    routing_keys = {event["routing_key"] for event in outbox.json()}
    assert {
        "stock.supplier_order.created",
        "stock.supplier_order.acknowledged",
        "stock.supplier_order.shipped",
        "stock.supplier_order.delivered",
    } <= routing_keys


def test_merchant_manual_pepita_grant_emits_valley_event() -> None:
    marketplace = fresh_client_for("marketplace")
    customer_id = str(uuid4())
    merchant_id = str(uuid4())
    business_id = str(uuid4())
    nonce = uuid4().hex

    order = marketplace.post(
        "/resources/orders",
        headers={**actor_headers(customer_id), "X-Idempotency-Key": f"order-{nonce}"},
        json={
            "user_id": customer_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-valley-local",
                "escrow_id": "escrow-valley-local",
                "total_brl": "90.00",
            },
        },
    )
    assert order.status_code == 201
    order_id = order.json()["id"]

    paid = marketplace.post(
        f"/resources/orders/{order_id}/actions/pay",
        headers=actor_headers(customer_id),
        json={"reason": "venda paga"},
    )
    assert paid.status_code == 200

    grant = marketplace.post(
        f"/valley/orders/{order_id}/pepitas/grants",
        headers={
            **actor_headers(merchant_id, "merchant", business_id=business_id),
            "X-Idempotency-Key": f"pepitas-{nonce}",
        },
        json={
            "pepitas": 100,
            "customer_user_id": customer_id,
            "merchant_gold_ledger_id": f"gold-ledger-{nonce}",
        },
    )
    assert grant.status_code == 201
    assert grant.json()["payload"]["grant_mode"] == "merchant_manual_free_will"

    repeated = marketplace.post(
        f"/valley/orders/{order_id}/pepitas/grants",
        headers={
            **actor_headers(merchant_id, "merchant", business_id=business_id),
            "X-Idempotency-Key": f"pepitas-{nonce}",
        },
        json={
            "pepitas": 100,
            "customer_user_id": customer_id,
            "merchant_gold_ledger_id": f"gold-ledger-{nonce}",
        },
    )
    assert repeated.status_code == 201
    assert repeated.json()["id"] == grant.json()["id"]

    blocked_amount = marketplace.post(
        f"/valley/orders/{order_id}/pepitas/grants",
        headers={
            **actor_headers(merchant_id, "merchant", business_id=business_id),
            "X-Idempotency-Key": f"pepitas-invalid-{nonce}",
        },
        json={
            "pepitas": 50,
            "customer_user_id": customer_id,
            "merchant_gold_ledger_id": f"gold-ledger-{nonce}",
        },
    )
    assert blocked_amount.status_code == 422

    outbox = marketplace.get("/events/outbox", headers=actor_headers(merchant_id, "auditor"))
    assert outbox.status_code == 200
    assert any(event["routing_key"] == "valley.pepitas.granted" for event in outbox.json())


def test_valley_essential_plan_blocks_external_integrations() -> None:
    marketplace = fresh_client_for("marketplace")
    merchant_id = str(uuid4())
    business_id = str(uuid4())

    blocked = marketplace.post(
        "/resources/stores",
        headers=actor_headers(
            merchant_id,
            "merchant",
            business_id=business_id,
            business_plan="essential",
            business_cnpj="12345678000199",
        ),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "business_id": business_id,
                "store_name": "Loja Essencial",
                "inventory_source": "local_physical",
                "external_integrations": ["erp-provider"],
            },
        },
    )
    assert blocked.status_code == 403
