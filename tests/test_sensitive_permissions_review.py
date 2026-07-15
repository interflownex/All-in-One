import json
from pathlib import Path

from modules.shared.domain_rules import (
    MEDICAL_ROLES,
    RECRUITER_ROLES,
    SENSITIVE_ROLES,
    can_read_sensitive,
    rule_for,
)


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "config" / "security" / "sensitive_permissions_review.json"
COMPLIANCE_PATH = ROOT / "config" / "compliance" / "data_classification.json"

REQUIRED_MODULES = {"identity", "finance", "jobs", "document", "health", "hr"}
RUNTIME_ROLES = {
    "SENSITIVE_ROLES": SENSITIVE_ROLES,
    "RECRUITER_ROLES": RECRUITER_ROLES,
    "MEDICAL_ROLES": MEDICAL_ROLES,
}


def load_review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def load_compliance() -> dict:
    return json.loads(COMPLIANCE_PATH.read_text(encoding="utf-8"))


def test_sensitive_permissions_review_covers_critical_modules_and_evidence() -> None:
    review = load_review()
    compliance = load_compliance()

    assert review["version"] == "2026-07-15"
    assert review["global_requirements"]["deny_by_default"] is True
    assert review["global_requirements"]["mfa_required_for_mutation"] is True
    assert review["global_requirements"]["audit_required_for_read"] is True
    assert review["global_requirements"]["raw_sensitive_payload_in_logs"] is False
    assert set(review["modules"]) == REQUIRED_MODULES

    for module_name, module_review in review["modules"].items():
        assert compliance["modules"][module_name]["risk_level"] == "critical"
        assert module_review["risk_level"] == "critical"
        assert module_review["sensitive_resources"], module_name
        assert module_review["allowed_read_roles"], module_name
        assert module_review["denied_read_roles"], module_name
        assert module_review["negative_tests"], module_name
        assert "audit_event_id" in module_review["required_evidence"], module_name
        assert "payload" not in " ".join(module_review["required_evidence"]).casefold(), module_name
        assert module_review["runtime_rule"] in RUNTIME_ROLES


def test_sensitive_permissions_review_matches_runtime_role_sets() -> None:
    review = load_review()

    for module_name, module_review in review["modules"].items():
        expected_roles = RUNTIME_ROLES[module_review["runtime_rule"]]
        assert set(module_review["allowed_read_roles"]) == set(expected_roles), module_name
        assert can_read_sensitive(module_name, frozenset(module_review["allowed_read_roles"])) is True
        assert can_read_sensitive(module_name, frozenset(module_review["denied_read_roles"])) is False


def test_sensitive_permissions_review_points_to_sensitive_runtime_resources() -> None:
    review = load_review()

    for module_name, module_review in review["modules"].items():
        for resource in module_review["sensitive_resources"]:
            rule = rule_for(module_name, resource)
            assert rule.sensitive is True or rule.immutable is True, f"{module_name}.{resource}"
