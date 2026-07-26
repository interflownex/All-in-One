import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RIGHTS = {
    "acesso",
    "correcao",
    "portabilidade",
    "anonimizacao",
    "revogacao de consentimento",
    "exclusao quando legalmente permitida",
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


def load_matrix() -> dict:
    return json.loads(
        (ROOT / "config" / "compliance" / "data_classification.json").read_text(
            encoding="utf-8"
        )
    )


def load_rights() -> dict:
    return json.loads(
        (ROOT / "config" / "compliance" / "data_subject_rights.json").read_text(
            encoding="utf-8"
        )
    )


def test_data_subject_rights_match_lgpd_policy_and_catalog_modules() -> None:
    rights = load_rights()
    compliance = load_matrix()

    assert (
        set(rights["rights"])
        == set(compliance["policy"]["subject_rights"])
        == REQUIRED_RIGHTS
    )
    assert set(rights["module_coverage"]) == load_catalog_modules()
    assert (
        rights["guardrails"]["audit_event"]
        == "compliance.data_subject_request.processed"
    )


def test_each_right_has_sla_workflow_and_evidence() -> None:
    rights = load_rights()

    for right_name, right in rights["rights"].items():
        assert 1 <= right["sla_days"] <= 15, f"{right_name} tem SLA invalido"
        assert "validar_identidade" in right["workflow"]
        assert "registrar_auditoria" in right["workflow"]
        assert "identity_check" in right["evidence"]
        assert "audit_event_id" in right["evidence"]
        assert right["consumer_label"]
        assert len(right["allowed_output"]) >= 20


def test_module_coverage_declares_safe_handling_for_critical_data() -> None:
    rights = load_rights()

    for module, entry in rights["module_coverage"].items():
        assert set(entry["rights"]).issubset(REQUIRED_RIGHTS), (
            f"{module} declara direito desconhecido"
        )
        assert "acesso" in entry["rights"], f"{module} precisa permitir acesso"
        assert entry["special_handling"], (
            f"{module} precisa declarar tratamento especial"
        )
        if module in CRITICAL_MODULES:
            assert entry["risk"] == "critical"
            assert REQUIRED_RIGHTS.issubset(entry["rights"])


def test_sensitive_exports_are_blocked_by_default() -> None:
    rights = load_rights()
    blocked = " ".join(rights["guardrails"]["never_export"]).casefold()

    for token in [
        "segredos reais",
        "chaves privadas",
        "dados de cartao",
        "biometria bruta",
    ]:
        assert token in blocked
    assert {"compliance_officer", "data_protection_officer"}.issubset(
        set(rights["guardrails"]["sensitive_review_roles"])
    )
