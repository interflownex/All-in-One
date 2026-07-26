"""Módulo Document/GED ECM – Primícia 17: Documento Vivo de Obrigações."""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Body, Depends, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.feature_flags import is_flag_enabled, require_flag
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers
from ._primicias import router as primacia_router

app = create_module_app("document")

_FLAG = "primicia.document.living_obligations"


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/obligations", status_code=201)
async def create_obligation(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Vincula obrigação a cláusula de documento. IA cria rascunho até revisão humana."""
    _require_flag(actor)
    document_id = body.get("document_id")
    title = body.get("title")
    if not document_id or not title:
        raise HTTPException(status_code=422, detail="document_id e title são obrigatórios.")

    ai_generated = body.get("ai_generated", False)
    oid = str(uuid4())
    payload = {
        "id": oid,
        "document_id": str(document_id),
        "anchor": {
            "page_number": body.get("page_number"),
            "section_ref": body.get("section_ref"),
            "clause_text": body.get("clause_text", ""),
        },
        "title": str(title)[:256],
        "description": body.get("description", ""),
        "obligation_type": body.get("obligation_type", "compliance"),
        "status": "pending",
        "ai_generated": ai_generated,
        "reviewed": not ai_generated,  # IA exige revisão; manual já é revisado
        "responsible_id": body.get("responsible_id"),
        "due_date": body.get("due_date"),
        "created_at": _now(),
    }
    if ai_generated:
        payload["disclaimer"] = "Obrigação gerada por IA. Sujeita a revisão humana antes de ser considerada oficial."

    try:
        return _store().create("document_obligations", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "pending", payload, str(actor.user_id), ("id",), "document.obligation.detected" if ai_generated else "document.obligation.reviewed", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/obligations/{obligation_id}/review", status_code=200)
async def review_obligation(
    obligation_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Revisor humano aprova ou rejeita obrigação gerada por IA."""
    _require_flag(actor)
    decision = body.get("decision")
    if decision not in {"approved", "rejected", "amended"}:
        raise HTTPException(status_code=422, detail="decision deve ser: approved | rejected | amended.")
    store = _store()
    try:
        obligation = store.get("document_obligations", str(obligation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada.")
    return store.update(obligation, {"reviewed": True, "reviewed_by": str(actor.user_id), "reviewed_at": _now(), "review_decision": decision, "review_notes": body.get("notes", "")}, "reviewed", str(actor.user_id), "document.obligation.reviewed")


@app.post("/obligations/{obligation_id}/complete", status_code=200)
async def complete_obligation(
    obligation_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Marca obrigação como cumprida com evidência."""
    _require_flag(actor)
    evidence_ref = body.get("evidence_ref")
    if not evidence_ref:
        raise HTTPException(status_code=422, detail="evidence_ref é obrigatório.")
    store = _store()
    try:
        obligation = store.get("document_obligations", str(obligation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Obrigação não encontrada.")
    return store.update(obligation, {"status": "completed", "completed_at": _now(), "evidence_ref": str(evidence_ref)}, "completed", str(actor.user_id), "document.obligation.completed")


@app.get("/obligations/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Documento Vivo de Obrigações – Primícia 17"}

app.include_router(primacia_router)