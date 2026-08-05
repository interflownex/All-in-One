import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "compliance" / "access_control.v1.json"
ASSETS_PATH = ROOT / "config" / "compliance" / "access_assets.v1.json"
EXPECTED_ASSETS = {
    "compliance.catalog_versions",
    "compliance.field_registry",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_access_assets_are_complete_and_fail_closed() -> None:
    contract = _load(CONTRACT_PATH)
    registry = _load(ASSETS_PATH)

    required_context = {
        item["setting"] for item in contract["session_context"].values()
    }
    assets = registry["assets"]

    assert registry["default_effect"] == "deny"
    assert registry["activation"] == "contract_only"
    assert {item["asset"] for item in assets} == EXPECTED_ASSETS

    for asset in assets:
        assert asset["owner"] is None
        assert asset["owner_status"] == "unconfirmed"
        assert asset["consumer_status"] == "unconfirmed"
        assert asset["allowed_consumers"] == []
        assert asset["allowed_purposes"] == []
        assert asset["access_mode"] == "deny_all"
        assert asset["rls_required"] is True
        assert asset["force_rls_required"] is True
        assert asset["application_role_may_own_table"] is False
        assert asset["bypass_rls_allowed"] is False
        assert asset["production_activation_blocked"] is True
        assert set(asset["required_context"]) == required_context
        assert {
            "owner_confirmation",
            "consumer_inventory",
            "minimum_policy_design",
            "security_review",
            "dpo_legal_validation",
        }.issubset(asset["blockers"])


def test_registry_does_not_predeclare_privileged_access() -> None:
    raw = ASSETS_PATH.read_text(encoding="utf-8").lower()

    forbidden_fragments = (
        '"access_mode": "allow"',
        '"bypass_rls_allowed": true',
        '"production_activation_blocked": false',
        '"application_role_may_own_table": true',
        '"allowed_consumers": ["',
        '"allowed_purposes": ["',
    )

    for fragment in forbidden_fragments:
        assert fragment not in raw
