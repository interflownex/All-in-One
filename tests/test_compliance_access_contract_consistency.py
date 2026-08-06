from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCESS_CONTROL = ROOT / "config" / "compliance" / "access_control.v1.json"
ACCESS_ASSETS = ROOT / "config" / "compliance" / "access_assets.v1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_access_assets_require_exactly_the_declared_session_context() -> None:
    control = _load(ACCESS_CONTROL)
    registry = _load(ACCESS_ASSETS)

    required_settings = {
        definition["setting"]
        for definition in control["session_context"].values()
        if definition["required"] is True
    }
    assert required_settings

    for asset in registry["assets"]:
        assert set(asset["required_context"]) == required_settings


def test_access_assets_preserve_the_global_fail_closed_contract() -> None:
    control = _load(ACCESS_CONTROL)
    registry = _load(ACCESS_ASSETS)

    assert registry["issue"] == control["issue"] == 204
    assert registry["default_effect"] == control["default_effect"] == "deny"
    assert control["privileged_access"]["bypass_rls_allowed"] is False
    assert control["database_contract"]["application_roles_must_not_own_tables"] is True
    assert control["database_contract"]["force_row_level_security"] is True
    assert control["database_contract"]["missing_context_denies_access"] is True

    for asset in registry["assets"]:
        assert asset["access_mode"] == "deny_all"
        assert asset["application_role_may_own_table"] is False
        assert asset["bypass_rls_allowed"] is False
        assert asset["rls_required"] is True
        assert asset["force_rls_required"] is True
        assert asset["allowed_consumers"] == []
        assert asset["allowed_purposes"] == []
        assert asset["production_activation_blocked"] is True


def test_unconfirmed_assets_keep_all_external_blockers_explicit() -> None:
    registry = _load(ACCESS_ASSETS)
    required_blockers = {
        "owner_confirmation",
        "consumer_inventory",
        "minimum_policy_design",
        "security_review",
        "dpo_legal_validation",
    }

    for asset in registry["assets"]:
        assert asset["owner"] is None
        assert asset["owner_status"] == "unconfirmed"
        assert asset["consumer_status"] == "unconfirmed"
        assert set(asset["blockers"]) == required_blockers
