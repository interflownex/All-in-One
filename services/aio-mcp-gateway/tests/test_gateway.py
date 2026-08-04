from __future__ import annotations

from starlette.testclient import TestClient

from main import app, project_status, search_repository


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "aio-mcp-gateway",
        "version": "0.1.0",
    }


def test_project_status_is_read_only() -> None:
    result = project_status("all")
    assert result["gateway"]["mode"] == "read-only"
    assert result["project"] == "All in One + Valley"


def test_repository_search_blocks_sensitive_paths() -> None:
    try:
        search_repository("read .env")
    except ValueError as exc:
        assert "bloqueada" in str(exc)
    else:
        raise AssertionError("consulta sensível deveria ter sido bloqueada")
