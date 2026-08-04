from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import jwt
import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = str(SERVICE_ROOT)
if SERVICE_PATH not in sys.path:
    sys.path.insert(0, SERVICE_PATH)

from security import (  # noqa: E402
    InMemoryRateLimiter,
    OIDCTokenVerifier,
    RateLimitBackendError,
    SecurityConfigurationError,
    SecurityMiddleware,
    SecuritySettings,
    build_transport_security,
    redact,
)


def _settings(
    *,
    auth_required: bool = False,
    rate_limit_requests: int = 120,
) -> SecuritySettings:
    return SecuritySettings(
        deployment_env="development",
        auth_required=auth_required,
        oidc_issuer=("https://identity.example.com" if auth_required else None),
        oidc_audience="aio-mcp-gateway" if auth_required else None,
        oidc_jwks_url=(
            "https://identity.example.com/.well-known/jwks.json"
            if auth_required
            else None
        ),
        oidc_algorithms=("RS256",),
        required_scope="aio:mcp:read",
        allowed_origins=frozenset(
            {
                "https://mcp.brasildesconto.com.br",
                "http://testserver",
            }
        ),
        allowed_hosts=frozenset({"mcp.brasildesconto.com.br", "testserver"}),
        protected_resource_url="https://mcp.brasildesconto.com.br/mcp",
        redis_url=None,
        rate_limit_requests=rate_limit_requests,
        rate_limit_window_seconds=60,
        max_request_body_bytes=1_048_576,
    )


def _clear_security_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "AUTH_REQUIRED",
        "OIDC_ISSUER",
        "OIDC_AUDIENCE",
        "OIDC_JWKS_URL",
        "OIDC_ALGORITHMS",
        "MCP_REQUIRED_SCOPE",
        "MCP_ALLOWED_ORIGINS",
        "MCP_ALLOWED_HOSTS",
        "PROTECTED_RESOURCE_URL",
        "REDIS_URL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_production_configuration_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_security_environment(monkeypatch)
    monkeypatch.setenv("DEPLOYMENT_ENV", "production")

    with pytest.raises(
        SecurityConfigurationError,
        match="OIDC_AUDIENCE",
    ):
        SecuritySettings.from_env()


def test_redact_removes_nested_secret_values() -> None:
    payload: dict[str, Any] = {
        "authorization": "Bearer secret",
        "nested": {
            "api_key": "abc",
            "safe": ["visible", {"password": "hidden"}],
        },
    }

    result = redact(payload)

    assert result == {
        "authorization": "[REDACTED]",
        "nested": {
            "api_key": "[REDACTED]",
            "safe": ["visible", {"password": "[REDACTED]"}],
        },
    }


def test_in_memory_rate_limiter_enforces_window() -> None:
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60)

    assert asyncio.run(limiter.allow("subject")) is True
    assert asyncio.run(limiter.allow("subject")) is True
    assert asyncio.run(limiter.allow("subject")) is False


def test_oidc_verifier_returns_native_access_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = OIDCTokenVerifier(_settings(auth_required=True))
    monkeypatch.setattr(
        verifier,
        "_decode",
        lambda token: {
            "sub": "user-123",
            "azp": "gemini-spark",
            "scope": "aio:mcp:read aio:github:read",
            "exp": 2_000_000_000,
            "iss": "https://identity.example.com",
            "aud": "aio-mcp-gateway",
        },
    )

    access_token = asyncio.run(verifier.verify_token("signed-token"))

    assert access_token is not None
    assert access_token.client_id == "gemini-spark"
    assert access_token.subject == "user-123"
    assert access_token.resource == "https://mcp.brasildesconto.com.br/mcp"
    assert access_token.scopes == ["aio:github:read", "aio:mcp:read"]


def test_oidc_verifier_rejects_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    verifier = OIDCTokenVerifier(_settings(auth_required=True))

    def invalid(_: str) -> dict[str, Any]:
        raise jwt.InvalidTokenError("invalid")

    monkeypatch.setattr(verifier, "_decode", invalid)

    assert asyncio.run(verifier.verify_token("invalid-token")) is None


def test_transport_security_uses_canonical_hosts() -> None:
    transport = build_transport_security(_settings())

    assert transport.enable_dns_rebinding_protection is True
    assert "mcp.brasildesconto.com.br" in transport.allowed_hosts
    assert "https://mcp.brasildesconto.com.br" in transport.allowed_origins


async def _ok(_: Request) -> JSONResponse:
    return JSONResponse({"ok": True})


def test_security_middleware_rate_limits_and_hardens_headers() -> None:
    settings = _settings(rate_limit_requests=1)
    app = SecurityMiddleware(
        Starlette(routes=[Route("/mcp", _ok)]),
        settings=settings,
        limiter=InMemoryRateLimiter(limit=1, window_seconds=60),
    )

    with TestClient(app) as client:
        first = client.get("/mcp")
        second = client.get("/mcp")

    assert first.status_code == 200
    assert first.headers["x-content-type-options"] == "nosniff"
    assert first.headers["permissions-policy"]
    assert second.status_code == 429
    assert second.headers["retry-after"] == "60"


class _BrokenLimiter:
    async def allow(self, _: str) -> bool:
        raise RateLimitBackendError("unavailable")

    async def close(self) -> None:
        return None


def test_security_middleware_fails_closed_when_limiter_breaks() -> None:
    app = SecurityMiddleware(
        Starlette(routes=[Route("/mcp", _ok)]),
        settings=_settings(),
        limiter=_BrokenLimiter(),
    )

    with TestClient(app) as client:
        response = client.get("/mcp")

    assert response.status_code == 503
    assert response.json()["error"] == "rate_limit_backend_unavailable"
