"""Módulo HR – Primícia 18: Escala de Afinidade Justa."""
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

app = create_module_app("hr")

_FLAG = "primicia.hr.fair_affinity_schedule"

# Critérios sensíveis que não podem ser usados em escala
_SENSITIVE_CRITERIA = frozenset({"race", "religion", "gender", "age", "disability", "origin", "sexual_orientation", "pregnancy"})


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/schedule-preferences", status_code=201)
async def update_preferences(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Funcionário registra preferências voluntárias de escala."""
    _require_flag(actor)
    for crit in _SENSITIVE_CRITERIA:
        if crit in body:
            raise HTTPException(status_code=422, detail=f"Critério sensível proibido na preferência de escala: '{crit}'.")

    pref_id = str(uuid4())
    payload = {"id": pref_id, "employee_id": str(actor.user_id), "preferences": body.get("preferences", []), "voluntary": True, "updated_at": _now()}
    try:
        return _store().create("employee_schedule_preferences", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "active", payload, str(actor.user_id), ("id",), "hr.schedule_preferences.updated", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/schedule-proposals", status_code=201)
async def generate_schedule_proposal(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Gera proposta de escala considerando preferências e equilíbrio."""
    _require_flag(actor)
    period_start = body.get("period_start")
    period_end = body.get("period_end")
    if not period_start or not period_end:
        raise HTTPException(status_code=422, detail="period_start e period_end são obrigatórios.")
    prop_id = str(uuid4())
    payload = {"id": prop_id, "tenant_id": str(actor.business_id) if actor.business_id else None, "period_start": str(period_start), "period_end": str(period_end), "status": "draft", "generated_by": "algorithm", "assignments": body.get("assignments", []), "fairness_rationale": body.get("fairness_rationale", ""), "created_at": _now()}
    try:
        return _store().create("schedule_proposals", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "draft", payload, str(actor.user_id), ("id",), "hr.schedule_proposal.generated", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/schedule-proposals/{proposal_id}/approve", status_code=200)
async def approve_schedule(
    proposal_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Gestor aprova proposta de escala antes da publicação."""
    _require_flag(actor)
    if "hr_manager" not in actor.roles and "administrator" not in actor.roles:
        raise HTTPException(status_code=403, detail="Apenas gestores de RH podem aprovar escalas.")
    store = _store()
    try:
        proposal = store.get("schedule_proposals", str(proposal_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Proposta não encontrada.")
    return store.update(proposal, {"status": "approved", "approved_by": str(actor.user_id), "approved_at": _now()}, "approved", str(actor.user_id), "hr.schedule_proposal.approved")


@app.post("/schedule-assignments/{assignment_id}/contest", status_code=201)
async def contest_schedule(
    assignment_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Funcionário contesta alocação de escala."""
    _require_flag(actor)
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="reason é obrigatório para contestar escala.")
    cid = str(uuid4())
    payload = {"id": cid, "assignment_id": str(assignment_id), "employee_id": str(actor.user_id), "reason": reason, "status": "open", "created_at": _now()}
    try:
        return _store().create("schedule_contestations", str(actor.user_id), None, "open", payload, str(actor.user_id), ("id",), "hr.schedule.contested", None)
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/schedule-proposals/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Escala de Afinidade Justa – Primícia 18"}

app.include_router(primacia_router)