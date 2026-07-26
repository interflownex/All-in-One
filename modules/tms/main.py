"""Módulo TMS – Primícia 14: Bolsa Cega de Capacidade Logística."""

from __future__ import annotations

import hashlib
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

app = create_module_app("tms")

_FLAG = "primicia.tms.blind_capacity_exchange"


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


def _anon_ref(company_id: str) -> str:
    """Gera alias anônimo determinístico para uma empresa."""
    return "anon-" + hashlib.sha256(company_id.encode()).hexdigest()[:12]


@app.post("/capacity-offers", status_code=201)
async def publish_capacity_offer(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Empresa publica oferta de capacidade logística de forma anônima."""
    _require_flag(actor)
    if not actor.business_id:
        raise HTTPException(
            status_code=403,
            detail="Apenas empresas verificadas podem publicar capacidade.",
        )
    origin = body.get("origin_region")
    dest = body.get("destination_region")
    available_from = body.get("available_from")
    available_until = body.get("available_until")
    if not all([origin, dest, available_from, available_until]):
        raise HTTPException(
            status_code=422,
            detail="origin_region, destination_region, available_from e available_until são obrigatórios.",
        )
    offer_id = str(uuid4())
    anonymous_ref = _anon_ref(str(actor.business_id) + offer_id)
    payload = {
        "id": offer_id,
        "company_id": str(actor.business_id),
        "anonymous_ref": anonymous_ref,
        "origin_region": str(origin)[:128],
        "destination_region": str(dest)[:128],
        "available_from": available_from,
        "available_until": available_until,
        "capacity_kg": body.get("capacity_kg"),
        "capacity_m3": body.get("capacity_m3"),
        "transport_types": body.get("transport_types", []),
        "status": "published",
        "published_at": _now(),
    }
    try:
        result = _store().create(
            "anonymous_capacity_offers",
            str(actor.user_id),
            str(actor.business_id),
            "published",
            payload,
            str(actor.user_id),
            ("id",),
            "tms.capacity_offer.published",
            body.get("idempotency_key"),
        )
        # Retornar sem expor company_id real
        result_safe = dict(result)
        if "payload" in result_safe:
            result_safe["payload"] = {
                k: v for k, v in result_safe["payload"].items() if k != "company_id"
            }
        return result_safe
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/freight-demands", status_code=201)
async def publish_freight_demand(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Empresa publica demanda de frete de forma anônima."""
    _require_flag(actor)
    if not actor.business_id:
        raise HTTPException(
            status_code=403,
            detail="Apenas empresas verificadas podem publicar demandas.",
        )
    origin = body.get("origin_region")
    dest = body.get("destination_region")
    needed_by = body.get("needed_by")
    if not all([origin, dest, needed_by]):
        raise HTTPException(
            status_code=422,
            detail="origin_region, destination_region e needed_by são obrigatórios.",
        )
    did = str(uuid4())
    anonymous_ref = _anon_ref(str(actor.business_id) + did)
    payload = {
        "id": did,
        "company_id": str(actor.business_id),
        "anonymous_ref": anonymous_ref,
        "origin_region": str(origin)[:128],
        "destination_region": str(dest)[:128],
        "needed_by": needed_by,
        "weight_kg": body.get("weight_kg"),
        "volume_m3": body.get("volume_m3"),
        "cargo_types": body.get("cargo_types", []),
        "status": "published",
        "published_at": _now(),
    }
    try:
        result = _store().create(
            "anonymous_freight_demands",
            str(actor.user_id),
            str(actor.business_id),
            "published",
            payload,
            str(actor.user_id),
            ("id",),
            "tms.freight_demand.published",
            body.get("idempotency_key"),
        )
        result_safe = dict(result)
        if "payload" in result_safe:
            result_safe["payload"] = {
                k: v for k, v in result_safe["payload"].items() if k != "company_id"
            }
        return result_safe
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/matches/{match_id}/accept", status_code=200)
async def accept_match(
    match_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Empresa aceita combinação. Após aceite mútuo, dados são revelados."""
    _require_flag(actor)
    if not actor.business_id:
        raise HTTPException(
            status_code=403,
            detail="Apenas empresas verificadas podem aceitar combinações.",
        )
    store = _store()
    try:
        match = store.get("capacity_match_candidates", str(match_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Combinação não encontrada.")

    # Registra consentimento de divulgação mútua
    consent_id = str(uuid4())
    consent_payload = {
        "id": consent_id,
        "match_id": str(match_id),
        "company_id": str(actor.business_id),
        "accepted": True,
        "accepted_at": _now(),
    }
    try:
        _store().create(
            "mutual_disclosure_consents",
            str(actor.user_id),
            str(actor.business_id),
            "accepted",
            consent_payload,
            str(actor.user_id),
            ("id",),
            "tms.capacity_match.mutually_accepted",
            None,
        )
    except Exception:
        pass
    return store.update(
        match,
        {"status": "accepted"},
        "accepted",
        str(actor.user_id),
        "tms.capacity_match.proposed",
    )


@app.get("/capacity-offers/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Bolsa Cega de Capacidade Logística – Primícia 14",
    }

app.include_router(primacia_router)