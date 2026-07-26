"""Módulo Permissions – Primícia 3: Procuração Operacional Expirável.

Endpoints adicionais às rotas genéricas fornecidas por create_module_app().
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

from ._primicias import router as primacia_router

app = create_module_app("permissions")

_FLAG = "primicia.permissions.expiring_delegation"

# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


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


def _validate_constraints(constraints: dict[str, Any]) -> None:
    valid_until = constraints.get("valid_until")
    valid_from = constraints.get("valid_from", _now())
    if valid_until and valid_until < valid_from:
        raise HTTPException(
            status_code=422, detail="valid_until deve ser posterior a valid_from."
        )
    max_amount = constraints.get("max_amount")
    if max_amount is not None and float(max_amount) <= 0:
        raise HTTPException(status_code=422, detail="max_amount deve ser positivo.")
    if not isinstance(constraints.get("allowed_actions", []), list):
        raise HTTPException(
            status_code=422, detail="allowed_actions deve ser uma lista."
        )


def _check_delegation_active(delegation: dict[str, Any]) -> None:
    if delegation.get("status") not in {"active", "pending"}:
        raise HTTPException(
            status_code=409,
            detail=f"Delegação está em estado '{delegation.get('status')}' e não pode ser usada.",
        )
    constraints = delegation.get("payload", {}).get("constraints", {})
    valid_until = constraints.get("valid_until")
    if valid_until and valid_until < _now():
        raise HTTPException(status_code=410, detail="Delegação expirada.")


def _check_delegation_authorizable(grantor: Actor, grantee_scopes: list[str]) -> None:
    for scope in grantee_scopes:
        if scope not in grantor.scopes and "administrator" not in grantor.roles:
            raise HTTPException(
                status_code=403,
                detail=f"Grantor não possui o escopo '{scope}' para delegar.",
            )


# ---------------------------------------------------------------------------
# Recurso 3: Procuração Operacional Expirável
# ---------------------------------------------------------------------------


@app.post("/delegations", status_code=201)
async def create_delegation(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria uma procuração operacional com restrições expirável."""
    _require_flag(actor)
    grantee_id = body.get("grantee_id")
    purpose = body.get("purpose")
    if not grantee_id or not purpose:
        raise HTTPException(
            status_code=422, detail="grantee_id e purpose são obrigatórios."
        )

    constraints = body.get("constraints", {})
    _validate_constraints(constraints)
    allowed_actions = constraints.get("allowed_actions", [])
    _check_delegation_authorizable(actor, allowed_actions)

    delegation_id = str(uuid4())
    payload = {
        "id": delegation_id,
        "grantor_id": str(actor.user_id),
        "grantee_id": str(grantee_id),
        "purpose": str(purpose)[:512],
        "status": "pending",
        "constraints": {
            "valid_from": constraints.get("valid_from", _now()),
            "valid_until": constraints.get("valid_until"),
            "max_amount": constraints.get("max_amount"),
            "allowed_actions": allowed_actions,
            "allowed_entities": constraints.get("allowed_entities", []),
            "allowed_branches": constraints.get("allowed_branches", []),
            "allowed_locations": constraints.get("allowed_locations", []),
            "allowed_hours": constraints.get("allowed_hours", {}),
            "single_use": bool(constraints.get("single_use", False)),
            "requires_second_approval": bool(
                constraints.get("requires_second_approval", False)
            ),
        },
        "idempotency_key": body.get("idempotency_key"),
        "created_at": _now(),
    }

    store = _store()
    try:
        result = store.create(
            "delegations",
            str(actor.user_id),
            str(actor.business_id) if actor.business_id else None,
            "pending",
            payload,
            str(actor.user_id),
            ("id",),
            "permissions.delegation.created",
            body.get("idempotency_key"),
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=409, detail=f"Erro ao criar delegação: {exc}"
        ) from exc


@app.post("/delegations/{delegation_id}/activate", status_code=200)
async def activate_delegation(
    delegation_id: UUID,
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Ativa uma procuração pendente."""
    _require_flag(actor)
    store = _store()
    try:
        delegation = store.get("delegations", str(delegation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Delegação não encontrada.")

    grantor_id = delegation.get("payload", {}).get("grantor_id") or delegation.get(
        "user_id"
    )
    if str(actor.user_id) != str(grantor_id) and "administrator" not in actor.roles:
        raise HTTPException(
            status_code=403, detail="Apenas o concedente pode ativar esta delegação."
        )
    if delegation.get("status") != "pending":
        raise HTTPException(
            status_code=409, detail=f"Delegação em estado '{delegation.get('status')}'."
        )

    return store.update(
        delegation,
        {"status": "active", "activated_at": _now()},
        "active",
        str(actor.user_id),
        "permissions.delegation.activated",
    )


@app.post("/delegations/{delegation_id}/use", status_code=200)
async def use_delegation(
    delegation_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Registra uso de uma procuração e valida as restrições."""
    _require_flag(actor)
    store = _store()
    try:
        delegation = store.get("delegations", str(delegation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Delegação não encontrada.")

    _check_delegation_active(delegation)
    payload = delegation.get("payload", {})
    if str(actor.user_id) != str(payload.get("grantee_id")):
        raise HTTPException(
            status_code=403, detail="Apenas o beneficiário pode usar esta delegação."
        )

    constraints = payload.get("constraints", {})
    action = body.get("action", "")
    allowed_actions = constraints.get("allowed_actions", [])
    if allowed_actions and action not in allowed_actions:
        store.audit_external(
            "delegations",
            str(delegation_id),
            str(actor.user_id),
            "delegation_use_denied",
            {"reason": "action_not_allowed", "action": action},
        )
        raise HTTPException(
            status_code=403, detail=f"Ação '{action}' não permitida por esta delegação."
        )

    amount = body.get("amount")
    max_amount = constraints.get("max_amount")
    if (
        max_amount is not None
        and amount is not None
        and float(amount) > float(max_amount)
    ):
        raise HTTPException(
            status_code=403,
            detail=f"Valor R$ {amount} excede o limite R$ {max_amount}.",
        )

    if constraints.get("single_use", False):
        store.update(
            delegation,
            {"status": "expired", "expired_at": _now()},
            "expired",
            str(actor.user_id),
            "permissions.delegation.expired",
        )

    store.audit_external(
        "delegations",
        str(delegation_id),
        str(actor.user_id),
        "delegation_used",
        {"action": action, "amount": amount, "result": "allowed"},
    )
    return {"delegation_id": str(delegation_id), "result": "allowed", "action": action}


@app.post("/delegations/{delegation_id}/revoke", status_code=200)
async def revoke_delegation(
    delegation_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Revoga uma procuração operacional imediatamente."""
    _require_flag(actor)
    store = _store()
    try:
        delegation = store.get("delegations", str(delegation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Delegação não encontrada.")

    grantor_id = delegation.get("payload", {}).get("grantor_id") or delegation.get(
        "user_id"
    )
    if str(actor.user_id) != str(grantor_id) and "administrator" not in actor.roles:
        raise HTTPException(
            status_code=403, detail="Apenas o concedente pode revogar esta delegação."
        )

    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(
            status_code=422, detail="Motivo da revogação é obrigatório."
        )

    return store.update(
        delegation,
        {
            "status": "revoked",
            "revoked_at": _now(),
            "revoked_by": str(actor.user_id),
            "revocation_reason": reason,
        },
        "revoked",
        str(actor.user_id),
        "permissions.delegation.revoked",
    )


@app.get("/delegations")
async def list_delegations(
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Lista delegações do ator."""
    _require_flag(actor)
    return _store().list("delegations", str(actor.user_id), None, page=1, page_size=50)


@app.get("/delegations/feature-status")
async def feature_status() -> dict[str, Any]:
    return {
        "flag": _FLAG,
        "enabled": is_flag_enabled(_FLAG),
        "description": "Procuração Operacional Expirável – Primícia 3",
    }


@app.get("/delegations/{delegation_id}")
async def get_delegation(
    delegation_id: UUID, actor: Actor = Depends(actor_from_headers)
) -> dict[str, Any]:
    """Consulta uma delegação específica."""
    _require_flag(actor)
    store = _store()
    try:
        delegation = store.get("delegations", str(delegation_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Delegação não encontrada.")

    payload = delegation.get("payload", {})
    grantor_id = payload.get("grantor_id") or delegation.get("user_id")
    grantee_id = payload.get("grantee_id")
    if (
        str(actor.user_id) not in {str(grantor_id), str(grantee_id)}
        and "administrator" not in actor.roles
    ):
        raise HTTPException(status_code=403, detail="Acesso negado a esta delegação.")
    return delegation


app.include_router(primacia_router)
