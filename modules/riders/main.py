"""Módulo Riders – Primícia 8: Passaporte de Evidências Operacionais."""

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

app = create_module_app("riders")

_FLAG = "primicia.riders.evidence_passport"

# Atributos protegidos que nunca devem fundamentar competências
_PROTECTED_ATTRIBUTES = frozenset(
    {"race", "religion", "gender", "age", "disability", "origin", "sexual_orientation"}
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


@app.post("/evidence-credentials", status_code=201)
async def issue_evidence_credential(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Emite credencial de evidência operacional para um rider."""
    _require_flag(actor)
    rider_id = body.get("rider_id")
    competency_id = body.get("competency_id")
    if not rider_id or not competency_id:
        raise HTTPException(
            status_code=422, detail="rider_id e competency_id são obrigatórios."
        )

    # Proibir atributos protegidos
    for attr in _PROTECTED_ATTRIBUTES:
        if attr in body:
            raise HTTPException(
                status_code=422,
                detail=f"Atributo protegido não pode fundamentar competência: '{attr}'.",
            )

    source_type = body.get("source_type", "platform_activity")
    cred_id = str(uuid4())
    payload = {
        "id": cred_id,
        "rider_id": str(rider_id),
        "competency_id": str(competency_id),
        "source_type": source_type,
        "source_ref": body.get("source_ref"),
        "period_start": body.get("period_start"),
        "period_end": body.get("period_end"),
        "issued_at": _now(),
        "expires_at": body.get("expires_at"),
        "revoked": False,
    }
    try:
        return _store().create(
            "rider_evidence_credentials",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "active",
            payload,
            str(actor.user_id),
            ("id",),
            "rider.evidence.issued",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/evidence-credentials/{cred_id}/present", status_code=201)
async def present_evidence(
    cred_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Compartilha competências selecionadas – empresa acessa apenas o necessário."""
    _require_flag(actor)
    presented_to = body.get("presented_to")
    competencies_shared = body.get("competencies_shared", [])
    if not presented_to:
        raise HTTPException(status_code=422, detail="presented_to é obrigatório.")

    store = _store()
    try:
        cred = store.get("rider_evidence_credentials", str(cred_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")

    if cred.get("payload", {}).get("revoked"):
        raise HTTPException(status_code=410, detail="Credencial revogada.")

    rider_id = cred.get("payload", {}).get("rider_id")
    if str(actor.user_id) != str(rider_id):
        raise HTTPException(
            status_code=403, detail="Apenas o rider pode apresentar sua credencial."
        )

    pres_id = str(uuid4())
    payload = {
        "id": pres_id,
        "credential_id": str(cred_id),
        "presented_to": str(presented_to),
        "competencies_shared": competencies_shared,
        "consented_at": _now(),
        "expires_at": body.get("expires_at"),
    }
    try:
        return store.create(
            "evidence_presentations",
            str(actor.user_id),
            None,
            "active",
            payload,
            str(actor.user_id),
            ("id",),
            "rider.evidence.presented",
            body.get("idempotency_key"),
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/evidence-credentials/{cred_id}/dispute", status_code=201)
async def dispute_evidence(
    cred_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Rider contesta uma evidência registrada."""
    _require_flag(actor)
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(
            status_code=422, detail="reason é obrigatório para contestação."
        )
    disp_id = str(uuid4())
    payload = {
        "id": disp_id,
        "credential_id": str(cred_id),
        "disputed_by": str(actor.user_id),
        "reason": reason,
        "status": "open",
        "created_at": _now(),
    }
    try:
        return _store().create(
            "evidence_disputes",
            str(actor.user_id),
            None,
            "open",
            payload,
            str(actor.user_id),
            ("id",),
            "rider.evidence.disputed",
            None,
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/evidence-credentials/{cred_id}/revoke", status_code=200)
async def revoke_evidence(
    cred_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Revoga credencial de evidência."""
    _require_flag(actor)
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="reason é obrigatório.")
    store = _store()
    try:
        cred = store.get("rider_evidence_credentials", str(cred_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")
    return store.update(
        cred,
        {
            "revoked": True,
            "revoked_at": _now(),
            "revoked_by": str(actor.user_id),
            "revoked_reason": reason,
        },
        "revoked",
        str(actor.user_id),
        "rider.evidence.revoked",
    )


@app.get("/evidence-credentials/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Passaporte de Evidências Operacionais – Primícia 8",
    }

app.include_router(primacia_router)