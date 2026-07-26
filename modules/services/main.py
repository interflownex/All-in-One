"""Módulo Services – Primícia 9: Contrato por Resultado Componível."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Body, Depends, HTTPException, Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.feature_flags import is_flag_enabled, require_flag
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers
from _primicias import router as primacia_router

app = create_module_app("services")

_FLAG = "primicia.services.outcome_contract"


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


@app.post("/outcome-contracts", status_code=201)
async def create_outcome_contract(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria contrato por resultado com etapas e critérios objetivos."""
    _require_flag(actor)
    title = body.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="title é obrigatório.")
    milestones = body.get("milestones", [])
    if not milestones:
        raise HTTPException(
            status_code=422, detail="Pelo menos um marco (milestone) é obrigatório."
        )
    for m in milestones:
        if not m.get("acceptance_criteria"):
            raise HTTPException(
                status_code=422,
                detail="Cada marco deve ter acceptance_criteria objetivos.",
            )

    cid = str(uuid4())
    payload = {
        "id": cid,
        "client_id": str(actor.user_id),
        "title": str(title)[:256],
        "description": body.get("description", ""),
        "status": "draft",
        "escrow_amount": body.get("escrow_amount"),
        "milestones": milestones,
        "created_at": _now(),
    }
    try:
        return _store().create(
            "outcome_contracts",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "draft",
            payload,
            str(actor.user_id),
            ("id",),
            "services.outcome_contract.created",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/outcome-contracts/{contract_id}/activate", status_code=200)
async def activate_contract(
    contract_id: UUID, actor: Actor = Depends(actor_from_headers)
) -> dict[str, Any]:
    """Ativa o contrato após acordo de todas as partes."""
    _require_flag(actor)
    store = _store()
    try:
        contract = store.get("outcome_contracts", str(contract_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    if contract.get("status") != "draft":
        raise HTTPException(
            status_code=409, detail="Apenas contratos em rascunho podem ser ativados."
        )
    return store.update(
        contract,
        {"status": "active", "activated_at": _now()},
        "active",
        str(actor.user_id),
        "services.outcome_contract.activated",
    )


@app.post("/milestone-evidence/{evidence_id}/accept", status_code=200)
async def accept_milestone(
    evidence_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cliente aceita marco cumprido."""
    _require_flag(actor)
    store = _store()
    try:
        evidence = store.get("milestone_evidence", str(evidence_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Evidência não encontrada.")
    return store.update(
        evidence,
        {
            "status": "accepted",
            "accepted_at": _now(),
            "accepted_by": str(actor.user_id),
            "notes": body.get("notes", ""),
        },
        "accepted",
        str(actor.user_id),
        "services.outcome_milestone.accepted",
    )


@app.get("/outcome-contracts/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Contrato por Resultado Componível – Primícia 9",
    }


@app.get("/providers/{provider_id}/time-slots")
async def get_time_slots(provider_id: str, date: str):
    """
    Mock do Motor de Calendário: retorna slots de horários disponíveis
    para um prestador num dia específico.
    """
    return {
        "provider_id": provider_id,
        "date": date,
        "available_slots": ["09:00", "10:00", "11:30", "14:00", "15:30", "16:00"],
    }


@app.post("/providers/{provider_id}/reserve-slot")
async def reserve_slot(provider_id: str, request: Request, body: dict):
    """
    Mock de Reserva de Calendário. Simula a verificação de concorrência.
    """
    slot = body.get("slot")
    customer_id = body.get("customer_id")

    if not slot or not customer_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="slot e customer_id obrigatorios.")

    if slot in ["10:00", "14:00"]:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=409,
            detail=f"O horario {slot} acabou de ser reservado por outra pessoa.",
        )

    return {
        "status": "reserved",
        "provider_id": provider_id,
        "slot": slot,
        "customer_id": customer_id,
        "reservation_id": f"res-{customer_id}-{slot.replace(':', '')}",
    }

app.include_router(primacia_router)