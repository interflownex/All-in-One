"""Módulo WMS – Primícia 13: Mapa de Certeza do Estoque."""
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

app = create_module_app("wms")

_FLAG = "primicia.wms.inventory_confidence"

# Limite de score que dispara contagem dirigida
_COUNT_TRIGGER_THRESHOLD = 0.7


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/inventory/confidence-scores", status_code=201)
async def create_confidence_score(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria ou registra score de confiança para um item/localização."""
    _require_flag(actor)
    location_id = body.get("location_id")
    sku = body.get("sku")
    if not location_id or not sku:
        raise HTTPException(status_code=422, detail="location_id e sku são obrigatórios.")

    score = float(body.get("score", 1.0))
    if not 0.0 <= score <= 1.0:
        raise HTTPException(status_code=422, detail="score deve estar entre 0 e 1.")

    score_id = str(uuid4())
    payload = {
        "id": score_id,
        "tenant_id": str(actor.business_id) if actor.business_id else None,
        "location_id": str(location_id),
        "sku": str(sku),
        "score": score,
        "last_event_type": body.get("event_type"),
        "calculated_at": _now(),
        "requires_count": score < _COUNT_TRIGGER_THRESHOLD,
    }
    try:
        return _store().create("inventory_confidence_scores", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "active", payload, str(actor.user_id), ("id",), "wms.inventory_confidence.changed", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/inventory/confidence-scores/{score_id}/events", status_code=201)
async def register_confidence_event(
    score_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra um evento que altera a confiança do estoque.

    Movimentação sem leitura, ajuste e atraso REDUZEM o score.
    Contagem confirmada AUMENTA o score.
    """
    _require_flag(actor)
    event_type = body.get("event_type")
    delta = body.get("delta")
    if not event_type or delta is None:
        raise HTTPException(status_code=422, detail="event_type e delta são obrigatórios.")

    delta = float(delta)
    # Nunca ajustar estoque apenas pelo score – só registrar o impacto
    if abs(delta) > 1.0:
        raise HTTPException(status_code=422, detail="delta deve ser entre -1 e 1.")

    store = _store()
    try:
        score_record = store.get("inventory_confidence_scores", str(score_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Score de confiança não encontrado.")

    # Calcular novo score
    current_score = float(score_record.get("payload", {}).get("score", 1.0))
    new_score = max(0.0, min(1.0, current_score + delta))

    # Atualizar score
    updated = store.update(
        score_record,
        {"score": new_score, "last_event_type": event_type, "calculated_at": _now(), "requires_count": new_score < _COUNT_TRIGGER_THRESHOLD},
        "active",
        str(actor.user_id),
        "wms.inventory_confidence.changed",
    )

    # Se score caiu abaixo do limiar, sugerir contagem dirigida
    triggered_count = new_score < _COUNT_TRIGGER_THRESHOLD and current_score >= _COUNT_TRIGGER_THRESHOLD
    return {
        "score_id": str(score_id),
        "previous_score": current_score,
        "new_score": new_score,
        "event_type": event_type,
        "count_requested": triggered_count,
    }


@app.post("/inventory/count-requests", status_code=201)
async def request_targeted_count(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Solicita contagem dirigida para localização com baixo score."""
    _require_flag(actor)
    score_id = body.get("score_id")
    reason = body.get("reason")
    if not score_id or not reason:
        raise HTTPException(status_code=422, detail="score_id e reason são obrigatórios.")

    store = _store()
    try:
        score = store.get("inventory_confidence_scores", str(score_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Score não encontrado.")

    request_id = str(uuid4())
    payload = {
        "id": request_id,
        "tenant_id": str(actor.business_id) if actor.business_id else None,
        "score_id": str(score_id),
        "location_id": score.get("payload", {}).get("location_id"),
        "sku": score.get("payload", {}).get("sku"),
        "reason": str(reason)[:512],
        "status": "requested",
        "requested_at": _now(),
    }
    try:
        result = store.create("targeted_count_requests", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "requested", payload, str(actor.user_id), ("id",), "wms.targeted_count.requested", body.get("idempotency_key"))
        return result
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/inventory/count-requests/{request_id}/complete", status_code=200)
async def complete_count(
    request_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra resultado de contagem física.

    IMPORTANTE: Nunca ajustar estoque apenas pelo score; correção exige evidência real.
    """
    _require_flag(actor)
    counted_quantity = body.get("counted_quantity")
    if counted_quantity is None:
        raise HTTPException(status_code=422, detail="counted_quantity é obrigatório.")

    evidence = body.get("evidence", {})
    if not evidence:
        raise HTTPException(status_code=422, detail="evidence é obrigatória para registrar resultado de contagem.")

    store = _store()
    try:
        request = store.get("targeted_count_requests", str(request_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Solicitação de contagem não encontrada.")

    system_quantity = body.get("system_quantity")
    discrepancy = None
    if system_quantity is not None:
        discrepancy = float(counted_quantity) - float(system_quantity)

    result_id = str(uuid4())
    payload = {
        "id": result_id,
        "request_id": str(request_id),
        "counted_by": str(actor.user_id),
        "counted_quantity": float(counted_quantity),
        "system_quantity": system_quantity,
        "discrepancy": discrepancy,
        "counted_at": _now(),
        "evidence": evidence,
    }
    result = store.create("targeted_count_results", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "completed", payload, str(actor.user_id), ("id",), "wms.targeted_count.completed", body.get("idempotency_key"))

    # Atualiza o request para concluído
    store.update(request, {"status": "completed"}, "completed", str(actor.user_id), "wms.targeted_count.started")

    if discrepancy is not None and abs(discrepancy) > 0:
        store.audit_external("targeted_count_results", result_id, str(actor.user_id), "wms.inventory_discrepancy.confirmed", {"discrepancy": discrepancy, "sku": request.get("payload", {}).get("sku")})

    return result


@app.get("/inventory/confidence-scores/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Mapa de Certeza do Estoque – Primícia 13"}

app.include_router(primacia_router)