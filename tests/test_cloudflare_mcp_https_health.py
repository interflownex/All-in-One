from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_cloudflare_mcp_dns.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cloudflare_mcp_https", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dns = _load_module()


class _Response:
    status = 200

    def read(self) -> bytes:
        return b'{"status":"ok"}'


class _Connection:
    instances: list[_Connection] = []

    def __init__(self, host: str, port: int, timeout: int) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.request_args: tuple[str, str, dict[str, str]] | None = None
        self.closed = False
        self.instances.append(self)

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str],
    ) -> None:
        self.request_args = (method, path, headers)

    def getresponse(self) -> _Response:
        return _Response()

    def close(self) -> None:
        self.closed = True


def test_verify_https_uses_fixed_tls_connection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _Connection.instances.clear()
    monkeypatch.setattr(dns.http.client, "HTTPSConnection", _Connection)

    dns.verify_https("https://mcp.brasildesconto.com.br/health")

    connection = _Connection.instances[0]
    assert connection.host == "mcp.brasildesconto.com.br"
    assert connection.port == 443
    assert connection.timeout == 20
    assert connection.request_args == (
        "GET",
        "/health",
        {
            "User-Agent": "aio-mcp-dns-validator/1.0",
            "Accept": "application/json",
        },
    )
    assert connection.closed is True


@pytest.mark.parametrize(
    "health_url",
    [
        "http://mcp.brasildesconto.com.br/health",
        "https://example.com/health",
        "https://mcp-admin.brasildesconto.com.br/health",
        "https://mcp.brasildesconto.com.br/status",
        "https://mcp.brasildesconto.com.br:8443/health",
        "https://user:password@mcp.brasildesconto.com.br/health",
        "https://mcp.brasildesconto.com.br/health?token=value",
        "https://mcp.brasildesconto.com.br/health#fragment",
    ],
)
def test_verify_https_rejects_unapproved_urls(health_url: str) -> None:
    with pytest.raises(dns.ConfigurationError, match="health URL"):
        dns.verify_https(health_url)


def test_verify_https_rejects_non_ok_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BadResponse(_Response):
        def read(self) -> bytes:
            return b'{"status":"degraded"}'

    class BadConnection(_Connection):
        def getresponse(self) -> BadResponse:
            return BadResponse()

    monkeypatch.setattr(dns.http.client, "HTTPSConnection", BadConnection)

    with pytest.raises(RuntimeError, match="status=ok"):
        dns.verify_https("https://mcp-preview.brasildesconto.com.br/health")
