from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_cloudflare_mcp_dns.py"
PLAN = ROOT / "config" / "cloudflare" / "mcp_dns_plan.json"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cloudflare_mcp_dns", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dns = _load_module()


def _plan() -> dict[str, Any]:
    return json.loads(PLAN.read_text(encoding="utf-8"))


def test_plan_uses_only_brasildesconto_subdomains() -> None:
    plan = _plan()
    dns.validate_plan(plan)
    assert plan["zone_name"] == "brasildesconto.com.br"
    assert plan["canonical"]["hostname"] == "mcp.brasildesconto.com.br"
    environment_hostnames = {
        item["environment"]: item["hostname"] for item in plan["environments"]
    }
    assert environment_hostnames == {
        "staging": "mcp-staging.brasildesconto.com.br",
        "preview": "mcp-preview.brasildesconto.com.br",
    }
    hostnames = {
        plan["canonical"]["hostname"],
        *environment_hostnames.values(),
        *(item["hostname"] for item in plan["aliases"]),
    }
    assert "brasildesconto.com.br" not in hostnames
    assert all(name.endswith(".brasildesconto.com.br") for name in hostnames)
    assert all("*" not in name for name in hostnames)


def test_production_records_use_one_gateway_and_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MCP_PRODUCTION_DNS_TARGET", "origin.example.net")
    records = list(
        dns.iter_plan_records(
            _plan(),
            environment="production",
            require_targets=True,
        )
    )
    assert records[0]["name"] == "mcp.brasildesconto.com.br"
    assert records[0]["content"] == "origin.example.net"
    aliases = records[1:]
    assert {item["name"] for item in aliases} == {
        "mcp-valley.brasildesconto.com.br",
        "mcp-rider.brasildesconto.com.br",
        "mcp-admin.brasildesconto.com.br",
    }
    assert {item["content"] for item in aliases} == {"mcp.brasildesconto.com.br"}


def test_missing_environment_target_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MCP_PRODUCTION_DNS_TARGET", raising=False)
    with pytest.raises(dns.ConfigurationError, match="MCP_PRODUCTION_DNS_TARGET"):
        list(
            dns.iter_plan_records(
                _plan(),
                environment="production",
                require_targets=True,
            )
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("allow_apex_changes", True, "domínio raiz"),
        ("allow_wildcards", True, "wildcards"),
        ("allow_delete", True, "remoção"),
    ],
)
def test_guardrails_cannot_be_relaxed(
    field: str,
    value: bool,
    message: str,
) -> None:
    plan = copy.deepcopy(_plan())
    plan["guardrails"][field] = value
    with pytest.raises(dns.ConfigurationError, match=message):
        dns.validate_plan(plan)


def test_url_is_rejected_as_cname_target() -> None:
    with pytest.raises(dns.ConfigurationError, match="apenas hostname"):
        dns._validate_target(
            "https://origin.example.net/path",
            "mcp.brasildesconto.com.br",
        )


@pytest.mark.parametrize(
    "target",
    [
        "127.0.0.1",
        "single-label",
        "-invalid.example.net",
        "invalid-.example.net",
        "invalid_underscore.example.net",
    ],
)
def test_invalid_cname_targets_are_rejected(target: str) -> None:
    with pytest.raises(dns.ConfigurationError, match="target CNAME"):
        dns._validate_target(target, "mcp.brasildesconto.com.br")


class ZoneClient(dns.CloudflareClient):
    def __init__(self, result: dict[str, Any]) -> None:
        super().__init__("test-token")
        self.result = result

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        assert method == "GET"
        assert path.startswith("/zones/")
        assert payload is None
        return {"success": True, "result": self.result}


def test_explicit_zone_id_must_belong_to_allowed_zone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLOUDFLARE_ZONE_ID", "a" * 32)
    client = ZoneClient(
        {
            "name": "example.com",
            "status": "active",
            "account": {"id": "account-id"},
        }
    )
    with pytest.raises(dns.CloudflareAPIError, match="não a brasildesconto.com.br"):
        client.zone_id("brasildesconto.com.br", "account-id")


def test_explicit_zone_id_must_be_active_and_match_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CLOUDFLARE_ZONE_ID", "b" * 32)
    inactive = ZoneClient(
        {
            "name": "brasildesconto.com.br",
            "status": "pending",
            "account": {"id": "account-id"},
        }
    )
    with pytest.raises(dns.CloudflareAPIError, match="não está ativa"):
        inactive.zone_id("brasildesconto.com.br", "account-id")

    other_account = ZoneClient(
        {
            "name": "brasildesconto.com.br",
            "status": "active",
            "account": {"id": "other-account"},
        }
    )
    with pytest.raises(dns.CloudflareAPIError, match="outra conta"):
        other_account.zone_id("brasildesconto.com.br", "account-id")


class FakeClient(dns.CloudflareClient):
    def __init__(self, existing: list[dict[str, Any]]) -> None:
        self.existing = existing
        self.calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def find_record(
        self,
        zone_id: str,
        name: str,
    ) -> list[dict[str, Any]]:
        assert zone_id == "zone-id"
        return self.existing

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.calls.append((method, path, payload))
        return {"success": True, "result": {}}


def _desired() -> dict[str, Any]:
    return {
        "name": "mcp.brasildesconto.com.br",
        "type": "CNAME",
        "content": "origin.example.net",
        "proxied": True,
        "ttl": 1,
        "comment": "managed",
    }


def test_upsert_check_reports_missing_without_mutation() -> None:
    client = FakeClient([])
    assert client.upsert_record("zone-id", _desired(), apply=False) == "missing"
    assert client.calls == []


def test_upsert_apply_creates_missing_record() -> None:
    client = FakeClient([])
    assert client.upsert_record("zone-id", _desired(), apply=True) == "created"
    assert client.calls[0][0] == "POST"


def test_upsert_is_idempotent() -> None:
    existing = [
        {
            "id": "record-id",
            "type": "CNAME",
            "content": "origin.example.net",
            "proxied": True,
            "ttl": 1,
        }
    ]
    client = FakeClient(existing)
    assert client.upsert_record("zone-id", _desired(), apply=True) == "unchanged"
    assert client.calls == []


def test_upsert_check_reports_drift() -> None:
    existing = [
        {
            "id": "record-id",
            "type": "CNAME",
            "content": "old.example.net",
            "proxied": True,
            "ttl": 1,
        }
    ]
    client = FakeClient(existing)
    assert client.upsert_record("zone-id", _desired(), apply=False) == "drift"
    assert client.calls == []


def test_upsert_refuses_type_conflict() -> None:
    existing = [
        {
            "id": "record-id",
            "type": "A",
            "content": "192.0.2.1",
            "proxied": True,
            "ttl": 1,
        }
    ]
    client = FakeClient(existing)
    with pytest.raises(dns.CloudflareAPIError, match="conflito de tipo"):
        client.upsert_record("zone-id", _desired(), apply=True)
