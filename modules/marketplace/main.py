import sys
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers

app = create_module_app("marketplace")


class SupportCaseRequest(BaseModel):
    kind: Literal["support", "dispute"]
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=5, max_length=1000)
    desired_resolution: str | None = Field(default=None, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=120)


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


# ---------------------------------------------------------------------------
# Recurso 5: Compra em Coalizão Local (Primícia 5)
# ---------------------------------------------------------------------------

from datetime import UTC
from datetime import datetime as _mdatetime
from uuid import uuid4 as _muuid4

from shared.feature_flags import is_flag_enabled, require_flag
from _primicias import router as primacia_router

_MKT_FLAG = "primicia.marketplace.local_buying_coalition"


def _mnow() -> str:
    return _mdatetime.now(UTC).isoformat()


def _require_mkt_flag(actor) -> None:
    require_flag(_MKT_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/coalitions", status_code=201)
async def create_coalition(body: dict = Body(...), actor: Actor = Depends(actor_from_headers)) -> dict:
    """Cria coalizão de compra local com quantidade mínima, região e prazo."""
    _require_mkt_flag(actor)
    title = body.get("title")
    region = body.get("region")
    if not title or not region:
        raise HTTPException(status_code=422, detail="title e region são obrigatórios.")
    cid = str(_muuid4())
    payload = {"id": cid, "title": str(title)[:256], "description": body.get("description", ""), "organizer_id": str(actor.user_id), "region": str(region)[:128], "status": "open", "min_quantity": body.get("min_quantity", 2), "target_price": body.get("target_price"), "deadline": body.get("deadline"), "created_at": _mnow()}
    store = app.extra["store"]
    try:
        return store.create("buying_coalitions", str(actor.user_id), None, "open", payload, str(actor.user_id), ("id",), "marketplace.coalition.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/coalitions/{coalition_id}/join", status_code=201)
async def join_coalition(coalition_id, body: dict = Body({}), actor: Actor = Depends(actor_from_headers)) -> dict:
    """Usuário entra na coalizão. Localização exata nunca revelada antes do aceite."""
    _require_mkt_flag(actor)
    mid = str(_muuid4())
    payload = {"id": mid, "coalition_id": str(coalition_id), "user_id": str(actor.user_id), "quantity": body.get("quantity", 1), "status": "active", "location_approx": body.get("location_approx", ""),  # Somente bairro/cidade, NUNCA coordenada exata
               "joined_at": _mnow()}
    store = app.extra["store"]
    try:
        return store.create("coalition_members", str(actor.user_id), None, "active", payload, str(actor.user_id), ("id",), "marketplace.coalition.member_joined", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/coalitions/{coalition_id}/bids", status_code=201)
async def submit_supplier_bid(coalition_id, body: dict = Body(...), actor: Actor = Depends(actor_from_headers)) -> dict:
    """Fornecedor aprovado submete proposta para a coalizão."""
    _require_mkt_flag(actor)
    if not actor.business_id:
        raise HTTPException(status_code=403, detail="Apenas fornecedores aprovados podem submeter propostas.")
    unit_price = body.get("unit_price")
    if not unit_price:
        raise HTTPException(status_code=422, detail="unit_price é obrigatório.")
    bid_id = str(_muuid4())
    payload = {"id": bid_id, "coalition_id": str(coalition_id), "supplier_id": str(actor.business_id), "unit_price": float(unit_price), "valid_until": body.get("valid_until"), "status": "pending", "submitted_at": _mnow()}
    store = app.extra["store"]
    try:
        return store.create("supplier_bids", str(actor.user_id), str(actor.business_id), "pending", payload, str(actor.user_id), ("id",), "marketplace.supplier_bid.submitted", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/supplier-bids/{bid_id}/accept", status_code=200)
async def accept_supplier_bid(bid_id, actor: Actor = Depends(actor_from_headers)) -> dict:
    """Organizador aceita proposta do fornecedor e confirma pedido coletivo."""
    _require_mkt_flag(actor)
    store = app.extra["store"]
    try:
        bid = store.get("supplier_bids", str(bid_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Proposta não encontrada.")
    return store.update(bid, {"status": "accepted", "accepted_at": _mnow()}, "accepted", str(actor.user_id), "marketplace.supplier_bid.accepted")


@app.get("/coalitions/feature-status")
async def mkt_feature_status() -> dict:
    return {"flag": _MKT_FLAG, "enabled": is_flag_enabled(_MKT_FLAG), "description": "Compra em Coalizão Local – Primícia 5"}

app.include_router(primacia_router)