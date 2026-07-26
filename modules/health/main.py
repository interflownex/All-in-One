"""Módulo Health – Primícia 19: Cápsula de Continuidade do Cuidado.

Controle 100% pelo paciente. IA não oferece diagnóstico.
Acesso emergencial exige base jurídica e auditoria reforçada.
"""
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

app = create_module_app("health")

_FLAG = "primicia.health.continuity_capsule"


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/continuity-capsules", status_code=201)
async def create_capsule(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Paciente cria cápsula de saúde controlada por ele mesmo."""
    _require_flag(actor)
    title = body.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="title é obrigatório.")
    cid = str(uuid4())
    payload = {"id": cid, "patient_id": str(actor.user_id), "title": str(title)[:256], "status": "active", "version": 1, "sections": body.get("sections", []), "created_at": _now()}
    try:
        return _store().create("continuity_capsules", str(actor.user_id), None, "active", payload, str(actor.user_id), ("id",), "health.continuity_capsule.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/continuity-capsules/{capsule_id}/grant", status_code=201)
async def grant_access(
    capsule_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Paciente concede acesso temporário com consentimento granular."""
    _require_flag(actor)
    grantee_id = body.get("grantee_id")
    valid_until = body.get("valid_until")
    purpose = body.get("purpose")
    if not grantee_id or not valid_until or not purpose:
        raise HTTPException(status_code=422, detail="grantee_id, valid_until e purpose são obrigatórios.")

    store = _store()
    try:
        capsule = store.get("continuity_capsules", str(capsule_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Cápsula não encontrada.")

    patient_id = capsule.get("payload", {}).get("patient_id") or capsule.get("user_id")
    if str(actor.user_id) != str(patient_id):
        raise HTTPException(status_code=403, detail="Apenas o paciente pode conceder acesso à sua cápsula.")

    emergency_access = body.get("emergency_access", False)
    emergency_basis = body.get("emergency_basis", "")
    if emergency_access and not emergency_basis:
        raise HTTPException(status_code=422, detail="Acesso emergencial exige emergency_basis (base jurídica).")

    grant_id = str(uuid4())
    payload = {"id": grant_id, "capsule_id": str(capsule_id), "grantee_id": str(grantee_id), "grantee_type": body.get("grantee_type", "professional"), "granted_sections": body.get("granted_sections", []), "granted_at": _now(), "valid_until": str(valid_until), "purpose": str(purpose)[:512], "emergency_access": emergency_access, "emergency_basis": emergency_basis, "revoked": False}
    try:
        return store.create("continuity_access_grants", str(actor.user_id), None, "active", payload, str(actor.user_id), ("id",), "health.continuity_access.granted", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/access-grants/{grant_id}/revoke", status_code=200)
async def revoke_access(
    grant_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Paciente revoga acesso imediatamente."""
    _require_flag(actor)
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="reason é obrigatório.")
    store = _store()
    try:
        grant = store.get("continuity_access_grants", str(grant_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Acesso não encontrado.")
    capsule_id = grant.get("payload", {}).get("capsule_id")
    capsule = store.get("continuity_capsules", str(capsule_id))
    patient_id = capsule.get("payload", {}).get("patient_id") or capsule.get("user_id")
    if str(actor.user_id) != str(patient_id):
        raise HTTPException(status_code=403, detail="Apenas o paciente pode revogar acesso.")
    return store.update(grant, {"revoked": True, "revoked_at": _now(), "revoked_by": str(actor.user_id), "revocation_reason": reason}, "revoked", str(actor.user_id), "health.continuity_access.revoked")


@app.get("/continuity-capsules/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Cápsula de Continuidade do Cuidado – Primícia 19"}

app.include_router(primacia_router)