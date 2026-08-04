from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = str(SERVICE_ROOT)
if SERVICE_PATH not in sys.path:
    sys.path.insert(0, SERVICE_PATH)

from production_invariants import (  # noqa: E402
    CANONICAL_PRODUCTION_RESOURCE,
    enforce_runtime_security_invariants,
)
from security import (  # noqa: E402
    SecurityConfigurationError,
    SecuritySettings,
)

PRODUCTION_ENV = {
    "DEPLOYMENT_ENV": "production",
    "AUTH_REQUIRED": "true",
    "OIDC_ISSUER": "https://identity.example.com",
    "OIDC_AUDIENCE": "aio-mcp-gateway",
    "OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
    "OIDC_ALGORITHMS": "RS256",
    "MCP_REQUIRED_SCOPE": "aio:mcp:read",
    "MCP_ALLOWED_ORIGINS": "https://mcp.brasildesconto.com.br",
    "MCP_ALLOWED_HOSTS": "mcp.brasildesconto.com.br",
    "PROTECTED_RESOURCE_URL": CANONICAL_PRODUCTION_RESOURCE,
    "REDIS_URL": "redis://redis.internal:6379/0",
}


def _load_production_settings(
    monkeypatch: pytest.MonkeyPatch,
    **overrides: str,
) -> SecuritySettings:
    for name, value in {**PRODUCTION_ENV, **overrides}.items():
        monkeypatch.setenv(name, value)
    return SecuritySettings.from_env()


def test_complete_production_configuration_is_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _load_production_settings(monkeypatch)

    assert enforce_runtime_security_invariants(settings) is settings


def test_production_cannot_disable_authentication(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _load_production_settings(
        monkeypatch,
        AUTH_REQUIRED="false",
    )

    with pytest.raises(
        SecurityConfigurationError,
        match="AUTH_REQUIRED_MUST_BE_TRUE",
    ):
        enforce_runtime_security_invariants(settings)


def test_production_requires_explicit_hosts_and_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _load_production_settings(monkeypatch)
    monkeypatch.delenv("MCP_ALLOWED_HOSTS")
    monkeypatch.delenv("MCP_ALLOWED_ORIGINS")

    with pytest.raises(SecurityConfigurationError) as error:
        enforce_runtime_security_invariants(settings)

    message = str(error.value)
    assert "MCP_ALLOWED_HOSTS_EXPLICIT" in message
    assert "MCP_ALLOWED_ORIGINS_EXPLICIT" in message


def test_production_rejects_symmetric_oidc_algorithm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _load_production_settings(
        monkeypatch,
        OIDC_ALGORITHMS="HS256",
    )

    with pytest.raises(
        SecurityConfigurationError,
        match="OIDC_ALGORITHMS_UNSAFE",
    ):
        enforce_runtime_security_invariants(settings)


def test_production_rejects_noncanonical_resource_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _load_production_settings(
        monkeypatch,
        PROTECTED_RESOURCE_URL=("https://mcp-preview.brasildesconto.com.br/mcp"),
    )

    with pytest.raises(
        SecurityConfigurationError,
        match="PROTECTED_RESOURCE_URL_CANONICAL",
    ):
        enforce_runtime_security_invariants(settings)


def test_production_rejects_wildcard_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = _load_production_settings(
        monkeypatch,
        MCP_ALLOWED_HOSTS="mcp.brasildesconto.com.br,localhost:*",
    )

    with pytest.raises(
        SecurityConfigurationError,
        match="MCP_ALLOWED_HOSTS_WILDCARD",
    ):
        enforce_runtime_security_invariants(settings)
