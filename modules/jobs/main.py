"""Módulo Jobs – Primícia 11: Janela de Trabalho Reversa."""

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

app = create_module_app("jobs")

_FLAG = "primicia.jobs.reverse_availability"

# Critérios discriminatórios proibidos na oferta
_FORBIDDEN_CRITERIA = frozenset(
    {
        "race",
        "religion",
        "gender",
        "age",
        "disability",
        "origin",
        "color",
        "sexual_orientation",
    }
)


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


def _check_discriminatory(body: dict[str, Any]) -> None:
    for key in _FORBIDDEN_CRITERIA:
        if key in body:
            raise HTTPException(
                status_code=422, detail=f"Critério discriminatório proibido: '{key}'."
            )


@app.post("/availability-windows", status_code=201)
async def create_availability_window(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Trabalhador publica janela de disponibilidade."""
    _require_flag(actor)
    available_from = body.get("available_from")
    available_until = body.get("available_until")
    if not available_from or not available_until:
        raise HTTPException(
            status_code=422, detail="available_from e available_until são obrigatórios."
        )
    if available_until <= available_from:
        raise HTTPException(
            status_code=422,
            detail="available_until deve ser posterior a available_from.",
        )

    window_id = str(uuid4())
    payload = {
        "id": window_id,
        "worker_id": str(actor.user_id),
        "available_from": available_from,
        "available_until": available_until,
        "status": "draft",
        "skills": body.get("skills", []),
        "preferences": body.get("preferences", []),
        "privacy": {
            "location_precision": body.get("location_precision", "neighborhood"),
            "show_to_verified_only": body.get("show_to_verified_only", True),
            "allow_direct_contact": body.get("allow_direct_contact", False),
        },
        "min_compensation": body.get("min_compensation"),
        "compensation_type": body.get("compensation_type", "hourly"),
        "created_at": _now(),
    }
    try:
        return _store().create(
            "availability_windows",
            str(actor.user_id),
            None,
            "draft",
            payload,
            str(actor.user_id),
            ("id",),
            "jobs.availability.created",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/availability-windows/{window_id}/publish", status_code=200)
async def publish_availability_window(
    window_id: UUID, actor: Actor = Depends(actor_from_headers)
) -> dict[str, Any]:
    """Publica a janela tornando-a visível para empregadores verificados."""
    _require_flag(actor)
    store = _store()
    try:
        window = store.get("availability_windows", str(window_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Janela não encontrada.")

    if str(actor.user_id) != str(window.get("user_id")):
        raise HTTPException(
            status_code=403,
            detail="Apenas o próprio trabalhador pode publicar a janela.",
        )
    if window.get("status") != "draft":
        raise HTTPException(
            status_code=409,
            detail=f"Janela em estado '{window.get('status')}', não pode ser publicada.",
        )

    return store.update(
        window,
        {"status": "published", "published_at": _now()},
        "published",
        str(actor.user_id),
        "jobs.availability.published",
    )


@app.post("/availability-windows/{window_id}/offers", status_code=201)
async def send_work_offer(
    window_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Empregador envia proposta a uma janela de disponibilidade."""
    _require_flag(actor)
    _check_discriminatory(body)

    if not actor.business_id:
        raise HTTPException(
            status_code=403,
            detail="Apenas empresas verificadas podem enviar propostas.",
        )

    store = _store()
    try:
        window = store.get("availability_windows", str(window_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Janela não encontrada.")

    if window.get("status") != "published":
        raise HTTPException(
            status_code=409, detail="Janela não está disponível para propostas."
        )

    prefs = window.get("payload", {}).get("privacy", {})
    min_comp = window.get("payload", {}).get("min_compensation")
    offered_comp = body.get("compensation_amount")
    if min_comp and offered_comp and float(offered_comp) < float(min_comp):
        raise HTTPException(
            status_code=422,
            detail="Remuneração abaixo do mínimo especificado pelo trabalhador.",
        )

    title = body.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="title é obrigatório na proposta.")

    offer_id = str(uuid4())
    payload = {
        "id": offer_id,
        "window_id": str(window_id),
        "employer_id": str(actor.business_id),
        "title": str(title)[:256],
        "description": body.get("description", ""),
        "compensation_amount": offered_comp,
        "compensation_type": body.get("compensation_type", "hourly"),
        "status": "sent",
        "expires_at": body.get("expires_at"),
        "sent_at": _now(),
    }
    try:
        return store.create(
            "employer_work_offers",
            str(actor.user_id),
            str(actor.business_id),
            "sent",
            payload,
            str(actor.user_id),
            ("id",),
            "jobs.work_offer.created",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/work-offers/{offer_id}/respond", status_code=200)
async def respond_to_offer(
    offer_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Trabalhador aceita ou rejeita uma proposta de trabalho."""
    _require_flag(actor)
    response = body.get("response")
    if response not in {"accepted", "rejected"}:
        raise HTTPException(
            status_code=422, detail="response deve ser 'accepted' ou 'rejected'."
        )

    store = _store()
    try:
        offer = store.get("employer_work_offers", str(offer_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Proposta não encontrada.")

    window_id = offer.get("payload", {}).get("window_id")
    event = (
        "jobs.work_offer.accepted"
        if response == "accepted"
        else "jobs.work_offer.rejected"
    )
    return store.update(
        offer,
        {"status": response, "responded_at": _now(), "notes": body.get("notes", "")},
        response,
        str(actor.user_id),
        event,
    )


@app.get("/availability-windows/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Janela de Trabalho Reversa – Primícia 11",
    }

app.include_router(primacia_router)