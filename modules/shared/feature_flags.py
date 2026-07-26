"""Feature flags para primícias do All in One + Valley.

Padrão:
  - Desligadas por padrão em produção.
  - Ativação por variável de ambiente, empresa ou usuário.
  - Registro de quem ativou, quando e por quê (via tabela feature_flag_activations).
  - Desligamento imediato possível.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

# ---------------------------------------------------------------------------
# Catálogo oficial de flags das primícias
# ---------------------------------------------------------------------------

PRIMICIA_FLAGS: frozenset[str] = frozenset(
    {
        "primicia.identity.minimum_proofs",  # Recurso 1
        "primicia.business.flash_consortium",  # Recurso 2
        "primicia.permissions.expiring_delegation",  # Recurso 3
        "primicia.finance.earmarked_money",  # Recurso 4
        "primicia.marketplace.local_buying_coalition",  # Recurso 5
        # Recurso 6 EXCLUÍDO – não criar flag
        "primicia.delivery.route_capacity",  # Recurso 7
        "primicia.riders.evidence_passport",  # Recurso 8
        "primicia.services.outcome_contract",  # Recurso 9
        "primicia.mobility.intention_route_premium",  # Recurso 10 (Premium)
        "primicia.jobs.reverse_availability",  # Recurso 11
        "primicia.erp.continuous_close",  # Recurso 12
        "primicia.wms.inventory_confidence",  # Recurso 13
        "primicia.tms.blind_capacity_exchange",  # Recurso 14
        "primicia.crm.customer_promises",  # Recurso 15
        "primicia.bpm.process_laboratory",  # Recurso 16
        "primicia.document.living_obligations",  # Recurso 17
        "primicia.hr.fair_affinity_schedule",  # Recurso 18
        "primicia.health.continuity_capsule",  # Recurso 19
        "primicia.legal.impact_radar",  # Recurso 20
        "primicia.property.shared_capacity",  # Recurso 21
        "primicia.bi.unasked_questions",  # Recurso 22
        "primicia.ai.memory_receipt",  # Recurso 23
        "primicia.api.adaptive_contract",  # Recurso 24
    }
)

# Flags Premium (exigem entitlement além da flag)
PREMIUM_FLAGS: frozenset[str] = frozenset({"primicia.mobility.intention_route_premium"})


# ---------------------------------------------------------------------------
# Verificação simples via variável de ambiente (padrão desligado)
# ---------------------------------------------------------------------------


def _env_key(flag: str) -> str:
    """Converte 'primicia.identity.minimum_proofs' → 'FF_PRIMICIA_IDENTITY_MINIMUM_PROOFS'."""
    return "FF_" + flag.upper().replace(".", "_")


def is_flag_enabled(
    flag: str,
    *,
    tenant_id: str | None = None,
    user_id: str | None = None,
    extra_context: dict[str, Any] | None = None,
) -> bool:
    """Verifica se uma feature flag está habilitada.

    Ordem de precedência:
      1. Env var global  FF_<FLAG> (sem tenant/user)
      2. Env var por tenant  FF_<FLAG>__TENANT_<tenant_id>
      3. Env var por user    FF_<FLAG>__USER_<user_id>
      4. Padrão: desligado
    """
    if flag not in PRIMICIA_FLAGS:
        return False

    env_key = _env_key(flag)

    def _truthy(val: str | None) -> bool:
        return (val or "").strip().lower() in {"1", "true", "yes", "on"}

    # Global
    if _truthy(os.getenv(env_key)):
        return True

    # Por tenant
    if tenant_id:
        tenant_key = f"{env_key}__TENANT_{tenant_id.upper().replace('-', '_')}"
        if _truthy(os.getenv(tenant_key)):
            return True

    # Por usuário
    if user_id:
        user_key = f"{env_key}__USER_{user_id.upper().replace('-', '_')}"
        if _truthy(os.getenv(user_key)):
            return True

    return False


def require_flag(
    flag: str,
    *,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> None:
    """Levanta HTTPException 402 se a flag não estiver habilitada."""
    from fastapi import HTTPException  # import local para evitar ciclo

    if not is_flag_enabled(flag, tenant_id=tenant_id, user_id=user_id):
        raise HTTPException(
            status_code=402,
            detail={
                "code": "FEATURE_NOT_ENABLED",
                "flag": flag,
                "message": (
                    "Este recurso não está habilitado para o seu plano ou ambiente. "
                    "Contate o suporte para ativação."
                ),
            },
        )


# ---------------------------------------------------------------------------
# Entitlements (direitos de uso)
# ---------------------------------------------------------------------------


@dataclass
class Entitlement:
    user_id: str
    tenant_id: str | None
    flag: str
    plan: str
    valid_from: str
    valid_until: str | None = None
    limit_units: int | None = None
    consumed_units: int = 0
    promotional: bool = False
    revoked: bool = False
    revoked_at: str | None = None
    revoked_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        if self.revoked:
            return False
        now = datetime.now(UTC).isoformat()
        if self.valid_until and self.valid_until < now:
            return False
        return True

    def has_quota(self) -> bool:
        if self.limit_units is None:
            return True
        return self.consumed_units < self.limit_units


def check_premium_entitlement(
    flag: str,
    *,
    user_id: str,
    tenant_id: str | None = None,
    entitlement: Entitlement | None = None,
) -> None:
    """Verifica entitlement Premium antes de cobrar ou liberar acesso.

    Se entitlement não for fornecido, verifica apenas via flag de ambiente
    (útil em testes e ambientes sem banco).
    """
    from fastapi import HTTPException

    if flag not in PREMIUM_FLAGS:
        return  # Não é Premium, verificação de flag simples basta

    if entitlement is not None:
        if not entitlement.is_active():
            raise HTTPException(
                status_code=402,
                detail={
                    "code": "ENTITLEMENT_INACTIVE",
                    "flag": flag,
                    "message": "Seu direito de uso para este serviço Premium expirou ou foi revogado.",
                },
            )
        if not entitlement.has_quota():
            raise HTTPException(
                status_code=402,
                detail={
                    "code": "ENTITLEMENT_QUOTA_EXCEEDED",
                    "flag": flag,
                    "message": "Limite de uso do serviço Premium atingido para o período.",
                },
            )
        return

    # Fallback: verifica por variável de ambiente
    require_flag(flag, tenant_id=tenant_id, user_id=user_id)


# ---------------------------------------------------------------------------
# Helpers de contexto para testes
# ---------------------------------------------------------------------------


def flag_context(flags: list[str]) -> dict[str, str]:
    """Retorna dict de env vars para habilitar flags em testes."""
    return {_env_key(f): "true" for f in flags}
