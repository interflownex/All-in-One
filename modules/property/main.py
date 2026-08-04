from pathlib import Path
import sys
from typing import Any

from fastapi import Query

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app


app = create_module_app("property")

PUBLIC_PROPERTY_STATUSES = frozenset(
    {"active", "approved", "available", "published"}
)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _money(value: Any) -> float | None:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount if amount >= 0 else None


def _public_item(resource_type: str, item: dict[str, Any]) -> dict[str, Any] | None:
    if str(item.get("status") or "").casefold() not in PUBLIC_PROPERTY_STATUSES:
        return None
    payload = item.get("payload")
    if not isinstance(payload, dict):
        return None
    if payload.get("public_listing") is False:
        return None

    title = _text(payload.get("title") or payload.get("name"))
    if not title:
        return None
    address = payload.get("address")
    if isinstance(address, dict):
        public_address = ", ".join(
            part
            for part in (
                _text(address.get("neighborhood")),
                _text(address.get("city")),
                _text(address.get("state")),
            )
            if part
        )
    else:
        public_address = _text(address)

    return {
        "id": str(item.get("id") or ""),
        "resource_type": resource_type,
        "title": title,
        "description": _text(payload.get("description")),
        "property_type": _text(
            payload.get("property_type") or payload.get("unit_type") or payload.get("type")
        ),
        "region": _text(
            payload.get("region") or payload.get("city") or public_address
        ),
        "public_address": public_address,
        "rent_amount": _money(
            payload.get("rent_amount") or payload.get("price_amount")
        ),
        "bedrooms": payload.get("bedrooms"),
        "bathrooms": payload.get("bathrooms"),
        "area_m2": payload.get("area_m2"),
        "image_url": _text(
            payload.get("primary_image_url") or payload.get("image_url")
        ) or None,
        "available_from": payload.get("available_from"),
    }


@app.get("/valley/catalog")
def valley_property_catalog(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    region: str | None = Query(default=None, min_length=1, max_length=120),
    property_type: str | None = Query(default=None, min_length=1, max_length=80),
    max_price_brl: float | None = Query(default=None, ge=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=30, ge=1, le=100),
) -> dict[str, Any]:
    store = app.extra["store"]
    query = q.casefold().strip() if q else None
    normalized_region = region.casefold().strip() if region else None
    normalized_type = property_type.casefold().strip() if property_type else None
    items: list[dict[str, Any]] = []

    for resource_type in ("properties", "units"):
        for raw in store.list(resource_type):
            item = _public_item(resource_type, raw)
            if item is None:
                continue
            blob = " ".join(
                _text(item.get(field))
                for field in (
                    "title",
                    "description",
                    "property_type",
                    "region",
                    "public_address",
                )
            ).casefold()
            if query and query not in blob:
                continue
            if normalized_region and normalized_region not in _text(item["region"]).casefold():
                continue
            if normalized_type and normalized_type not in _text(item["property_type"]).casefold():
                continue
            price = item.get("rent_amount")
            if max_price_brl is not None and price is not None and price > max_price_brl:
                continue
            items.append(item)

    items.sort(
        key=lambda item: (
            item.get("available_from") or "",
            item.get("title") or "",
        ),
        reverse=True,
    )
    return {
        "items": items[offset : offset + limit],
        "total": len(items),
        "offset": offset,
        "limit": limit,
    }


# O runtime genérico registra rotas dinâmicas como ``/{resource_type}`` antes
# das especializações do módulo. A rota estática precisa ser avaliada primeiro
# para que ``/valley/catalog`` não seja interpretada como uma listagem genérica.
for route_index, route in enumerate(app.router.routes):
    if getattr(route, "path", None) == "/valley/catalog":
        app.router.routes.insert(0, app.router.routes.pop(route_index))
        break
