"""Módulo BI – Primícia 22: Painel de Perguntas Não Feitas."""

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

app = create_module_app("bi")

_FLAG = "primicia.bi.unasked_questions"


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


@app.post("/anomalies", status_code=201)
async def register_anomaly(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra observação anormal de métrica com período e evidências."""
    _require_flag(actor)
    metric = body.get("metric")
    period = body.get("period")
    if not metric or not period:
        raise HTTPException(status_code=422, detail="metric e period são obrigatórios.")
    anomaly_id = str(uuid4())
    payload = {
        "id": anomaly_id,
        "tenant_id": str(actor.business_id) if actor.business_id else None,
        "metric": str(metric),
        "period": str(period),
        "observed_value": body.get("observed_value"),
        "expected_range": body.get("expected_range", {}),
        "deviation_pct": body.get("deviation_pct"),
        "detected_at": _now(),
    }
    try:
        return _store().create(
            "anomaly_observations",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "detected",
            payload,
            str(actor.user_id),
            ("id",),
            "bi.anomaly.detected",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/anomalies/{anomaly_id}/suggest-question", status_code=201)
async def suggest_question(
    anomaly_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Sugere pergunta investigativa baseada na anomalia detectada.

    Correlação não é causalidade. Não acusar fraude automaticamente.
    """
    _require_flag(actor)
    question_text = body.get("question_text")
    explanation = body.get("explanation")
    if not question_text or not explanation:
        raise HTTPException(
            status_code=422, detail="question_text e explanation são obrigatórios."
        )
    qid = str(uuid4())
    payload = {
        "id": qid,
        "observation_id": str(anomaly_id),
        "question_text": str(question_text)[:512],
        "explanation": str(explanation)[:1024],
        "status": "suggested",
        "dismissed": False,
        "created_at": _now(),
    }
    try:
        return _store().create(
            "question_suggestions",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "suggested",
            payload,
            str(actor.user_id),
            ("id",),
            "bi.question.suggested",
            None,
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/questions/{question_id}/feedback", status_code=200)
async def analyst_feedback(
    question_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Analista descarta, investiga ou valida uma pergunta sugerida."""
    _require_flag(actor)
    action = body.get("action")
    if action not in {"dismissed", "investigate", "validated"}:
        raise HTTPException(
            status_code=422,
            detail="action deve ser: dismissed | investigate | validated.",
        )
    store = _store()
    try:
        question = store.get("question_suggestions", str(question_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada.")
    event = {
        "dismissed": "bi.question.dismissed",
        "investigate": "bi.question.investigation_started",
        "validated": "bi.question.validated",
    }.get(action, "bi.question.viewed")
    return store.update(
        question,
        {
            "status": action,
            "feedback_by": str(actor.user_id),
            "feedback_at": _now(),
            "feedback_notes": body.get("notes", ""),
        },
        action,
        str(actor.user_id),
        event,
    )


@app.get("/anomalies/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Painel de Perguntas Não Feitas – Primícia 22",
    }

app.include_router(primacia_router)