from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import hmac
import os
import time
from uuid import UUID

from fastapi import Header, HTTPException

from .audit_contract import AuditContext, set_audit_context


RECRUITER_ROLES = frozenset({"owner", "administrator", "hr_manager", "recruiter", "auditor"})


@dataclass(frozen=True)
class Actor:
    user_id: UUID
    roles: frozenset[str]
    scopes: frozenset[str]
    mfa_verified: bool
    business_id: UUID | None = None
    business_status: str | None = None
    business_plan: str | None = None
    business_cnpj: str | None = None
    valley_master_account: bool = False


def actor_from_headers(
    x_actor_user_id: UUID | None = Header(default=None, alias="X-Actor-User-Id"),
    x_actor_roles: str = Header(default="", alias="X-Actor-Roles"),
    x_actor_scopes: str = Header(default="", alias="X-Actor-Scopes"),
    x_mfa_verified: str = Header(default="false", alias="X-MFA-Verified"),
    x_business_id: UUID | None = Header(default=None, alias="X-Business-Id"),
    x_business_status: str | None = Header(default=None, alias="X-Business-Status"),
    x_business_plan: str | None = Header(default=None, alias="X-Business-Plan"),
    x_business_cnpj: str | None = Header(default=None, alias="X-Business-CNPJ"),
    x_valley_master_account: str = Header(default="false", alias="X-Valley-Master-Account"),
    x_gateway_timestamp: str | None = Header(default=None, alias="X-Gateway-Timestamp"),
    x_gateway_signature: str | None = Header(default=None, alias="X-Gateway-Signature"),
    x_tenant_id: UUID | None = Header(default=None, alias="X-Tenant-Id"),
    x_audit_session_id: str | None = Header(default=None, alias="X-Audit-Session-Id"),
    x_device_fingerprint: str | None = Header(default=None, alias="X-Device-Fingerprint"),
    x_forwarded_for: str | None = Header(default=None, alias="X-Forwarded-For"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
    x_client_origin: str = Header(default="web", alias="X-Client-Origin"),
    x_client_channel: str = Header(default="api", alias="X-Client-Channel"),
    x_audit_reason: str | None = Header(default=None, alias="X-Audit-Reason"),
    x_causation_id: UUID | None = Header(default=None, alias="X-Causation-Id"),
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
        x_business_plan.casefold() if x_business_plan else None,
        _digits_only(x_business_cnpj) if x_business_cnpj else None,
        x_valley_master_account.casefold() == "true",
    )
    if os.getenv("ALL_IN_ONE_ENV", "development").casefold() == "production":
        _verify_gateway_signature(actor, x_gateway_timestamp, x_gateway_signature)
    allowed_channels = {"api", "web", "mobile", "worker", "integration", "admin"}
    channel = x_client_channel.casefold() if x_client_channel.casefold() in allowed_channels else "api"
    set_audit_context(AuditContext(
        tenant_id=str(x_tenant_id) if x_tenant_id else None,
        company_id=str(actor.business_id) if actor.business_id else None,
        actor_role=",".join(sorted(actor.roles))[:200] or None,
        session_id=x_audit_session_id[:180] if x_audit_session_id else None,
        device_id=x_device_fingerprint[:180] if x_device_fingerprint else None,
        ip_address=x_forwarded_for.split(",", maxsplit=1)[0].strip()[:64] if x_forwarded_for else None,
        user_agent=user_agent[:500] if user_agent else None,
        origin=x_client_origin.casefold()[:100], channel=channel,
        reason=x_audit_reason[:500] if x_audit_reason else None,
        causation_id=str(x_causation_id) if x_causation_id else None,
        authorization=",".join(sorted(actor.scopes))[:1000] or None,
    ))
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
            actor.business_plan or "",
            actor.business_cnpj or "",
            str(actor.valley_master_account).lower(),
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


def _digits_only(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


def demand_active_business(actor: Actor, action: str = "operar no Valley Business") -> None:
    if actor.business_id is None or actor.business_status != "active":
        raise HTTPException(status_code=403, detail="Acesso exclusivo a empresa ativa no All-in-One Business.")
    demand_role(actor, frozenset({"owner", "administrator", "merchant", "store_manager", "auditor"}), action)


def demand_valley_master_stock(actor: Actor) -> None:
    if actor.valley_master_account or "valley_master" in actor.roles or "stock:global:import" in actor.scopes:
        return
    raise HTTPException(status_code=403, detail="Modulo Stock global exclusivo da conta mestre corporativa Valley.")


def enforce_essential_plan(actor: Actor, payload: dict[str, object]) -> None:
    if actor.business_plan != "essential":
        return
    if not actor.business_cnpj:
        raise HTTPException(status_code=403, detail="Plano Essencial exige CNPJ autenticado no contexto Business.")
    blocked = payload.get("external_integrations") or payload.get("integration_provider") or payload.get("external_provider")
    if blocked:
        raise HTTPException(status_code=403, detail="Integracoes externas bloqueadas no Plano Essencial.")
    payload_cnpj = payload.get("cnpj") or payload.get("document_cnpj")
    if payload_cnpj and _digits_only(str(payload_cnpj)) != actor.business_cnpj:
        raise HTTPException(status_code=403, detail="Plano Essencial permite apenas o CNPJ autenticado da propria unidade.")
    root_cnpj = payload.get("root_cnpj")
    if root_cnpj and _digits_only(str(root_cnpj)) != actor.business_cnpj:
        raise HTTPException(status_code=403, detail="Plano Essencial nao permite matriz/filiais no mesmo cadastro.")
