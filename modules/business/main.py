"""Módulo Business – Primícia 2: Consórcio Relâmpago Empresarial."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Body, Depends, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from business.module_settings import router as module_settings_router
from shared.feature_flags import is_flag_enabled, require_flag
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers
from ._primicias import router as primacia_router

app = create_module_app("business")
app.include_router(module_settings_router)
app.include_router(primacia_router)

_FLAG = "primicia.business.flash_consortium"


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(
        _FLAG,
        tenant_id=str(actor.business_id) if actor.business_id else None,
        user_id=str(actor.user_id),
    )


def _require_approved_company(actor: Actor) -> None:
    if not actor.business_id:
        raise HTTPException(
            status_code=403,
            detail="Apenas empresas aprovadas podem participar de consórcios.",
        )
    if actor.business_status not in {"active", "approved", "verified", None}:
        raise HTTPException(
            status_code=403,
            detail=f"Empresa com status '{actor.business_status}' não autorizada para consórcios.",
        )


@app.post("/opportunities", status_code=201)
async def create_opportunity(
    body: dict[str, Any] = Body(...), actor: Actor = Depends(actor_from_headers)
) -> dict[str, Any]:
    """Cria oportunidade de negócio para formação de consórcio."""
    _require_flag(actor)
    _require_approved_company(actor)
    title = body.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="title é obrigatório.")
    opp_id = str(uuid4())
    payload = {
        "id": opp_id,
        "title": str(title)[:256],
        "description": body.get("description", ""),
        "owner_id": str(actor.user_id),
        "status": "draft",
        "deadline": body.get("deadline"),
        "min_members": body.get("min_members", 2),
        "max_members": body.get("max_members"),
        "created_at": _now(),
    }
    try:
        return _store().create(
            "business_opportunities",
            str(actor.user_id),
            str(actor.business_id),
            "draft",
            payload,
            str(actor.user_id),
            ("id",),
            "business.consortium.created",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/opportunities/{opp_id}/consortia", status_code=201)
async def form_consortium(
    opp_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria consórcio temporário vinculado a uma oportunidade."""
    _require_flag(actor)
    _require_approved_company(actor)
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=422, detail="name do consórcio é obrigatório.")
    cid = str(uuid4())
    payload = {
        "id": cid,
        "opportunity_id": str(opp_id),
        "name": str(name)[:256],
        "status": "forming",
        "created_at": _now(),
    }
    try:
        return _store().create(
            "temporary_consortia",
            str(actor.user_id),
            str(actor.business_id),
            "forming",
            payload,
            str(actor.user_id),
            ("id",),
            "business.consortium.activated",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/consortia/{consortium_id}/invite", status_code=201)
async def invite_member(
    consortium_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Convida empresa verificada para o consórcio."""
    _require_flag(actor)
    company_id = body.get("company_id")
    if not company_id:
        raise HTTPException(status_code=422, detail="company_id é obrigatório.")
    mid = str(uuid4())
    payload = {
        "id": mid,
        "consortium_id": str(consortium_id),
        "company_id": str(company_id),
        "role": body.get("role", "member"),
        "status": "invited",
        "invited_at": _now(),
    }
    try:
        return _store().create(
            "consortium_members",
            str(actor.user_id),
            str(actor.business_id),
            "invited",
            payload,
            str(actor.user_id),
            ("id",),
            "business.consortium.member_invited",
            None,
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/consortium-members/{member_id}/accept", status_code=200)
async def accept_membership(
    member_id: UUID, actor: Actor = Depends(actor_from_headers)
) -> dict[str, Any]:
    """Empresa aceita convite e responsabilidades."""
    _require_flag(actor)
    _require_approved_company(actor)
    store = _store()
    try:
        member = store.get("consortium_members", str(member_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Membro não encontrado.")
    return store.update(
        member,
        {"status": "accepted", "accepted_at": _now()},
        "accepted",
        str(actor.user_id),
        "business.consortium.member_accepted",
    )


@app.post("/consortia/{consortium_id}/revenue-split", status_code=201)
async def define_revenue_split(
    consortium_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Define split de receita. Percentuais devem somar 100%."""
    _require_flag(actor)
    splits = body.get("splits", [])
    total_pct = sum(float(s.get("percentage", 0)) for s in splits)
    if abs(total_pct - 100.0) > 0.01:
        raise HTTPException(
            status_code=422,
            detail=f"Percentuais devem somar 100%. Soma atual: {total_pct}%.",
        )
    rsid = str(uuid4())
    payload = {
        "id": rsid,
        "consortium_id": str(consortium_id),
        "splits": splits,
        "created_at": _now(),
    }
    try:
        return _store().create(
            "consortium_revenue_splits",
            str(actor.user_id),
            str(actor.business_id),
            "pending_approval",
            payload,
            str(actor.user_id),
            ("id",),
            "business.consortium.agreement_signed",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/consortia/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Consórcio Relâmpago Empresarial – Primícia 2",
    }
