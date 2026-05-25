from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import hmac
import os
import time
from uuid import UUID

from fastapi import Header, HTTPException


RECRUITER_ROLES = frozenset({"owner", "administrator", "hr_manager", "recruiter", "auditor"})


@dataclass(frozen=True)
class Actor:
    user_id: UUID
    roles: frozenset[str]
    scopes: frozenset[str]
    mfa_verified: bool
    business_id: UUID | None = None
    business_status: str | None = None


def actor_from_headers(
    x_actor_user_id: UUID | None = Header(default=None, alias="X-Actor-User-Id"),
    x_actor_roles: str = Header(default="", alias="X-Actor-Roles"),
    x_actor_scopes: str = Header(default="", alias="X-Actor-Scopes"),
    x_mfa_verified: str = Header(default="false", alias="X-MFA-Verified"),
    x_business_id: UUID | None = Header(default=None, alias="X-Business-Id"),
    x_business_status: str | None = Header(default=None, alias="X-Business-Status"),
    x_gateway_timestamp: str | None = Header(default=None, alias="X-Gateway-Timestamp"),
    x_gateway_signature: str | None = Header(default=None, alias="X-Gateway-Signature"),
) -> Actor:
    if x_actor_user_id is None:
        raise HTTPException(status_code=401, detail="Ator autenticado obrigatorio.")
    roles = frozenset(item.strip().casefold() for item in x_actor_roles.split(",") if item.strip())
    scopes = frozenset(item.strip().casefold() for item in x_actor_scopes.split(",") if item.strip())
    actor = Actor(
        x_actor_user_id,
        roles,
        scopes,
        x_mfa_verified.casefold() == "true",
        x_business_id,
        x_business_status.casefold() if x_business_status else None,
    )
    if os.getenv("ALL_IN_ONE_ENV", "development").casefold() == "production":
        _verify_gateway_signature(actor, x_gateway_timestamp, x_gateway_signature)
    return actor


def _verify_gateway_signature(actor: Actor, timestamp: str | None, signature: str | None) -> None:
    secret = os.getenv("ALL_IN_ONE_TRUSTED_GATEWAY_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="Gateway signing secret ausente.")
    if not timestamp or not signature:
        raise HTTPException(status_code=401, detail="Assinatura do gateway obrigatoria.")
    try:
        issued_at = int(timestamp)
    except ValueError:
        raise HTTPException(status_code=401, detail="Timestamp do gateway invalido.") from None
    if abs(int(time.time()) - issued_at) > 300:
        raise HTTPException(status_code=401, detail="Assinatura do gateway expirada.")
    material = "|".join(
        [
            str(actor.user_id),
            ",".join(sorted(actor.roles)),
            ",".join(sorted(actor.scopes)),
            str(actor.mfa_verified).lower(),
            str(actor.business_id or ""),
            actor.business_status or "",
            timestamp,
        ]
    )
    expected = hmac.new(secret.encode(), material.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Assinatura do gateway invalida.")


def demand_role(actor: Actor, accepted: frozenset[str], action: str) -> None:
    if accepted and not actor.roles.intersection(accepted):
        raise HTTPException(status_code=403, detail=f"Perfil sem permissao para {action}.")


def demand_mfa(actor: Actor, action: str) -> None:
    if not actor.mfa_verified:
        raise HTTPException(status_code=403, detail=f"MFA obrigatorio para {action}.")


def demand_active_business_recruiter(
    actor: Actor,
    action: str = "consultar curriculos",
    required_scope: str = "jobs:resumes:read",
) -> None:
    if actor.business_id is None or actor.business_status != "active":
        raise HTTPException(status_code=403, detail="Acesso exclusivo a empresa ativa no All-in-One Business.")
    demand_role(actor, RECRUITER_ROLES, action)
    if required_scope not in actor.scopes and "jobs:manage" not in actor.scopes:
        raise HTTPException(status_code=403, detail="Escopo Business Jobs ausente.")
