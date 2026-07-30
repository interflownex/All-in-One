import sys
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers

app = create_module_app("marketplace")

PUBLIC_PRODUCT_STATUSES = frozenset({"active", "published"})
PUBLIC_STORE_STATUSES = frozenset({"active", "approved"})
MAX_CART_QUANTITY = 99


class SupportCaseRequest(BaseModel):
    kind: Literal["support", "dispute"]
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=5, max_length=1000)
    desired_resolution: str | None = Field(default=None, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=120)


class CartItemRequest(BaseModel):
    quantity: int = Field(ge=1, le=MAX_CART_QUANTITY)


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    try:
        return date.fromisoformat(candidate[:10])
    except ValueError:
        return None


def _location(payload: dict[str, Any]) -> tuple[float, float] | None:
    source = payload.get("location")
    if not isinstance(source, dict):
        source = payload
    try:
        latitude = float(source["latitude"])
        longitude = float(source["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return latitude, longitude


def _distance_km(
    origin_latitude: float,
    origin_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
) -> float:
    lat1, lon1, lat2, lon2 = map(
        radians,
        (
            origin_latitude,
            origin_longitude,
            destination_latitude,
            destination_longitude,
        ),
    )
    delta_latitude = lat2 - lat1
    delta_longitude = lon2 - lon1
    a = (
        sin(delta_latitude / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_longitude / 2) ** 2
    )
    return 6371.0088 * 2 * asin(sqrt(a))


def _text_blob(payload: dict[str, Any]) -> str:
    tags = payload.get("tags")
    normalized_tags = (
        " ".join(str(item) for item in tags) if isinstance(tags, list) else ""
    )
    return (
        " ".join(
            str(payload.get(field) or "")
            for field in ("name", "description", "category", "subcategory", "brand")
        ).casefold()
        + f" {normalized_tags.casefold()}"
    )


def _store_index(store: Any) -> dict[str, dict[str, Any]]:
    return {str(item["id"]): item for item in store.list("stores")}


def _public_product(
    item: dict[str, Any],
    stores: dict[str, dict[str, Any]],
    *,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict[str, Any] | None:
    if item["status"] not in PUBLIC_PRODUCT_STATUSES:
        return None
    payload = item["payload"]
    store_id = str(payload.get("store_id") or "")
    merchant = stores.get(store_id)
    if merchant is None or merchant["status"] not in PUBLIC_STORE_STATUSES:
        return None

    store_payload = merchant["payload"]
    coordinates = _location(payload) or _location(store_payload)
    distance = None
    if latitude is not None and longitude is not None and coordinates is not None:
        distance = round(_distance_km(latitude, longitude, *coordinates), 3)

    price = _decimal(payload.get("price_brl"))
    promotion = (
        payload.get("promotion") if isinstance(payload.get("promotion"), dict) else {}
    )
    stock_quantity = payload.get("stock_quantity")
    in_stock = payload.get("available", True)
    if isinstance(stock_quantity, int):
        in_stock = in_stock and stock_quantity > 0

    return {
        "id": str(item["id"]),
        "store_id": store_id,
        "store_name": store_payload.get("name") or store_payload.get("legal_name"),
        "sku": payload.get("sku"),
        "name": payload.get("name"),
        "description": payload.get("description"),
        "category": payload.get("category"),
        "subcategory": payload.get("subcategory"),
        "brand": payload.get("brand"),
        "price_brl": str(price) if price is not None else None,
        "currency": payload.get("currency") or "BRL",
        "image_url": payload.get("image_url"),
        "media": payload.get("media") if isinstance(payload.get("media"), list) else [],
        "tags": payload.get("tags") if isinstance(payload.get("tags"), list) else [],
        "rating": payload.get("rating"),
        "review_count": payload.get("review_count", 0),
        "in_stock": bool(in_stock),
        "stock_quantity": stock_quantity,
        "distance_km": distance,
        "promotion": promotion or None,
        "sponsored": bool(promotion.get("sponsored") or payload.get("sponsored")),
        "published_at": payload.get("published_at") or item.get("updated_at"),
    }


def _catalog_items(
    store: Any,
    *,
    query: str | None = None,
    category: str | None = None,
    store_id: UUID | None = None,
    min_price_brl: Decimal | None = None,
    max_price_brl: Decimal | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float | None = None,
    in_stock_only: bool = True,
) -> list[dict[str, Any]]:
    stores = _store_index(store)
    normalized_query = query.casefold().strip() if query else None
    normalized_category = category.casefold().strip() if category else None
    result: list[dict[str, Any]] = []

    for raw in store.list("products"):
        payload = raw["payload"]
        if store_id is not None and str(payload.get("store_id")) != str(store_id):
            continue
        if normalized_query and normalized_query not in _text_blob(payload):
            continue
        if (
            normalized_category
            and str(payload.get("category") or "").casefold() != normalized_category
        ):
            continue

        price = _decimal(payload.get("price_brl"))
        if price is None:
            continue
        if min_price_brl is not None and price < min_price_brl:
            continue
        if max_price_brl is not None and price > max_price_brl:
            continue

        exposed = _public_product(
            raw,
            stores,
            latitude=latitude,
            longitude=longitude,
        )
        if exposed is None:
            continue
        if in_stock_only and not exposed["in_stock"]:
            continue
        if radius_km is not None:
            if exposed["distance_km"] is None or exposed["distance_km"] > radius_km:
                continue
        result.append(exposed)
    return result


def _sort_catalog(items: list[dict[str, Any]], sort: str) -> list[dict[str, Any]]:
    if sort == "price_asc":
        return sorted(
            items, key=lambda item: _decimal(item["price_brl"]) or Decimal("Infinity")
        )
    if sort == "price_desc":
        return sorted(
            items,
            key=lambda item: _decimal(item["price_brl"]) or Decimal("-Infinity"),
            reverse=True,
        )
    if sort == "distance":
        return sorted(
            items,
            key=lambda item: (
                item["distance_km"] is None,
                item["distance_km"]
                if item["distance_km"] is not None
                else float("inf"),
            ),
        )
    if sort == "rating":
        return sorted(
            items,
            key=lambda item: (
                float(item["rating"] or 0),
                int(item["review_count"] or 0),
            ),
            reverse=True,
        )
    return sorted(
        items,
        key=lambda item: (
            bool(item["sponsored"]),
            item["published_at"] or "",
        ),
        reverse=True,
    )


def _workspace(
    store: Any, actor: Actor, kind: Literal["cart", "favorites"]
) -> dict[str, Any]:
    for item in store.list("carts", str(actor.user_id)):
        if item["payload"].get("cart_type") == kind:
            return item
    return store.create(
        "carts",
        str(actor.user_id),
        None,
        "active",
        {"cart_type": kind, "items": []},
        str(actor.user_id),
        (),
        f"marketplace.{kind}.created",
        f"marketplace-{kind}-{actor.user_id}",
    )


def _public_product_or_404(store: Any, product_id: UUID) -> dict[str, Any]:
    product = store.get("products", str(product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado.")
    exposed = _public_product(product, _store_index(store))
    if exposed is None:
        raise HTTPException(status_code=409, detail="Produto indisponivel para compra.")
    return exposed


def _cart_response(store: Any, workspace: dict[str, Any]) -> dict[str, Any]:
    raw_items = workspace["payload"].get("items")
    if not isinstance(raw_items, list):
        raw_items = []
    items: list[dict[str, Any]] = []
    total = Decimal("0")
    unavailable = 0
    stores = _store_index(store)

    for raw in raw_items:
        if not isinstance(raw, dict):
            continue
        product_id = raw.get("product_id")
        quantity = raw.get("quantity")
        if not product_id or not isinstance(quantity, int) or quantity < 1:
            continue
        product = store.get("products", str(product_id))
        exposed = _public_product(product, stores) if product is not None else None
        if exposed is None or not exposed["in_stock"]:
            unavailable += 1
            items.append(
                {
                    "product_id": str(product_id),
                    "quantity": quantity,
                    "available": False,
                }
            )
            continue
        unit_price = _decimal(exposed["price_brl"]) or Decimal("0")
        subtotal = unit_price * quantity
        total += subtotal
        items.append(
            {
                "product_id": str(product_id),
                "quantity": quantity,
                "available": True,
                "name": exposed["name"],
                "image_url": exposed["image_url"],
                "unit_price_brl": str(unit_price),
                "subtotal_brl": str(subtotal),
                "store_id": exposed["store_id"],
            }
        )

    return {
        "id": str(workspace["id"]),
        "status": workspace["status"],
        "items": items,
        "items_count": sum(item["quantity"] for item in items),
        "unavailable_items": unavailable,
        "total_brl": str(total),
        "currency": "BRL",
    }


@app.get("/valley/marketplace/catalog")
def marketplace_catalog(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    category: str | None = Query(default=None, min_length=1, max_length=80),
    store_id: UUID | None = None,
    min_price_brl: Decimal | None = Query(default=None, ge=0),
    max_price_brl: Decimal | None = Query(default=None, ge=0),
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float | None = Query(default=None, gt=0, le=200),
    in_stock_only: bool = True,
    sort: Literal[
        "relevance", "price_asc", "price_desc", "distance", "rating"
    ] = "relevance",
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    if (latitude is None) != (longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude e longitude devem ser informadas em conjunto.",
        )
    if radius_km is not None and latitude is None:
        raise HTTPException(
            status_code=422,
            detail="Filtro por raio exige latitude e longitude.",
        )
    if (
        min_price_brl is not None
        and max_price_brl is not None
        and min_price_brl > max_price_brl
    ):
        raise HTTPException(
            status_code=422,
            detail="Preco minimo nao pode ser maior que o preco maximo.",
        )

    items = _catalog_items(
        app.extra["store"],
        query=q,
        category=category,
        store_id=store_id,
        min_price_brl=min_price_brl,
        max_price_brl=max_price_brl,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        in_stock_only=in_stock_only,
    )
    ordered = _sort_catalog(items, sort)
    return {
        "items": ordered[offset : offset + limit],
        "total": len(ordered),
        "offset": offset,
        "limit": limit,
        "sort": sort,
        "filters": {
            "query": q,
            "category": category,
            "store_id": str(store_id) if store_id else None,
            "min_price_brl": str(min_price_brl) if min_price_brl is not None else None,
            "max_price_brl": str(max_price_brl) if max_price_brl is not None else None,
            "radius_km": radius_km,
            "in_stock_only": in_stock_only,
        },
    }


@app.get("/valley/feed")
def valley_feed(
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
    limit: int = Query(default=20, ge=1, le=50),
) -> dict[str, Any]:
    if (latitude is None) != (longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude e longitude devem ser informadas em conjunto.",
        )
    items = _catalog_items(
        app.extra["store"],
        latitude=latitude,
        longitude=longitude,
        in_stock_only=True,
    )
    ordered = sorted(
        items,
        key=lambda item: (
            bool(item["sponsored"]),
            int((item["promotion"] or {}).get("feed_priority") or 0),
            item["published_at"] or "",
        ),
        reverse=True,
    )[:limit]
    cards = [
        {
            **item,
            "card_type": "sponsored_product" if item["sponsored"] else "product",
            "disclosure": "Patrocinado" if item["sponsored"] else None,
            "primary_action": {
                "label": "Ver produto",
                "route": f"/marketplace/products/{item['id']}",
            },
        }
        for item in ordered
    ]
    return {"items": cards, "total": len(cards), "format": "vertical_9_16"}


@app.get("/valley/promotions/today")
def promotion_of_the_day(
    latitude: float | None = Query(default=None, ge=-90, le=90),
    longitude: float | None = Query(default=None, ge=-180, le=180),
) -> dict[str, Any]:
    if (latitude is None) != (longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude e longitude devem ser informadas em conjunto.",
        )
    today = datetime.now(UTC).date()
    candidates = _catalog_items(
        app.extra["store"],
        latitude=latitude,
        longitude=longitude,
        in_stock_only=True,
    )
    eligible: list[dict[str, Any]] = []
    for item in candidates:
        promotion = item["promotion"]
        if not isinstance(promotion, dict) or not promotion.get("active", False):
            continue
        starts_on = _iso_date(promotion.get("starts_at"))
        ends_on = _iso_date(promotion.get("ends_at"))
        if starts_on and today < starts_on:
            continue
        if ends_on and today > ends_on:
            continue
        eligible.append(item)

    if not eligible:
        return {
            "active": False,
            "promotion": None,
            "reason": "Nenhuma promocao elegivel no contexto atual.",
        }

    winner = max(
        eligible,
        key=lambda item: (
            bool(item["sponsored"]),
            int((item["promotion"] or {}).get("priority") or 0),
            _decimal((item["promotion"] or {}).get("discount_percent")) or Decimal("0"),
        ),
    )
    return {
        "active": True,
        "promotion": {
            **winner,
            "disclosure": "Conteudo promocional"
            if winner["sponsored"]
            else "Promocao do dia",
            "dismissible": True,
            "destination_route": f"/marketplace/products/{winner['id']}",
        },
    }


@app.get("/valley/favorites")
def list_favorites(actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
    store = app.extra["store"]
    workspace = _workspace(store, actor, "favorites")
    product_ids = workspace["payload"].get("items")
    if not isinstance(product_ids, list):
        product_ids = []
    stores = _store_index(store)
    items: list[dict[str, Any]] = []
    unavailable: list[str] = []
    for product_id in product_ids:
        product = store.get("products", str(product_id))
        exposed = _public_product(product, stores) if product is not None else None
        if exposed is None:
            unavailable.append(str(product_id))
        else:
            items.append(exposed)
    return {
        "items": items,
        "total": len(items),
        "unavailable_product_ids": unavailable,
    }


@app.put("/valley/favorites/{product_id}")
def add_favorite(
    product_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    store = app.extra["store"]
    exposed = _public_product_or_404(store, product_id)
    workspace = _workspace(store, actor, "favorites")
    product_ids = workspace["payload"].get("items")
    if not isinstance(product_ids, list):
        product_ids = []
    normalized = [str(item) for item in product_ids]
    if str(product_id) not in normalized:
        normalized.append(str(product_id))
        payload = {**workspace["payload"], "items": normalized}
        store.update(
            workspace,
            payload,
            "active",
            str(actor.user_id),
            "favorite_add",
            "marketplace.favorite.added",
        )
    return {"saved": True, "product": exposed}


@app.delete("/valley/favorites/{product_id}")
def remove_favorite(
    product_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    store = app.extra["store"]
    workspace = _workspace(store, actor, "favorites")
    product_ids = workspace["payload"].get("items")
    if not isinstance(product_ids, list):
        product_ids = []
    normalized = [str(item) for item in product_ids if str(item) != str(product_id)]
    if len(normalized) != len(product_ids):
        payload = {**workspace["payload"], "items": normalized}
        store.update(
            workspace,
            payload,
            "active",
            str(actor.user_id),
            "favorite_remove",
            "marketplace.favorite.removed",
        )
    return {"saved": False, "product_id": str(product_id)}


@app.get("/valley/cart")
def get_cart(actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
    store = app.extra["store"]
    return _cart_response(store, _workspace(store, actor, "cart"))


@app.put("/valley/cart/items/{product_id}")
def put_cart_item(
    product_id: UUID,
    body: CartItemRequest,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    store = app.extra["store"]
    _public_product_or_404(store, product_id)
    workspace = _workspace(store, actor, "cart")
    raw_items = workspace["payload"].get("items")
    if not isinstance(raw_items, list):
        raw_items = []
    updated: list[dict[str, Any]] = []
    replaced = False
    for item in raw_items:
        if isinstance(item, dict) and str(item.get("product_id")) == str(product_id):
            updated.append({"product_id": str(product_id), "quantity": body.quantity})
            replaced = True
        elif isinstance(item, dict):
            updated.append(item)
    if not replaced:
        updated.append({"product_id": str(product_id), "quantity": body.quantity})
    payload = {**workspace["payload"], "items": updated}
    workspace = store.update(
        workspace,
        payload,
        "active",
        str(actor.user_id),
        "cart_item_put",
        "marketplace.cart.item.updated",
    )
    return _cart_response(store, workspace)


@app.delete("/valley/cart/items/{product_id}")
def delete_cart_item(
    product_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    store = app.extra["store"]
    workspace = _workspace(store, actor, "cart")
    raw_items = workspace["payload"].get("items")
    if not isinstance(raw_items, list):
        raw_items = []
    updated = [
        item
        for item in raw_items
        if not isinstance(item, dict) or str(item.get("product_id")) != str(product_id)
    ]
    if len(updated) != len(raw_items):
        payload = {**workspace["payload"], "items": updated}
        workspace = store.update(
            workspace,
            payload,
            "active",
            str(actor.user_id),
            "cart_item_delete",
            "marketplace.cart.item.removed",
        )
    return _cart_response(store, workspace)


@app.post("/valley/orders/{order_id}/support", status_code=201)
def create_order_support_case(
    order_id: UUID,
    body: SupportCaseRequest,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    store = app.extra["store"]
    order = store.get("orders", str(order_id))
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado.")
    if str(order["user_id"]) != str(actor.user_id):
        raise HTTPException(
            status_code=403, detail="Pedido nao pertence ao consumidor autenticado."
        )
    if order["status"] not in {
        "paid",
        "accepted",
        "in_progress",
        "delivered",
        "completed",
    }:
        raise HTTPException(
            status_code=409,
            detail="Suporte fica disponivel apos a confirmacao do pedido.",
        )

    payload = order.get("payload") if isinstance(order.get("payload"), dict) else {}
    case = store.create(
        "disputes",
        str(actor.user_id),
        payload.get("store_id") or payload.get("company_id"),
        "open",
        {
            "order_id": str(order_id),
            "store_id": payload.get("store_id"),
            "company_id": payload.get("company_id"),
            "offer_id": payload.get("offer_id") or payload.get("valley_offer_id"),
            "case_type": body.kind,
            "subject": body.subject
            or ("Suporte ao pedido" if body.kind == "support" else "Disputa do pedido"),
            "message": body.message,
            "desired_resolution": body.desired_resolution,
        },
        str(actor.user_id),
        (),
        "support.ticket.created"
        if body.kind == "support"
        else "marketplace.dispute.created",
        body.idempotency_key,
    )
    return {
        "id": case["id"],
        "order_id": str(order_id),
        "kind": body.kind,
        "status": case["status"],
        "message": "Caso registrado. Nossa equipe acompanha o retorno.",
    }


@app.get("/valley/reviews")
def public_reviews(
    store_id: str | None = None,
    company_id: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    store = app.extra["store"]
    reviews = store.list("reviews")

    filtered_reviews = []
    for review in reviews:
        payload = review.get("payload", {})
        if store_id and str(payload.get("store_id")) != store_id:
            continue
        if company_id and str(payload.get("company_id")) != company_id:
            continue

        filtered_reviews.append(
            {
                "id": review["id"],
                "rating": payload.get("rating"),
                "comment": payload.get("comment"),
                "created_at": review["created_at"],
                "author_initials": "Anonimo",  # A deeper integration would fetch user data
            }
        )

    return {
        "reviews": filtered_reviews[:limit],
        "total": len(filtered_reviews),
    }


@app.get("/valley/insights/commercial")
def commercial_insights(actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
    store = app.extra["store"]
    orders = store.list("orders")
    reviews = store.list("reviews")
    disputes = store.list("disputes")

    paid_orders = [
        item
        for item in orders
        if item["status"]
        in {"paid", "accepted", "in_progress", "delivered", "completed"}
    ]
    completed_orders = [
        item for item in orders if item["status"] in {"delivered", "completed"}
    ]
    resolved_cases = [
        item for item in disputes if item["status"] in {"resolved", "closed"}
    ]
    open_cases = [
        item for item in disputes if item["status"] in {"open", "under_review"}
    ]
    published_reviews = [item for item in reviews if item["status"] == "published"]
    pending_reviews = [item for item in reviews if item["status"] == "pending_review"]
    ratings = [
        int(item["payload"].get("rating"))
        for item in published_reviews
        if str(item["payload"].get("rating") or "").isdigit()
    ]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
    conversion_rate = (
        round((len(paid_orders) / len(orders)) * 100, 2) if orders else 0.0
    )

    return {
        "orders_total": len(orders),
        "orders_paid": len(paid_orders),
        "orders_completed": len(completed_orders),
        "reviews_total": len(reviews),
        "reviews_published": len(published_reviews),
        "reviews_pending_moderation": len(pending_reviews),
        "average_rating": average_rating,
        "support_cases_total": len(disputes),
        "support_cases_open": len(open_cases),
        "support_cases_resolved": len(resolved_cases),
        "conversion_rate_percent": conversion_rate,
        "source": "marketplace.commercial_insights",
        "actor": str(actor.user_id),
    }
