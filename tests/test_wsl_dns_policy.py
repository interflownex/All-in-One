from __future__ import annotations

import json
from pathlib import Path

from scripts import configure_wsl_dns

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "autonomy" / "wsl_dns_policy.json"


def load_policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_wsl_dns_policy_declares_persistent_resolver_contract() -> None:
    policy = load_policy()

    assert policy["wsl"]["distro"] == "Ubuntu"
    assert policy["wsl"]["hostname"] == "all-in-one"
    assert policy["wsl"]["require_systemd"] is True
    assert policy["wsl"]["disable_generated_resolv_conf"] is True
    assert policy["resolved"]["resolv_conf_symlink_target"] == "/run/systemd/resolve/stub-resolv.conf"
    assert policy["resolved"]["stub_nameserver"] == "127.0.0.53"
    assert policy["resolved"]["dns"][:2] == ["10.255.255.254", "1.1.1.1"]
    assert "github.com" in policy["validation"]["hosts"]
    assert "stream.brasildesconto.com.br" in policy["validation"]["hosts"]


def test_wsl_dns_dropin_renderer_matches_policy() -> None:
    rendered = configure_wsl_dns.render_resolved_dropin(load_policy())

    assert rendered == (
        "[Resolve]\n"
        "DNS=10.255.255.254 1.1.1.1 8.8.8.8\n"
        "FallbackDNS=1.0.0.1 8.8.4.4 9.9.9.9\n"
        "Domains=~.\n"
        "DNSStubListener=yes\n"
    )


def test_wsl_dns_apply_requires_root(monkeypatch) -> None:
    monkeypatch.setattr(configure_wsl_dns.os, "geteuid", lambda: 1000)

    try:
        configure_wsl_dns.apply_policy(load_policy())
    except RuntimeError as exc:
        assert "wsl.exe -d Ubuntu -u root" in str(exc)
    else:
        raise AssertionError("apply_policy deve exigir root")
