import sys
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers

app = create_module_app("crm")


@app.get("/valley/crm/customer-profiles/{user_id}/tickets")
def customer_ticket_profile(
    user_id: UUID,
    actor: Annotated[Actor, Depends(actor_from_headers)],
) -> dict[str, Any]:
    if actor.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="O perfil solicitado nao pertence ao ator autenticado.",
        )
    store = app.extra["store"]
    disputes = store.list("disputes", user_id=str(user_id))
    reviews = store.list("reviews", user_id=str(user_id))

    open_tickets = [d for d in disputes if d["status"] in {"open", "under_review"}]
    resolved_tickets = [d for d in disputes if d["status"] in {"resolved", "closed"}]

    return {
        "customer_user_id": str(user_id),
        "total_interactions": len(disputes) + len(reviews),
        "tickets": {
            "total": len(disputes),
            "open": len(open_tickets),
            "resolved": len(resolved_tickets),
            "history": [
                {
                    "id": d["id"],
                    "status": d["status"],
                    "created_at": d["created_at"],
                    "subject": d.get("payload", {}).get("subject", "N/A"),
                }
                for d in disputes
            ],
        },
        "reviews": {
            "total": len(reviews),
            "history": [
                {
                    "id": r["id"],
                    "rating": r.get("payload", {}).get("rating"),
                    "created_at": r["created_at"],
                }
                for r in reviews
            ],
        },
    }
