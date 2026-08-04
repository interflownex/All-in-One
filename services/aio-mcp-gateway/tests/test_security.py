from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from security import (
    AuthContext,
    AuthenticationError,
    InMemoryRateLimiter,
    SecurityConfigurationError,
    SecurityMiddleware,
    SecuritySettings,
    protected_resource_metadata,
    redact,
)
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient


class StaticValidator:
    def __init__(
        self,
        scopes: frozenset[str],
        *,
        invalid_tokens: frozenset[str] = frozenset(),
    ) -> None:
        self._scopes = scopes
        self._invalid_tokens = invalid_tokens

    async def validate(self, token: str) -> AuthContext:
        if token in self._invalid_tokens:
            raise AuthenticationError("token inválido")
        return AuthContext(
            subject="user-123",
            scopes=self._scopes,
            claims={"sub": "user-123", "scope": " ".join(sorted(self._scopes))},
        )


async def echo(request: Request) -> JSONResponse:
    payload: Mapping[str, Any] = await request.json()
    return JSONResponse({"ok": True, "method": payload.get("method")})


def _settings(
    *,
    auth_required: bool = True,
    rate_limit_requests: int = 10,
    allowed_origins: frozenset[str] = frozenset(
        {"https://mcp.brasildesconto.com.br"}
    ),
) -> SecuritySettings:
    return SecuritySettings(
        deployment_env="test",
        auth_required=auth_required,
        oidc_issuer="https://issuer.example",
        oidc_audience="aio-mcp",
        oidc_jwks_url="https://issuer.example/.well-known/jwks.json",
        oidc_algorithms=("RS256",),
        allowed_origins=allowed_origins,
        protected_resource_url="https://mcp.brasildesconto.com.br",
        redis_url=None,
        rate_limit_requests=rate_limit_requests,
        rate_limit_window_seconds=60,
        max_request_body_bytes=4096,
    )


def _app(
    *,
    scopes: frozenset[str],
    rate_limit_requests: int = 10,
    invalid_tokens: frozenset[str] = frozenset(),
) -> Starlette:
    settings = _settings(rate_limit_requests=rate_limit_requests)
    limiter = InMemoryRateLimiter(rate_limit_requests, 60)
    validator = StaticValidator(scopes, invalid_tokens=invalid_tokens)
    return Starlette(
        routes=[Route("/mcp", endpoint=echo, methods=["POST"])],
        middleware=[
            Middleware(
                SecurityMiddleware,
                settings=settings,
                validator=validator,
                limiter=limiter,
            )
        ],
    )


def _tool_call(name: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": {}},
    }


def test_production_settings_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "AUTH_REQUIRED",
        "OIDC_ISSUER",
        "OIDC_AUDIENCE",
        "OIDC_JWKS_URL",
        "OIDC_ALGORITHMS",
        "REDIS_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DEPLOYMENT_ENV", "production")

    with pytest.raises(SecurityConfigurationError) as exc_info:
        SecuritySettings.from_env()

    message = str(exc_info.value)
    assert "OIDC_ISSUER" in message
    assert "OIDC_AUDIENCE" in message
    assert "OIDC_JWKS_URL" in message
    assert "REDIS_URL" in message


def test_missing_token_returns_oauth_challenge() -> None:
    app = _app(scopes=frozenset({"aio:mcp:read"}))
    with TestClient(app) as client:
        response = client.post("/mcp", json=_tool_call("project_status"))
    assert response.status_code == 401
    assert response.json()["error"] == "missing_token"
    assert "resource_metadata=" in response.headers["www-authenticate"]


def test_invalid_token_is_rejected() -> None:
    app = _app(
        scopes=frozenset({"aio:mcp:read"}),
        invalid_tokens=frozenset({"bad"}),
    )
    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            json=_tool_call("project_status"),
            headers={"authorization": "Bearer bad"},
        )
    assert response.status_code == 401
    assert response.json()["error"] == "invalid_token"


def test_invalid_origin_is_rejected_before_tool_execution() -> None:
    app = _app(scopes=frozenset({"aio:mcp:read"}))
    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            json=_tool_call("project_status"),
            headers={
                "authorization": "Bearer valid",
                "origin": "https://evil.example",
            },
        )
    assert response.status_code == 403
    assert response.json()["error"] == "origin_not_allowed"


def test_tool_specific_scope_is_required() -> None:
    app = _app(scopes=frozenset({"aio:mcp:read"}))
    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            json=_tool_call("search_repository"),
            headers={"authorization": "Bearer valid"},
        )
    assert response.status_code == 403
    payload = response.json()
    assert payload["error"] == "insufficient_scope"
    assert "aio:github:read" in payload["required_scopes"]


def test_authorized_request_reaches_downstream_app() -> None:
    app = _app(
        scopes=frozenset({"aio:mcp:read", "aio:github:read"}),
    )
    with TestClient(app) as client:
        response = client.post(
            "/mcp",
            json=_tool_call("search_repository"),
            headers={
                "authorization": "Bearer valid",
                "origin": "https://mcp.brasildesconto.com.br",
            },
        )
    assert response.status_code == 200
    assert response.json() == {"ok": True, "method": "tools/call"}
    assert response.headers["x-request-id"]
    assert response.headers["traceparent"].startswith("00-")


def test_rate_limit_is_enforced() -> None:
    app = _app(
        scopes=frozenset({"aio:mcp:read"}),
        rate_limit_requests=2,
    )
    headers = {"authorization": "Bearer valid"}
    with TestClient(app) as client:
        first = client.post("/mcp", json=_tool_call("project_status"), headers=headers)
        second = client.post("/mcp", json=_tool_call("project_status"), headers=headers)
        third = client.post("/mcp", json=_tool_call("project_status"), headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
    assert third.json()["error"] == "rate_limit_exceeded"


@pytest.mark.asyncio
async def test_memory_rate_limiter_resets_per_identity() -> None:
    limiter = InMemoryRateLimiter(limit=1, window_seconds=60)
    assert await limiter.allow("alpha") is True
    assert await limiter.allow("alpha") is False
    assert await limiter.allow("beta") is True
    await limiter.close()


def test_redaction_removes_nested_secrets() -> None:
    payload = {
        "authorization": "Bearer secret",
        "nested": {
            "api_key": "abc",
            "safe": "visible",
        },
    }
    assert redact(payload) == {
        "authorization": "[REDACTED]",
        "nested": {
            "api_key": "[REDACTED]",
            "safe": "visible",
        },
    }


def test_protected_resource_metadata_exposes_read_scopes() -> None:
    metadata = protected_resource_metadata(_settings())
    assert metadata["resource"] == "https://mcp.brasildesconto.com.br"
    assert metadata["authorization_servers"] == ["https://issuer.example"]
    assert "aio:mcp:read" in metadata["scopes_supported"]
    assert "aio:github:read" in metadata["scopes_supported"]
