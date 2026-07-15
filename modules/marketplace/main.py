from pathlib import Path
import sys
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
        raise HTTPException(status_code=403, detail="Pedido nao pertence ao consumidor autenticado.")
    if order["status"] not in {"paid", "accepted", "in_progress", "delivered", "completed"}:
        raise HTTPException(status_code=409, detail="Suporte fica disponivel apos a confirmacao do pedido.")

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
            "subject": body.subject or ("Suporte ao pedido" if body.kind == "support" else "Disputa do pedido"),
            "message": body.message,
            "desired_resolution": body.desired_resolution,
        },
        str(actor.user_id),
        (),
        "support.ticket.created" if body.kind == "support" else "marketplace.dispute.created",
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

    paid_orders = [item for item in orders if item["status"] in {"paid", "accepted", "in_progress", "delivered", "completed"}]
    completed_orders = [item for item in orders if item["status"] in {"delivered", "completed"}]
    resolved_cases = [item for item in disputes if item["status"] in {"resolved", "closed"}]
    open_cases = [item for item in disputes if item["status"] in {"open", "under_review"}]
    published_reviews = [item for item in reviews if item["status"] == "published"]
    pending_reviews = [item for item in reviews if item["status"] == "pending_review"]
    ratings = [
        int(item["payload"].get("rating"))
        for item in published_reviews
        if str(item["payload"].get("rating") or "").isdigit()
    ]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
    conversion_rate = round((len(paid_orders) / len(orders)) * 100, 2) if orders else 0.0

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
