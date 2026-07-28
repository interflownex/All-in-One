import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AUDIT_EVENTS = {
    "compliance.retention.reviewed",
    "compliance.data.anonymized",
    "compliance.data.deleted",
    "compliance.legal_hold.applied",
}
REQUIRED_JOBS = {
    "retention_review_daily",
    "anonymization_worker_hourly",
    "deletion_worker_daily",
    "legal_hold_reconciliation_daily",
}
CRITICAL_MODULES = {
    "identity",
    "finance",
    "jobs",
    "document",
    "hr",
    "health",
    "ai_core",
    "api_hub",
}


def load_catalog_modules() -> set[str]:
    catalog = json.loads(
        (ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8")
    )
    return {module["slug"] for module in catalog["modules"]}


def load_rights() -> dict:
    return json.loads(
        (ROOT / "config" / "compliance" / "data_subject_rights.json").read_text(
            encoding="utf-8"
        )
    )


def load_retention() -> dict:
    return json.loads(
        (ROOT / "config" / "compliance" / "retention_jobs.json").read_text(
            encoding="utf-8"
        )
    )


def test_retention_jobs_cover_all_modules_and_subject_rights() -> None:
    retention = load_retention()
    rights = load_rights()

    assert retention["safety_rules"]["requires_subject_rights_link"] is True
    assert (
        set(retention["module_rules"])
        == set(rights["module_coverage"])
        == load_catalog_modules()
    )
    assert set(retention["jobs"]) == REQUIRED_JOBS
    assert set(retention["audit_events"]) == EXPECTED_AUDIT_EVENTS


def test_each_job_declares_evidence_and_schedule() -> None:
    retention = load_retention()

    for job_name, job in retention["jobs"].items():
        assert job["schedule"] in {"hourly", "daily"}
        assert job["purpose"]
        assert "job_run_id" in job["required_evidence"], job_name
        assert "audit_event_id" in job["required_evidence"], job_name
        assert isinstance(job["dry_run_required"], bool)


def test_module_rules_have_action_legal_hold_and_known_job() -> None:
    retention = load_retention()

    for module, rule in retention["module_rules"].items():
        assert rule["default_action"], module
        assert rule["legal_hold"], module
        assert rule["minimum_job"] in REQUIRED_JOBS, module
        assert rule["evidence_domain"].endswith("_privacy"), module
        if module in CRITICAL_MODULES:
            assert rule["minimum_job"] in {
                "anonymization_worker_hourly",
                "deletion_worker_daily",
                "legal_hold_reconciliation_daily",
            }


def test_destructive_actions_are_blocked_without_legal_review() -> None:
    retention = load_retention()
    forbidden = set(retention["safety_rules"]["forbidden_without_legal_review"])

    assert (
        retention["safety_rules"]["requires_dry_run_before_first_production_deletion"]
        is True
    )
    assert retention["safety_rules"]["requires_immutable_audit"] is True
    assert {
        "delete_ledger",
        "delete_tax_record",
        "delete_medical_record",
        "delete_labor_record",
    }.issubset(forbidden)
