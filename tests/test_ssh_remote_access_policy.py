from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_ssh_remote_access_policy_keeps_secrets_outside_git() -> None:
    policy = json.loads(
        (ROOT / "config/autonomy/ssh_remote_access_policy.json").read_text(
            encoding="utf-8"
        )
    )

    assert policy["enabled"] is True
    assert policy["access_channel"] == "tailscale_only"
    assert policy["server"]["authentication_methods"] == ["publickey"]
    assert policy["server"]["password_authentication"] is False
    assert policy["server"]["keyboard_interactive_authentication"] is False
    assert policy["server"]["permit_root_login"] is False
    assert policy["client_key"]["storage"] == "outside_git"
    assert policy["client_key"]["private_key_path"].startswith("/home/eretazan/.ssh/")
    assert policy["manual"]["storage"] == "outside_git"
    assert policy["manual"]["pdf_path"].startswith(
        "/home/eretazan/.local/share/all-in-one/secure/"
    )
    assert policy["tailscale"]["required"] is True
    assert policy["tailscale"]["accept_dns"] is True
    assert policy["cloudflare"]["publish_ssh"] is False
    assert "ssh" in policy["cloudflare"]["tunnel_must_not_expose"]
