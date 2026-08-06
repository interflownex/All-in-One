from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "compliance" / "report_access_readiness.py"
SPEC = importlib.util.spec_from_file_location("report_access_readiness", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
build_report = MODULE.build_report


def _contracts() -> tuple[dict, dict]:
    assets = {
        "issue": 204,
        "default_effect": "deny",
        "assets": [
            {
                "asset": "compliance.field_registry",
                "access_mode": "deny_all",
                "production_activation_blocked": True,
                "blockers": [
                    "owner_confirmation",
                    "consumer_inventory",
                    "security_review",
                    "dpo_legal_validation",
                ],
            }
        ],
    }
    attestations = {
        "required_evidence": {
            "owner_confirmation": {"required": True},
            "consumer_inventory": {"required": True},
            "security_review": {"required": True},
            "dpo_legal_validation": {"required": True},
        },
        "attestations": [],
    }
    return assets, attestations


def test_report_marks_unconfirmed_assets_blocked() -> None:
    assets, attestations = _contracts()

    report = build_report(assets, attestations)

    assert report["ready"] is False
    assert report["asset_count"] == 1
    asset = report["assets"][0]
    assert asset["ready"] is False
    assert asset["missing_required_evidence"] == [
        "consumer_inventory",
        "dpo_legal_validation",
        "owner_confirmation",
        "security_review",
    ]
    assert asset["production_activation_blocked"] is True
    assert asset["access_mode"] == "deny_all"


def test_pending_or_rejected_evidence_does_not_count() -> None:
    assets, attestations = _contracts()
    attestations["attestations"] = [
        {
            "asset": "compliance.field_registry",
            "evidence_type": "owner_confirmation",
            "status": "pending",
        },
        {
            "asset": "compliance.field_registry",
            "evidence_type": "security_review",
            "status": "rejected",
        },
    ]

    report = build_report(assets, attestations)

    asset = report["assets"][0]
    assert asset["accepted_evidence"] == []
    assert report["ready"] is False


def test_evidence_alone_cannot_override_contract_blockers() -> None:
    assets, attestations = _contracts()
    attestations["attestations"] = [
        {
            "asset": "compliance.field_registry",
            "evidence_type": evidence_type,
            "status": "accepted",
        }
        for evidence_type in attestations["required_evidence"]
    ]

    report = build_report(assets, attestations)

    asset = report["assets"][0]
    assert asset["missing_required_evidence"] == []
    assert asset["ready"] is False
    assert report["ready"] is False


def test_asset_is_ready_only_after_explicit_contract_activation() -> None:
    assets, attestations = _contracts()
    activated_assets = copy.deepcopy(assets)
    activated_assets["assets"][0]["access_mode"] = "purpose_scoped"
    activated_assets["assets"][0]["production_activation_blocked"] = False
    activated_assets["assets"][0]["blockers"] = []
    attestations["attestations"] = [
        {
            "asset": "compliance.field_registry",
            "evidence_type": evidence_type,
            "status": "accepted",
        }
        for evidence_type in attestations["required_evidence"]
    ]

    report = build_report(activated_assets, attestations)

    assert report["ready"] is True
    assert report["assets"][0]["ready"] is True
