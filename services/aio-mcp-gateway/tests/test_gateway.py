from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from starlette.routing import Mount
from starlette.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]


def _load_gateway() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "aio_mcp_gateway_main",
        SERVICE_ROOT / "main.py",
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gateway = _load_gateway()
app = gateway.app
project_status = gateway.project_status
search_repository = gateway.search_repository


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "aio-mcp-gateway",
        "version": "0.1.0",
    }


def test_mcp_streamable_http_route_is_mounted() -> None:
    mounts = [route for route in app.routes if isinstance(route, Mount)]
    assert any(route.path == "/mcp" for route in mounts)


def test_project_status_is_read_only() -> None:
    result = project_status("all")
    assert result["gateway"]["mode"] == "read-only"
    assert result["project"] == "All in One + Valley"


def test_repository_search_blocks_sensitive_paths() -> None:
    with pytest.raises(ValueError, match="bloqueada"):
        search_repository("read .env")
