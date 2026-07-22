import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "config" / "operations" / "load_test_plan.json"

REQUIRED_SCENARIOS = {
    "api_hub_gateway_catalog",
    "identity_auth_mfa",
    "finance_escrow_ledger",
    "jobs_resume_access",
    "retention_worker_batch",
}


def load_plan() -> dict:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def test_load_test_plan_defines_safe_execution_policy_and_thresholds() -> None:
    plan = load_plan()

    assert plan["version"] == "2026-07-15"
    assert plan["scope"] == "load_and_performance_testing"
    assert plan["default_environment"] == "homologacao"
    assert plan["execution_policy"]["production_requires_approval"] is True
    assert plan["execution_policy"]["no_real_payment_capture"] is True
    assert plan["execution_policy"]["no_sensitive_payload_capture"] is True
    assert plan["execution_policy"]["use_synthetic_or_sanitized_data"] is True
    assert plan["global_thresholds"]["http_error_rate_max_percent"] <= 1.0
    assert plan["global_thresholds"]["p95_latency_ms_max"] <= 800
    assert plan["global_thresholds"]["duration_minutes_min"] >= 15


def test_load_test_plan_covers_critical_journeys_with_evidence() -> None:
    plan = load_plan()

    assert set(plan["scenarios"]) == REQUIRED_SCENARIOS
    critical = {
        name
        for name, scenario in plan["scenarios"].items()
        if scenario["priority"] == "critical"
    }
    assert {
        "api_hub_gateway_catalog",
        "identity_auth_mfa",
        "finance_escrow_ledger",
    } <= critical

    for name, scenario in plan["scenarios"].items():
        assert scenario["entrypoint"], name
        assert scenario["journey"], name
        assert scenario["duration_minutes"] >= 15, name
        assert scenario["covered_modules"], name
        assert scenario["required_metrics"], name
        assert scenario["success_criteria"], name
        assert "run_id" in scenario["evidence"], name
        assert "commit_sha" in scenario["evidence"], name
        assert "payload" not in " ".join(scenario["evidence"]).casefold(), name
        assert not any("raw" in item.casefold() for item in scenario["evidence"]), name


def test_load_test_plan_blocks_promotion_without_homologation_evidence() -> None:
    plan = load_plan()

    gate = " ".join(plan["promotion_gate"]).casefold()
    assert "homologacao" in gate
    assert "evidencias_sem_payload_sensivel" in plan["promotion_gate"]
    assert "aprovacao_humana_para_teste_em_producao" in plan["promotion_gate"]
    assert "tests/test_load_test_plan.py" in plan["tooling"]["local_contract_tests"]
    assert (
        "python3 scripts/validate_repository.py"
        in plan["tooling"]["local_contract_tests"]
    )
