"""Módulo Property – Primícia 21: Condomínio de Capacidade Compartilhada."""
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

app = create_module_app("property")

_FLAG = "primicia.property.shared_capacity"


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/shared-assets", status_code=201)
async def register_shared_asset(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cadastra ativo para compartilhamento. Pendente de aprovação do condomínio."""
    _require_flag(actor)
    name = body.get("name")
    asset_type = body.get("asset_type")
    if not name or not asset_type:
        raise HTTPException(status_code=422, detail="name e asset_type são obrigatórios.")
    if body.get("hazardous"):
        raise HTTPException(status_code=422, detail="Itens perigosos ou proibidos não podem ser cadastrados.")
    aid = str(uuid4())
    payload = {"id": aid, "tenant_id": str(actor.business_id) if actor.business_id else None, "name": str(name)[:256], "asset_type": str(asset_type), "description": body.get("description", ""), "status": "pending_approval", "hazardous": False, "created_by": str(actor.user_id), "created_at": _now()}
    try:
        return _store().create("shared_property_assets", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "pending_approval", payload, str(actor.user_id), ("id",), "property.shared_asset.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/shared-assets/{asset_id}/approve", status_code=200)
async def approve_asset(
    asset_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Administrador do condomínio aprova o ativo para compartilhamento."""
    _require_flag(actor)
    if "administrator" not in actor.roles and "owner" not in actor.roles:
        raise HTTPException(status_code=403, detail="Apenas administradores do condomínio podem aprovar ativos.")
    store = _store()
    try:
        asset = store.get("shared_property_assets", str(asset_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Ativo não encontrado.")
    return store.update(asset, {"status": "available", "approved_by": str(actor.user_id), "approved_at": _now()}, "available", str(actor.user_id), "property.shared_asset.approved")


@app.post("/shared-assets/{asset_id}/reserve", status_code=201)
async def reserve_asset(
    asset_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Morador reserva ativo compartilhado. Privacidade entre moradores preservada."""
    _require_flag(actor)
    start_at = body.get("start_at")
    end_at = body.get("end_at")
    if not start_at or not end_at:
        raise HTTPException(status_code=422, detail="start_at e end_at são obrigatórios.")
    store = _store()
    try:
        asset = store.get("shared_property_assets", str(asset_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Ativo não encontrado.")
    if asset.get("status") != "available":
        raise HTTPException(status_code=409, detail="Ativo não disponível para reserva.")
    rid = str(uuid4())
    payload = {"id": rid, "asset_id": str(asset_id), "reserver_id": str(actor.user_id), "start_at": str(start_at), "end_at": str(end_at), "status": "active", "created_at": _now()}
    try:
        return store.create("shared_asset_reservations", str(actor.user_id), None, "active", payload, str(actor.user_id), ("id",), "property.shared_asset.reserved", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/reservations/{reservation_id}/return", status_code=200)
async def return_asset(
    reservation_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra devolução de ativo com inspeção."""
    _require_flag(actor)
    store = _store()
    try:
        reservation = store.get("shared_asset_reservations", str(reservation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")
    reserver_id = reservation.get("payload", {}).get("reserver_id") or reservation.get("user_id")
    if str(actor.user_id) != str(reserver_id) and "administrator" not in actor.roles:
        raise HTTPException(status_code=403, detail="Apenas o reservante pode devolver o ativo.")
    return store.update(reservation, {"status": "returned", "returned_at": _now(), "condition_notes": body.get("condition_notes", "")}, "returned", str(actor.user_id), "property.shared_asset.returned")


@app.get("/shared-assets/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Condomínio de Capacidade Compartilhada – Primícia 21"}

app.include_router(primacia_router)