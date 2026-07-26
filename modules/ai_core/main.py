"""Módulo AI Core – Primícia 23: Recibo de Memória da IA."""
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
from ._primicias import router as primacia_router

app = create_module_app("ai_core")

_FLAG = "primicia.ai.memory_receipt"

# Tipos de memória permitidos
_MEMORY_TYPES = frozenset({"session", "user", "tenant"})

# Memória sensível desativada por padrão
_SENSITIVE_MEMORY_TYPES = frozenset({"health_data", "financial_data", "biometric", "location_history"})


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_flag(actor: Actor) -> None:
    require_flag(_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


def _hash_content(content: str) -> str:
    """Hash do conteúdo – nunca armazenar dado bruto."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


@app.post("/memory-receipts", status_code=201)
async def create_memory_receipt(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria recibo de memória da IA – tornando-a visível, limitada e controlável."""
    _require_flag(actor)

    memory_type = body.get("memory_type", "session")
    if memory_type not in _MEMORY_TYPES:
        raise HTTPException(status_code=422, detail=f"memory_type deve ser um de: {_MEMORY_TYPES}.")

    purpose = body.get("purpose")
    if not purpose:
        raise HTTPException(status_code=422, detail="purpose é obrigatório.")

    scope = body.get("scope", "local")
    content = body.get("content_summary", "")
    sensitive = body.get("sensitive", False)

    # Memória sensível desativada por padrão
    memory_subtype = body.get("memory_subtype", "")
    if memory_subtype in _SENSITIVE_MEMORY_TYPES and not body.get("explicitly_authorized", False):
        raise HTTPException(
            status_code=422,
            detail=f"Memória sensível do tipo '{memory_subtype}' está desativada por padrão. Requer autorização explícita.",
        )

    receipt_id = str(uuid4())
    payload = {
        "id": receipt_id,
        "user_id": str(actor.user_id) if memory_type in {"session", "user"} else None,
        "tenant_id": str(actor.business_id) if memory_type == "tenant" else None,
        "session_id": body.get("session_id"),
        "memory_type": memory_type,
        "memory_subtype": memory_subtype,
        "content_hash": _hash_content(content) if content else None,  # Nunca o dado bruto
        "purpose": str(purpose)[:512],
        "scope": scope,
        "sensitive": sensitive,
        "active": True,
        "expires_at": body.get("expires_at"),
        "modules_authorized": body.get("modules_authorized", []),
        "created_at": _now(),
    }

    try:
        return _store().create("ai_memory_receipts", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "active", payload, str(actor.user_id), ("id",), "ai.memory_receipt.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/memory-receipts/{receipt_id}")
async def get_memory_receipt(
    receipt_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Consulta um recibo de memória – titular pode sempre visualizar."""
    _require_flag(actor)
    store = _store()
    try:
        receipt = store.get("ai_memory_receipts", str(receipt_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Recibo de memória não encontrado.")

    payload = receipt.get("payload", {})
    owner_user_id = payload.get("user_id")
    owner_tenant_id = payload.get("tenant_id")

    if (str(actor.user_id) != str(owner_user_id or "") and
            str(actor.business_id or "") != str(owner_tenant_id or "") and
            "administrator" not in actor.roles):
        raise HTTPException(status_code=403, detail="Acesso negado a este recibo de memória.")

    # Registrar visualização
    store.audit_external("ai_memory_receipts", str(receipt_id), str(actor.user_id), "ai.memory_receipt.viewed", {})
    return receipt


@app.post("/memory-receipts/{receipt_id}/use", status_code=200)
async def log_memory_use(
    receipt_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra uso de memória por módulo consumidor."""
    _require_flag(actor)
    module = body.get("module")
    action = body.get("action")
    if not module or not action:
        raise HTTPException(status_code=422, detail="module e action são obrigatórios.")

    store = _store()
    try:
        receipt = store.get("ai_memory_receipts", str(receipt_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Recibo de memória não encontrado.")

    payload = receipt.get("payload", {})
    if not payload.get("active", True):
        raise HTTPException(status_code=410, detail="Memória expirada ou revogada. Uso negado.")

    modules_authorized = payload.get("modules_authorized", [])
    denied = bool(modules_authorized and module not in modules_authorized)

    store.audit_external("ai_memory_receipts", str(receipt_id), str(actor.user_id), "ai.memory.used", {"module": module, "action": action, "denied": denied})

    if denied:
        raise HTTPException(status_code=403, detail=f"Módulo '{module}' não autorizado a usar esta memória.")

    return {"receipt_id": str(receipt_id), "module": module, "action": action, "allowed": True}


@app.post("/memory-receipts/{receipt_id}/revoke", status_code=200)
async def revoke_memory(
    receipt_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Revoga memória – impede novo acesso imediatamente."""
    _require_flag(actor)
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="reason é obrigatório para revogar memória.")

    store = _store()
    try:
        receipt = store.get("ai_memory_receipts", str(receipt_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Recibo de memória não encontrado.")

    payload = receipt.get("payload", {})
    owner_user_id = payload.get("user_id")
    if str(actor.user_id) != str(owner_user_id or "") and "administrator" not in actor.roles:
        raise HTTPException(status_code=403, detail="Apenas o titular pode revogar esta memória.")

    return store.update(receipt, {"active": False, "revoked_at": _now(), "revoked_by": str(actor.user_id), "revocation_reason": reason}, "revoked", str(actor.user_id), "ai.memory.revoked")


@app.get("/memory-receipts")
async def list_my_memory_receipts(actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
    """Lista todos os recibos de memória do usuário."""
    _require_flag(actor)
    return _store().list("ai_memory_receipts", str(actor.user_id), None, page=1, page_size=50)


@app.get("/memory-receipts/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Recibo de Memória da IA – Primícia 23"}

app.include_router(primacia_router)