from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCESS_ASSETS = ROOT / "config" / "compliance" / "access_assets.v1.json"
ACCESS_ATTESTATIONS = ROOT / "config" / "compliance" / "access_attestations.v1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_attestation_contract_starts_fail_closed_and_empty() -> None:
    contract = _load(ACCESS_ATTESTATIONS)

    assert contract["issue"] == 204
    assert contract["default_effect"] == "deny"
    assert contract["activation"] == "contract_only"
    assert contract["attestations"] == []

    rules = contract["activation_rules"]
    assert rules["all_required_evidence_must_exist"] is True
    assert rules["evidence_reference_must_be_non_secret"] is True
    assert rules["pending_or_rejected_evidence_denies_access"] is True
    assert rules["manual_status_override_forbidden"] is True
    assert rules["production_activation_requires_separate_pull_request"] is True


def test_every_external_blocker_has_required_evidence_contract() -> None:
    registry = _load(ACCESS_ASSETS)
    contract = _load(ACCESS_ATTESTATIONS)
    required_evidence = contract["required_evidence"]

    evidence_blockers = {
        "owner_confirmation",
        "consumer_inventory",
        "security_review",
        "dpo_legal_validation",
    }

    for asset in registry["assets"]:
        assert evidence_blockers.issubset(set(asset["blockers"]))

    assert set(required_evidence) == evidence_blockers
    for definition in required_evidence.values():
        assert definition["required"] is True
        assert "asset" in definition["fields"]
        assert "evidence_reference" in definition["fields"]
        assert "reviewed_by" in definition["fields"] or "validated_by" in definition["fields"]


def test_unconfirmed_assets_cannot_claim_operational_activation() -> None:
    registry = _load(ACCESS_ASSETS)
    contract = _load(ACCESS_ATTESTATIONS)

    assert contract["attestations"] == []
    for asset in registry["assets"]:
        assert asset["owner_status"] == "unconfirmed"
        assert asset["consumer_status"] == "unconfirmed"
        assert asset["allowed_consumers"] == []
        assert asset["allowed_purposes"] == []
        assert asset["production_activation_blocked"] is True
        assert asset["access_mode"] == "deny_all"
