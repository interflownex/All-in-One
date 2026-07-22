import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "config" / "operations" / "backup_restore_plan.json"

REQUIRED_ASSETS = {
    "postgres_core",
    "mongodb_operational",
    "private_documents",
    "gitops_configuration",
}


def load_plan() -> dict:
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))


def test_backup_restore_plan_covers_critical_assets_without_sensitive_payloads() -> (
    None
):
    plan = load_plan()

    assert plan["version"] == "2026-07-15"
    assert plan["scope"] == "backup_restore_disaster_recovery"
    assert plan["notification_policy"]["include_sensitive_payload"] is False
    assert set(plan["assets"]) == REQUIRED_ASSETS

    for asset_name, asset in plan["assets"].items():
        assert asset["description"], asset_name
        assert asset["data_classification"] in {
            "critical",
            "sensitive",
            "operational",
        }, asset_name
        assert 0 <= asset["rpo_minutes"] <= 60, asset_name
        assert 1 <= asset["rto_minutes"] <= 240, asset_name
        assert asset["backup_frequency"], asset_name
        assert asset["restore_test_frequency"] in {"monthly", "quarterly"}, asset_name
        assert (
            "KMS" in asset["encryption"]
            or "no_secret_values_in_git" in asset["encryption"]
        ), asset_name
        assert asset["restore_validation"], asset_name
        assert "incident_ticket" in asset["evidence"], asset_name
        assert "payload" not in " ".join(asset["evidence"]).casefold(), asset_name
        assert asset["rollback"], asset_name


def test_backup_restore_plan_has_quarterly_dr_exercise_and_success_criteria() -> None:
    plan = load_plan()
    exercise = plan["dr_exercise"]

    assert exercise["cadence"] == "quarterly"
    assert set(exercise["minimum_scope"]) == REQUIRED_ASSETS
    assert "restaurar_em_ambiente_isolado" in exercise["required_steps"]
    assert "executar_validacoes_do_ativo" in exercise["required_steps"]
    assert "rpo_observado_menor_ou_igual_ao_contratado" in exercise["success_criteria"]
    assert "rto_observado_menor_ou_igual_ao_contratado" in exercise["success_criteria"]
    assert (
        "nenhum_segredo_ou_payload_sensivel_em_evidencia"
        in exercise["success_criteria"]
    )


def test_backup_restore_plan_references_existing_local_validators() -> None:
    plan = load_plan()
    validations = {
        item
        for asset in plan["assets"].values()
        for item in asset["restore_validation"]
        if item.endswith(".py")
        or item.endswith(".py --apply-migrations --repeat-migrations --write-checks")
    }

    assert (
        "scripts/validate_postgres_real_dsn.py --apply-migrations --repeat-migrations --write-checks"
        in validations
    )
    assert "scripts/validate_repository.py" in validations
    assert (ROOT / "scripts" / "validate_postgres_real_dsn.py").is_file()
    assert (ROOT / "scripts" / "validate_repository.py").is_file()
