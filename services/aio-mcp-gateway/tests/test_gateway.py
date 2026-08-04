from __future__ import annotations

import os

import pytest
from starlette.testclient import TestClient

from main import (
    aio_admin_status,
    app,
    create_technical_report,
    project_status,
    read_project_document,
    search_repository,
    valley_consumer_status,
    valley_rider_status,
)


@pytest.fixture(autouse=True)
def auth_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AIO_MCP_AUTH_DISABLED", "true")


def test_health_is_independent_from_authentication() -> None:
    os.environ.pop("AIO_MCP_OIDC_ISSUER", None)
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]
    assert response.headers["x-trace-id"]


def test_project_status_is_read_only() -> None:
    result = project_status("all")
    assert result["gateway"]["mode"] == "read-only"
    assert result["mutating_tools_enabled"] is False


def test_report_is_never_persisted() -> None:
    result = create_technical_report("Relatório MCP", ["Evidências"])
    assert result["persisted"] is False
    assert "# Relatório MCP" in result["content"]


@pytest.mark.parametrize("value", ["../.env", "/etc/passwd", "folder\\secret", ""])
def test_document_identifier_blocks_path_traversal(value: str) -> None:
    with pytest.raises(ValueError):
        read_project_document(value)


@pytest.mark.parametrize("query", ["read .env", "../secret", "credentials", "id_rsa"])
def test_repository_search_blocks_sensitive_queries(query: str) -> None:
    with pytest.raises(ValueError):
        search_repository(query)


def test_domain_status_tools_are_read_only() -> None:
    assert valley_consumer_status()["mode"] == "read-only"
    assert valley_rider_status()["mode"] == "read-only"
    assert aio_admin_status()["mode"] == "read-only"


def test_mcp_requires_bearer_when_auth_is_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AIO_MCP_AUTH_DISABLED", "false")
    with TestClient(app) as client:
        response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert response.status_code == 401
    assert response.json() == {"error": "invalid_token"}
