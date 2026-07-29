from uuid import uuid4

from platform_test_support import fresh_client_for


def actor_headers(user_id: str) -> dict[str, str]:
    return {"X-Actor-User-Id": user_id}


def admin_headers(user_id: str, business_id: str) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": "administrator",
        "X-MFA-Verified": "true",
        "X-Business-Id": business_id,
        "X-Business-Status": "active",
    }


def create_published_product(
    marketplace,
    *,
    merchant_id: str,
    name: str = "Cafeteira Compacta",
    sku: str | None = None,
    price_brl: str = "199.90",
    category: str = "Casa",
    latitude: float = -19.92,
    longitude: float = -44.10,
    sponsored: bool = True,
) -> tuple[dict, dict]:
    business_id = str(uuid4())
    headers = admin_headers(merchant_id, business_id)
    store = marketplace.post(
        "/resources/stores",
        headers={**headers, "X-Idempotency-Key": f"store-{uuid4().hex}"},
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "company_id": business_id,
                "company_status": "approved",
                "name": "Loja Central",
                "latitude": latitude,
                "longitude": longitude,
            },
        },
    )
    assert store.status_code == 201
    store_id = store.json()["id"]
    approved_store = marketplace.post(
        f"/resources/stores/{store_id}/actions/approve",
        headers=headers,
        json={"reason": "loja validada para catalogo"},
    )
    assert approved_store.status_code == 200

    product = marketplace.post(
        "/resources/products",
        headers={**headers, "X-Idempotency-Key": f"product-{uuid4().hex}"},
        json={
            "user_id": merchant_id,
            "entity_id": store_id,
            "payload": {
                "store_id": store_id,
                "sku": sku or "SKU-MKT-DEFAULT",
                "name": name,
                "description": "Produto local com retirada e entrega.",
                "category": category,
                "price_brl": price_brl,
                "stock_location_type": "local_physical",
                "stock_quantity": 8,
                "promotion": {
                    "active": True,
                    "starts_at": "2026-01-01",
                    "ends_at": "2099-12-31",
                    "discount_percent": "15",
                    "priority": 10,
                    "feed_priority": 20,
                    "sponsored": sponsored,
                },
            },
        },
    )
    assert product.status_code == 201
    product_id = product.json()["id"]
    approved_product = marketplace.post(
        f"/resources/products/{product_id}/actions/approve",
        headers=headers,
        json={"reason": "produto revisado"},
    )
    assert approved_product.status_code == 200
    published_product = marketplace.post(
        f"/resources/products/{product_id}/actions/publish",
        headers=headers,
        json={"reason": "produto liberado no catalogo"},
    )
    assert published_product.status_code == 200
    return store.json(), published_product.json()


def test_marketplace_catalog_feed_and_promotion_are_contextual() -> None:
    marketplace = fresh_client_for("marketplace")
    merchant_id = str(uuid4())
    _, product = create_published_product(
        marketplace,
        merchant_id=merchant_id,
        name="Cafeteira Compacta",
        sku="SKU-MKT-CAFE-A",
        price_brl="199.90",
    )

    catalog = marketplace.get(
        "/valley/marketplace/catalog",
        params={
            "q": "cafeteira",
            "category": "Casa",
            "latitude": -19.921,
            "longitude": -44.101,
            "radius_km": 5,
            "sort": "distance",
        },
    )
    assert catalog.status_code == 200
    payload = catalog.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == product["id"]
    assert payload["items"][0]["distance_km"] < 1
    assert payload["items"][0]["in_stock"] is True

    feed = marketplace.get("/valley/feed")
    assert feed.status_code == 200
    assert feed.json()["format"] == "vertical_9_16"
    assert feed.json()["items"][0]["disclosure"] == "Patrocinado"

    promotion = marketplace.get("/valley/promotions/today")
    assert promotion.status_code == 200
    assert promotion.json()["active"] is True
    assert promotion.json()["promotion"]["dismissible"] is True
    assert promotion.json()["promotion"]["id"] == product["id"]


def test_marketplace_favorites_and_cart_are_isolated_by_actor() -> None:
    marketplace = fresh_client_for("marketplace")
    merchant_id = str(uuid4())
    customer_id = str(uuid4())
    other_customer_id = str(uuid4())
    _, product = create_published_product(
        marketplace,
        merchant_id=merchant_id,
        sku="SKU-MKT-CAFE-B",
        price_brl="19.90",
        sponsored=False,
    )
    product_id = product["id"]

    favorite = marketplace.put(
        f"/valley/favorites/{product_id}",
        headers=actor_headers(customer_id),
    )
    assert favorite.status_code == 200
    assert favorite.json()["saved"] is True

    favorites = marketplace.get(
        "/valley/favorites",
        headers=actor_headers(customer_id),
    )
    assert favorites.status_code == 200
    assert favorites.json()["total"] == 1

    other_favorites = marketplace.get(
        "/valley/favorites",
        headers=actor_headers(other_customer_id),
    )
    assert other_favorites.status_code == 200
    assert other_favorites.json()["total"] == 0

    cart = marketplace.put(
        f"/valley/cart/items/{product_id}",
        headers=actor_headers(customer_id),
        json={"quantity": 2},
    )
    assert cart.status_code == 200
    assert cart.json()["items_count"] == 2
    assert cart.json()["total_brl"] == "39.80"

    removed = marketplace.delete(
        f"/valley/cart/items/{product_id}",
        headers=actor_headers(customer_id),
    )
    assert removed.status_code == 200
    assert removed.json()["items_count"] == 0
    assert removed.json()["total_brl"] == "0"

    unfavorite = marketplace.delete(
        f"/valley/favorites/{product_id}",
        headers=actor_headers(customer_id),
    )
    assert unfavorite.status_code == 200
    assert unfavorite.json()["saved"] is False


def test_marketplace_catalog_rejects_incomplete_geolocation() -> None:
    marketplace = fresh_client_for("marketplace")
    response = marketplace.get(
        "/valley/marketplace/catalog",
        params={"latitude": -19.92},
    )
    assert response.status_code == 422
