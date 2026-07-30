from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from shared.security import Actor, actor_from_headers

router = APIRouter()


@router.get("/valley/crm/customer-profiles/{user_id}/tickets")
def customer_ticket_profile(
    user_id: UUID,
    request: Request,
    actor: Annotated[Actor, Depends(actor_from_headers)],
) -> dict[str, Any]:
    if actor.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="O perfil solicitado nao pertence ao ator autenticado.",
        )
    store = request.app.extra["store"]
    disputes = store.list("disputes", user_id=str(user_id))
    reviews = store.list("reviews", user_id=str(user_id))
    open_tickets = [
        item for item in disputes if item["status"] in {"open", "under_review"}
    ]
    resolved_tickets = [
        item for item in disputes if item["status"] in {"resolved", "closed"}
    ]
    return {
        "customer_user_id": str(user_id),
        "total_interactions": len(disputes) + len(reviews),
        "tickets": {
            "total": len(disputes),
            "open": len(open_tickets),
            "resolved": len(resolved_tickets),
            "history": [
                {
                    "id": item["id"],
                    "status": item["status"],
                    "created_at": item["created_at"],
                    "subject": item.get("payload", {}).get("subject", "N/A"),
                }
                for item in disputes
            ],
        },
        "reviews": {
            "total": len(reviews),
            "history": [
                {
                    "id": item["id"],
                    "rating": item.get("payload", {}).get("rating"),
                    "created_at": item["created_at"],
                }
                for item in reviews
            ],
        },
    }
