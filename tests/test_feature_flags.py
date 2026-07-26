"""Testes das feature flags – Módulo compartilhado."""

import sys
from pathlib import Path

# Ajuste de path para testes
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules"))

import pytest
from shared.feature_flags import (
    PREMIUM_FLAGS,
    PRIMICIA_FLAGS,
    _env_key,
    flag_context,
    is_flag_enabled,
)


def test_all_23_flags_registered():
    """Todos os 23 recursos autorizados têm flags registradas (recurso 6 excluído)."""
    assert len(PRIMICIA_FLAGS) == 23
    # Recurso 6 NÃO deve estar registrado
    assert "primicia.stock.demand_before_showcase" not in PRIMICIA_FLAGS
    # Todos os outros devem estar
    expected_modules = {
        "identity",
        "business",
        "permissions",
        "finance",
        "marketplace",
        "delivery",
        "riders",
        "services",
        "mobility",
        "jobs",
        "erp",
        "wms",
        "tms",
        "crm",
        "bpm",
        "document",
        "hr",
        "health",
        "legal",
        "property",
        "bi",
        "ai",
        "api",
    }
    found_modules = {flag.split(".")[1] for flag in PRIMICIA_FLAGS}
    assert expected_modules == found_modules


def test_premium_flag_is_subset():
    """Flags Premium são subconjunto das flags de primícias."""
    assert PREMIUM_FLAGS.issubset(PRIMICIA_FLAGS)
    assert "primicia.mobility.intention_route_premium" in PREMIUM_FLAGS


def test_flag_disabled_by_default(monkeypatch):
    """Flags desligadas por padrão."""
    flag = "primicia.identity.minimum_proofs"
    monkeypatch.delenv(_env_key(flag), raising=False)
    assert is_flag_enabled(flag) is False


def test_flag_enabled_by_env_var(monkeypatch):
    """Flag habilitada via variável de ambiente."""
    flag = "primicia.identity.minimum_proofs"
    monkeypatch.setenv(_env_key(flag), "true")
    assert is_flag_enabled(flag) is True


def test_flag_enabled_by_tenant(monkeypatch):
    """Flag habilitada especificamente para um tenant."""
    flag = "primicia.business.flash_consortium"
    tenant_id = "abc123"
    tenant_key = f"{_env_key(flag)}__TENANT_{tenant_id.upper()}"
    monkeypatch.setenv(tenant_key, "1")
    monkeypatch.delenv(_env_key(flag), raising=False)
    assert is_flag_enabled(flag, tenant_id=tenant_id) is True
    assert is_flag_enabled(flag, tenant_id="outro-tenant") is False


def test_flag_enabled_by_user(monkeypatch):
    """Flag habilitada especificamente para um usuário."""
    flag = "primicia.permissions.expiring_delegation"
    user_id = "user-xyz"
    user_key = f"{_env_key(flag)}__USER_{user_id.upper().replace('-', '_')}"
    monkeypatch.setenv(user_key, "on")
    monkeypatch.delenv(_env_key(flag), raising=False)
    assert is_flag_enabled(flag, user_id=user_id) is True
    assert is_flag_enabled(flag, user_id="outro-user") is False


def test_unknown_flag_returns_false():
    """Flag desconhecida retorna False (segurança)."""
    assert is_flag_enabled("primicia.inexistente.recurso") is False


def test_flag_context_helper():
    """Helper flag_context gera dict de env vars para testes."""
    flags = ["primicia.identity.minimum_proofs", "primicia.finance.earmarked_money"]
    ctx = flag_context(flags)
    assert len(ctx) == 2
    for key, val in ctx.items():
        assert key.startswith("FF_PRIMICIA_")
        assert val == "true"


def test_require_flag_raises_402(monkeypatch):
    """require_flag levanta HTTPException 402 quando flag está desligada."""
    from fastapi import HTTPException
    from shared.feature_flags import require_flag

    flag = "primicia.wms.inventory_confidence"
    monkeypatch.delenv(_env_key(flag), raising=False)
    with pytest.raises(HTTPException) as exc_info:
        require_flag(flag)
    assert exc_info.value.status_code == 402
    assert exc_info.value.detail["code"] == "FEATURE_NOT_ENABLED"
    assert exc_info.value.detail["flag"] == flag


def test_mobility_premium_check_raises_402(monkeypatch):
    """Entitlement Premium levanta 402 sem credencial válida."""
    from fastapi import HTTPException
    from shared.feature_flags import check_premium_entitlement

    flag = "primicia.mobility.intention_route_premium"
    monkeypatch.delenv(_env_key(flag), raising=False)
    with pytest.raises(HTTPException) as exc_info:
        check_premium_entitlement(flag, user_id="user-1")
    assert exc_info.value.status_code == 402
