"""Módulo Legal – Primícia 20: Radar de Efeito Jurídico em Cadeia."""
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
from _primicias import router as primacia_router

app = create_module_app("legal")

_FLAG = "primicia.legal.impact_radar"


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/legal-changes", status_code=201)
async def register_legal_change(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra mudança jurídica ou regulatória com fonte e data obrigatórias."""
    _require_flag(actor)
    title = body.get("title")
    source = body.get("source")
    source_date = body.get("source_date")
    change_type = body.get("change_type", "legislation")
    if not title or not source or not source_date:
        raise HTTPException(status_code=422, detail="title, source e source_date são obrigatórios.")
    lcid = str(uuid4())
    payload = {"id": lcid, "title": str(title)[:512], "change_type": change_type, "source": str(source), "source_date": str(source_date), "urgency": body.get("urgency", "normal"), "description": body.get("description", ""), "created_by": str(actor.user_id), "created_at": _now()}
    try:
        return _store().create("legal_change_records", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "registered", payload, str(actor.user_id), ("id",), "legal.change.registered", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/legal-changes/{change_id}/impact", status_code=201)
async def suggest_impact(
    change_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """IA indica impacto provável. Não é parecer final – requer revisão profissional."""
    _require_flag(actor)
    entity_type = body.get("entity_type")
    entity_id = body.get("entity_id")
    if not entity_type or not entity_id:
        raise HTTPException(status_code=422, detail="entity_type e entity_id são obrigatórios.")
    link_id = str(uuid4())
    payload = {"id": link_id, "change_id": str(change_id), "entity_type": str(entity_type), "entity_id": str(entity_id), "impact_level": body.get("impact_level", "possible"), "ai_suggested": body.get("ai_suggested", True), "notes": body.get("notes", ""), "linked_at": _now(), "disclaimer": "Indicação de impacto provável por IA. Não constitui parecer jurídico. Sujeito a revisão profissional."}
    try:
        return _store().create("legal_impact_links", str(actor.user_id), None, "suggested", payload, str(actor.user_id), ("id",), "legal.impact.suggested", None)
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/legal-changes/{change_id}/action-plan", status_code=201)
async def create_action_plan(
    change_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria plano de ação para mudança jurídica. Nenhuma alteração contratual automática."""
    _require_flag(actor)
    title = body.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="title é obrigatório.")
    apid = str(uuid4())
    payload = {"id": apid, "change_id": str(change_id), "title": str(title)[:256], "status": "draft", "actions": body.get("actions", []), "created_at": _now()}
    try:
        return _store().create("legal_action_plans", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "draft", payload, str(actor.user_id), ("id",), "legal.action_plan.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/legal-changes/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Radar de Efeito Jurídico em Cadeia – Primícia 20"}

app.include_router(primacia_router)