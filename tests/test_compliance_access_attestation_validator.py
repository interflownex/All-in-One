from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/compliance/validate_access_attestations.py"
SPEC = importlib.util.spec_from_file_location("validate_access_attestations", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _registry() -> dict:
    return {"assets": [{"asset": "compliance.field_registry"}]}


def _contract() -> dict:
    return {
        "required_evidence": {
            "security_review": {
                "fields": ["asset", "review_status", "reviewed_at", "evidence_reference", "reviewed_by"]
            }
        },
        "attestations": [],
    }


def _approved() -> dict:
    return {
        "type": "security_review",
        "asset": "compliance.field_registry",
        "review_status": "approved",
        "reviewed_at": "2026-08-06T00:00:00Z",
        "evidence_reference": "github:interflownex/All-in-One#204",
        "reviewed_by": "security-team",
    }


def test_empty_contract_is_valid_and_fail_closed() -> None:
    assert MODULE.validate(_registry(), _contract()) == []


def test_valid_registered_attestation_is_accepted() -> None:
    contract = _contract()
    contract["attestations"] = [_approved()]
    assert MODULE.validate(_registry(), contract) == []


def test_unknown_asset_missing_fields_and_nonapproved_status_are_rejected() -> None:
    contract = _contract()
    attestation = _approved()
    attestation.update({"asset": "unknown.table", "review_status": "pending", "reviewed_by": ""})
    contract["attestations"] = [attestation]
    errors = MODULE.validate(_registry(), contract)
    assert any("unregistered asset" in error for error in errors)
    assert any("missing required field reviewed_by" in error for error in errors)
    assert any("cannot activate access" in error for error in errors)


def test_inline_secret_and_duplicate_evidence_are_rejected() -> None:
    contract = _contract()
    first = _approved()
    first["evidence_reference"] = "client_secret=do-not-store-here"
    contract["attestations"] = [first, copy.deepcopy(first)]
    errors = MODULE.validate(_registry(), contract)
    assert any("appears to contain a secret" in error for error in errors)
    assert any("duplicate evidence" in error for error in errors)
