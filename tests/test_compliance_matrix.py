import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_RISK_LEVELS = {"critical", "high", "medium", "low"}
REQUIRED_FIELDS = {
    "risk_level",
    "data_domains",
    "sensitive_categories",
    "legal_basis",
    "retention_policy",
    "production_gate",
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


def test_compliance_matrix_covers_all_catalog_modules() -> None:
    matrix = load_matrix()

    assert set(matrix["modules"]) == load_catalog_modules()
    assert matrix["policy"]["subject_rights"]
    assert "segredos reais" in matrix["policy"]["forbidden_repository_data"]


def test_compliance_matrix_has_required_fields_and_valid_risk() -> None:
    matrix = load_matrix()

    for module, entry in matrix["modules"].items():
        missing = REQUIRED_FIELDS - set(entry)
        assert not missing, f"{module} sem campos obrigatorios: {sorted(missing)}"
        assert entry["risk_level"] in ALLOWED_RISK_LEVELS
        for field in [
            "data_domains",
            "sensitive_categories",
            "legal_basis",
            "production_gate",
        ]:
            assert entry[field], f"{module}.{field} nao pode ficar vazio"
        assert len(entry["retention_policy"]) >= 20


def test_critical_modules_require_stronger_production_gates() -> None:
    matrix = load_matrix()

    for module in CRITICAL_MODULES:
        entry = matrix["modules"][module]
        assert entry["risk_level"] == "critical"
        gates = " ".join(entry["production_gate"]).casefold()
        assert any(
            token in gates for token in ["dpia", "kms", "vault", "cofre", "hash_only"]
        )
