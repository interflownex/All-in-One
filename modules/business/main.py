import sys
from pathlib import Path
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from business.module_settings import router as module_settings_router
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers

app = create_module_app("business")
app.include_router(module_settings_router)


class DisputeResolutionRequest(BaseModel):
    resolution_notes: str = Field(min_length=5, max_length=1000)
    action: Literal["resolve", "close"]


@app.post("/valley/disputes/{dispute_id}/resolve", status_code=200)
def resolve_dispute(
    dispute_id: UUID,
    body: DisputeResolutionRequest,
    actor: Annotated[Actor, Depends(actor_from_headers)],
) -> dict[str, Any]:
    store = app.extra["store"]
    dispute = store.get("disputes", str(dispute_id))
    if not dispute:
        raise HTTPException(status_code=404, detail="Disputa nao encontrada.")

    payload = dict(dispute.get("payload", {}))
    if actor.business_id is None or str(payload.get("company_id")) != str(
        actor.business_id
    ):
        raise HTTPException(
            status_code=403, detail="Disputa nao pertence a empresa do ator."
        )

    status = "resolved" if body.action == "resolve" else "closed"
    payload["resolution_notes"] = body.resolution_notes

    case = store.update(
        item=dispute,
        payload=payload,
        status=status,
        actor=str(actor.user_id),
        action="resolve_dispute",
        event=f"business.dispute.{status}",
    )

    return {
        "id": case["id"],
        "status": case["status"],
        "message": f"Disputa {status} com sucesso.",
    }
