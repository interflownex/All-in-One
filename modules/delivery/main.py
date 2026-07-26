"""Módulo Delivery – Primícia 7: Entrega de Trajeto Aproveitado."""

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

app = create_module_app("delivery")

_FLAG = "primicia.delivery.route_capacity"


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


@app.post("/planned-trips", status_code=201)
async def publish_trip(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Usuário e veículo verificados publicam trajetória para oferta de capacidade."""
    _require_flag(actor)
    departure_at = body.get("departure_at")
    origin_approx = body.get("origin_approx")
    destination_approx = body.get("destination_approx")
    if not all([departure_at, origin_approx, destination_approx]):
        raise HTTPException(
            status_code=422,
            detail="departure_at, origin_approx e destination_approx são obrigatórios.",
        )

    trip_id = str(uuid4())
    max_weight = body.get("max_weight_kg")
    prohibited = body.get("prohibited_items", [])
    payload = {
        "id": trip_id,
        "carrier_user_id": str(actor.user_id),
        "vehicle_id": body.get("vehicle_id"),
        "origin_approx": str(origin_approx)[:256],
        "destination_approx": str(destination_approx)[:256],
        "departure_at": departure_at,
        "arrival_at": body.get("arrival_at"),
        "status": "available",
        "max_weight_kg": max_weight,
        "max_volume_cm3": body.get("max_volume_cm3"),
        "prohibited_items": prohibited,
        "created_at": _now(),
    }
    try:
        return _store().create(
            "planned_trips",
            str(actor.user_id),
            None,
            "available",
            payload,
            str(actor.user_id),
            ("id",),
            "delivery.route_capacity.published",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/parcels", status_code=201)
async def request_parcel_delivery(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Remetente solicita entrega de encomenda via trajeto aproveitado."""
    _require_flag(actor)
    if not body.get("pickup_region") or not body.get("dropoff_region"):
        raise HTTPException(
            status_code=422, detail="pickup_region e dropoff_region são obrigatórios."
        )
    pid = str(uuid4())
    payload = {
        "id": pid,
        "sender_id": str(actor.user_id),
        "description": body.get("description", ""),
        "weight_kg": body.get("weight_kg"),
        "volume_cm3": body.get("volume_cm3"),
        "category": body.get("category", "general"),
        "pickup_region": str(body["pickup_region"])[:128],
        "dropoff_region": str(body["dropoff_region"])[:128],
        "status": "searching",
        "created_at": _now(),
    }
    try:
        return _store().create(
            "parcel_requirements",
            str(actor.user_id),
            None,
            "searching",
            payload,
            str(actor.user_id),
            ("id",),
            "delivery.route_capacity.matched",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/matches/{match_id}/pickup", status_code=200)
async def confirm_pickup(
    match_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra prova de coleta da encomenda."""
    _require_flag(actor)
    evidence = body.get("evidence")
    if not evidence:
        raise HTTPException(
            status_code=422, detail="evidence de coleta é obrigatória (foto ou hash)."
        )
    store = _store()
    try:
        match = store.get("route_parcel_matches", str(match_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Combinação não encontrada.")
    return store.update(
        match,
        {
            "status": "picked_up",
            "picked_up_at": _now(),
            "evidence_pickup": str(evidence)[:512],
        },
        "picked_up",
        str(actor.user_id),
        "delivery.route_capacity.picked_up",
    )


@app.post("/matches/{match_id}/deliver", status_code=200)
async def confirm_delivery(
    match_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra prova de entrega da encomenda."""
    _require_flag(actor)
    evidence = body.get("evidence")
    if not evidence:
        raise HTTPException(
            status_code=422, detail="evidence de entrega é obrigatória."
        )
    store = _store()
    try:
        match = store.get("route_parcel_matches", str(match_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Combinação não encontrada.")
    return store.update(
        match,
        {
            "status": "delivered",
            "delivered_at": _now(),
            "evidence_delivery": str(evidence)[:512],
        },
        "delivered",
        str(actor.user_id),
        "delivery.route_capacity.delivered",
    )


@app.get("/planned-trips/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Entrega de Trajeto Aproveitado – Primícia 7",
    }

app.include_router(primacia_router)