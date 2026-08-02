from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cloudflare_profile_keeps_runtime_secrets_out_of_git() -> None:
    profile_path = ROOT / "config" / "cloudflare" / "workspace_profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    serialized = json.dumps(profile, sort_keys=True)

    assert profile["account"]["account_id"] == "474fc26bf9c6bcf5e1a84b7f63a516d8"
    assert profile["pages"]["project_name"] == "all-in-one-web"
    assert profile["pages"]["production_branch"] == "main"
    assert "brasildesconto.com.br" in profile["pages"]["known_domains"]
    assert profile["tunnel"]["tunnel_name"] == "all-in-one-stream"
    assert profile["tunnel"]["tunnel_id"] == "7b9ce5bc-7f6e-4416-bff3-3a278ce4b96f"
    assert profile["tunnel"]["token_env_var"] == "CLOUDFLARE_TUNNEL_TOKEN"
    assert profile["mcp"]["api"]["bearer_token_env_var"] == "CLOUDFLARE_API_TOKEN"
    assert profile["tunnel"]["desired_public_hostnames"] == [
        {
            "hostname": "stream.brasildesconto.com.br",
            "origin": "http://127.0.0.1:8100",
            "purpose": "api_hub_stream_path",
        }
    ]
    assert profile["tunnel"]["reserved_public_hostnames"][0]["hostname"] == "api.brasildesconto.com.br"
    assert "AQ." not in serialized
    assert "BEGIN " not in serialized


def test_cloudflare_scripts_install_only_token_backed_service() -> None:
    configure = (ROOT / "scripts" / "configure_cloudflare_wsl.py").read_text(
        encoding="utf-8"
    )
    validate = (ROOT / "scripts" / "validate_cloudflare_wsl.py").read_text(
        encoding="utf-8"
    )

    assert "cloudflared-all-in-one.service" in configure
    assert "EnvironmentFile={token_file}" in configure
    assert "CLOUDFLARE_TUNNEL_TOKEN" in configure
    assert "CLOUDFLARE_TUNNEL_TOKEN" in validate
    assert "--strict" in validate
    assert "ssh" not in json.dumps(
        json.loads((ROOT / "config" / "cloudflare" / "workspace_profile.json").read_text())
    ).split('"do_not_expose"')[0]
