from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path
from types import ModuleType

import pytest
from starlette.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
SECURITY_ENV_VARS = (
    "DEPLOYMENT_ENV",
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
    "RATE_LIMIT_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "MAX_REQUEST_BODY_BYTES",
)


def _load_gateway(
    monkeypatch: pytest.MonkeyPatch,
    **environment: str,
) -> ModuleType:
    for name in SECURITY_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    service_path = str(SERVICE_ROOT)
    if service_path not in sys.path:
        sys.path.insert(0, service_path)

    module_name = f"aio_mcp_gateway_main_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        module_name,
        SERVICE_ROOT / "main.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _auth_environment() -> dict[str, str]:
    return {
        "AUTH_REQUIRED": "true",
        "OIDC_ISSUER": "https://identity.example.com",
        "OIDC_AUDIENCE": "aio-mcp-gateway",
        "OIDC_JWKS_URL": "https://identity.example.com/.well-known/jwks.json",
        "PROTECTED_RESOURCE_URL": "https://mcp.brasildesconto.com.br/mcp",
    }


def test_health_is_public_and_hardened(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch)

    with TestClient(gateway.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "aio-mcp-gateway",
        "version": "0.2.0",
        "mode": "development",
        "auth_required": False,
        "rate_limit_backend": "memory",
    }
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-request-id"]
    assert response.headers["traceparent"].startswith("00-")


def test_canonical_mcp_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch)

    assert gateway.mcp.settings.streamable_http_path == "/mcp"
    assert (
        gateway.security_settings.protected_resource_url
        == "https://mcp.brasildesconto.com.br/mcp"
    )
    assert "mcp.brasildesconto.com.br" in gateway.security_settings.allowed_hosts
    assert (
        "https://mcp-staging.brasildesconto.com.br"
        in gateway.security_settings.allowed_origins
    )


def test_project_status_is_read_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch)

    result = gateway.project_status("all")

    assert result["gateway"]["mode"] == "read-only"
    assert result["project"] == "All in One + Valley"
    assert (
        result["canonical_endpoint"]
        == "https://mcp.brasildesconto.com.br/mcp"
    )


def test_repository_search_blocks_sensitive_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch)

    with pytest.raises(ValueError, match="bloqueada"):
        gateway.search_repository("read .env")


def test_oauth_protected_resource_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch, **_auth_environment())

    with TestClient(gateway.app) as client:
        response = client.get(
            "/.well-known/oauth-protected-resource/mcp"
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["resource"] == "https://mcp.brasildesconto.com.br/mcp"
    assert payload["authorization_servers"][0].startswith(
        "https://identity.example.com"
    )
    assert payload["scopes_supported"] == ["aio:mcp:read"]


def test_mcp_rejects_missing_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch, **_auth_environment())

    with TestClient(gateway.app) as client:
        response = client.post(
            "/mcp",
            headers={
                "host": "mcp.brasildesconto.com.br",
                "content-type": "application/json",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"},
                },
            },
        )

    assert response.status_code == 401
    challenge = response.headers["www-authenticate"]
    assert "Bearer" in challenge
    assert (
        "https://mcp.brasildesconto.com.br/"
        ".well-known/oauth-protected-resource/mcp"
        in challenge
    )


def test_health_remains_public_when_auth_is_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch, **_auth_environment())

    with TestClient(gateway.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["auth_required"] is True


def test_every_registered_tool_has_a_scope_policy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = _load_gateway(monkeypatch)
    registered = {tool.name for tool in gateway.mcp._tool_manager.list_tools()}

    assert registered == set(gateway.DEFAULT_TOOL_SCOPES)
    assert all(gateway.DEFAULT_TOOL_SCOPES.values())
