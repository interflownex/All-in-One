from __future__ import annotations

import json
from pathlib import Path

from scripts import configure_antigravity_trust

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "autonomy" / "antigravity_trust_policy.json"
CONTRACT = ROOT / ".agents" / "antigravity.json"


def load_policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_antigravity_policy_matches_agent_contract() -> None:
    policy = load_policy()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert contract["name"] == "antigravity"
    assert set(contract["mcp_servers"]) == set(policy["essential_mcp_servers"])
    assert set(policy["disabled_mcp_servers"]) <= {
        item["name"] for item in contract["disabled_mcp_servers"]
    }


def test_antigravity_generated_config_uses_only_env_placeholders() -> None:
    policy = load_policy()
    config = configure_antigravity_trust.build_mcp_config(
        policy, "/mnt/c/Users/ereta/.gemini/antigravity/mcp_config.json"
    )
    text = configure_antigravity_trust.serialize(config)

    assert set(config["mcpServers"]) == set(policy["essential_mcp_servers"])
    assert "CLOUDFLARE_API_TOKEN" in text
    assert "STITCH_API_KEY" in text
    assert "AQ." not in text
    assert "eyJ" not in text
    assert "sk-" not in text
    assert "AIza" not in text
    assert "datacloud_bigquery_remote" not in text
    assert "github-mcp-server" not in text


def test_antigravity_docker_mcp_uses_local_profile() -> None:
    policy = load_policy()
    config = configure_antigravity_trust.build_mcp_config(policy, str(ROOT))

    assert config["mcpServers"]["docker"]["args"] == [
        "mcp",
        "gateway",
        "run",
        "--profile",
        "all_in_one_local",
    ]
