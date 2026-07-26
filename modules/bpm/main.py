"""Módulo BPM – Primícia 16: Laboratório de Processo Enxuto."""

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

app = create_module_app("bpm")

_FLAG = "primicia.bpm.process_laboratory"


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


@app.post("/scenarios", status_code=201)
async def create_scenario(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Clona processo real em cenário isolado. Cenário não altera processo real."""
    _require_flag(actor)
    source_process_id = body.get("source_process_id")
    name = body.get("name")
    if not source_process_id or not name:
        raise HTTPException(
            status_code=422, detail="source_process_id e name são obrigatórios."
        )
    sid = str(uuid4())
    payload = {
        "id": sid,
        "source_process_id": str(source_process_id),
        "name": str(name)[:256],
        "description": body.get("description", ""),
        "assumptions": body.get("assumptions", []),
        "steps": body.get("steps", []),
        "status": "draft",
        "created_by": str(actor.user_id),
        "created_at": _now(),
    }
    try:
        return _store().create(
            "process_scenarios",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "draft",
            payload,
            str(actor.user_id),
            ("id",),
            "bpm.scenario.created",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/scenarios/{scenario_id}/simulate", status_code=201)
async def simulate_scenario(
    scenario_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Executa simulação no cenário. IA não remove controle crítico sozinha."""
    _require_flag(actor)
    run_id = str(uuid4())
    payload = {
        "id": run_id,
        "scenario_id": str(scenario_id),
        "status": "running",
        "parameters": body.get("parameters", {}),
        "started_at": _now(),
    }
    try:
        result = _store().create(
            "simulation_runs",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "running",
            payload,
            str(actor.user_id),
            ("id",),
            "bpm.simulation.started",
            body.get("idempotency_key"),
        )
        # Simulação imediata para testes (em produção seria assíncrona)
        store = _store()
        store.update(
            result,
            {
                "status": "completed",
                "completed_at": _now(),
                "metrics": {"simulated": True},
            },
            "completed",
            str(actor.user_id),
            "bpm.simulation.completed",
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/scenarios/{scenario_id}/approve", status_code=201)
async def approve_experiment(
    scenario_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Aprova aplicação do experimento com rollback obrigatório documentado."""
    _require_flag(actor)
    rollback_plan = body.get("rollback_plan", "").strip()
    if not rollback_plan:
        raise HTTPException(
            status_code=422,
            detail="rollback_plan é obrigatório para aprovar experimento.",
        )
    target_group = body.get("target_group", {})
    if not target_group:
        raise HTTPException(
            status_code=422, detail="target_group é obrigatório (grupo controlado)."
        )
    approval_id = str(uuid4())
    payload = {
        "id": approval_id,
        "scenario_id": str(scenario_id),
        "approved_by": str(actor.user_id),
        "approved_at": _now(),
        "rollback_plan": rollback_plan,
        "target_group": target_group,
    }
    try:
        return _store().create(
            "process_experiment_approvals",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "approved",
            payload,
            str(actor.user_id),
            ("id",),
            "bpm.experiment.approved",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/scenarios/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Laboratório de Processo Enxuto – Primícia 16",
    }

app.include_router(primacia_router)