"""Módulo CRM – Primícia 15: Livro de Promessas ao Cliente."""
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

app = create_module_app("crm")

_FLAG = "primicia.crm.customer_promises"


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/promises", status_code=201)
async def create_promise(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra uma promessa feita ao cliente.

    Se source_type == 'ai_suggested', é obrigatória revisão humana.
    """
    _require_flag(actor)
    customer_id = body.get("customer_id")
    title = body.get("title")
    if not customer_id or not title:
        raise HTTPException(status_code=422, detail="customer_id e title são obrigatórios.")

    source_type = body.get("source_type", "manual")
    if source_type not in {"manual", "ai_suggested", "extracted"}:
        raise HTTPException(status_code=422, detail="source_type inválido.")

    promise_id = str(uuid4())
    due_date = body.get("due_date")
    responsible_id = body.get("responsible_id", str(actor.user_id))

    payload = {
        "id": promise_id,
        "tenant_id": str(actor.business_id) if actor.business_id else None,
        "customer_id": str(customer_id),
        "title": str(title)[:256],
        "description": body.get("description", ""),
        "source_type": source_type,
        "status": "open",
        "confirmed": False,
        "requires_review": source_type in {"ai_suggested", "extracted"},
        "responsible_id": str(responsible_id),
        "due_date": due_date,
        "created_at": _now(),
    }
    try:
        return _store().create("customer_promises", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "open", payload, str(actor.user_id), ("id",), "crm.promise.detected" if source_type != "manual" else "crm.promise.confirmed", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/promises/{promise_id}/assign", status_code=200)
async def assign_promise(
    promise_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Atribui um responsável e prazo à promessa."""
    _require_flag(actor)
    owner_id = body.get("owner_id")
    due_date = body.get("due_date")
    if not owner_id or not due_date:
        raise HTTPException(status_code=422, detail="owner_id e due_date são obrigatórios.")

    store = _store()
    try:
        promise = store.get("customer_promises", str(promise_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Promessa não encontrada.")

    return store.update(promise, {"status": "open", "responsible_id": str(owner_id), "due_date": str(due_date)}, "open", str(actor.user_id), "crm.promise.assigned")


@app.post("/promises/{promise_id}/fulfill", status_code=200)
async def fulfill_promise(
    promise_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Marca promessa como cumprida com evidência."""
    _require_flag(actor)
    evidence_ref = body.get("evidence_ref")
    if not evidence_ref:
        raise HTTPException(status_code=422, detail="evidence_ref é obrigatório para comprovar cumprimento.")

    store = _store()
    try:
        promise = store.get("customer_promises", str(promise_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Promessa não encontrada.")

    if promise.get("status") in {"fulfilled", "revoked"}:
        raise HTTPException(status_code=409, detail=f"Promessa já está em estado '{promise.get('status')}'.")

    return store.update(promise, {"status": "fulfilled", "fulfilled_at": _now(), "evidence_ref": str(evidence_ref)}, "fulfilled", str(actor.user_id), "crm.promise.fulfilled")


@app.post("/promises/{promise_id}/breach", status_code=200)
async def register_breach(
    promise_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra descumprimento de promessa. Promessa rompida NÃO é apagada."""
    _require_flag(actor)
    reason = body.get("reason", "")
    store = _store()
    try:
        promise = store.get("customer_promises", str(promise_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Promessa não encontrada.")

    return store.update(promise, {"status": "breached", "breached_at": _now(), "breach_reason": reason}, "breached", str(actor.user_id), "crm.promise.breached")


@app.post("/promises/{promise_id}/customer-confirm", status_code=200)
async def customer_confirm_promise(
    promise_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cliente confirma cumprimento da promessa."""
    _require_flag(actor)
    store = _store()
    try:
        promise = store.get("customer_promises", str(promise_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Promessa não encontrada.")

    customer_id = promise.get("payload", {}).get("customer_id")
    if str(actor.user_id) != str(customer_id) and "administrator" not in actor.roles:
        raise HTTPException(status_code=403, detail="Apenas o cliente pode confirmar o cumprimento.")

    return store.update(promise, {"confirmed": True, "confirmed_at": _now(), "confirmed_by": str(actor.user_id), "channel": body.get("channel", "platform")}, "fulfilled", str(actor.user_id), "crm.promise.customer_confirmed")


@app.get("/promises")
async def list_promises(actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
    """Lista promessas da empresa/tenant."""
    _require_flag(actor)
    return _store().list("customer_promises", str(actor.user_id), str(actor.business_id) if actor.business_id else None, page=1, page_size=50)


@app.get("/promises/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Livro de Promessas ao Cliente – Primícia 15"}

app.include_router(primacia_router)