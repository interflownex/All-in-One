import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "integrations" / "provider_matrix.json"
ENVIRONMENT_PROFILES_PATH = (
    ROOT / "config" / "integrations" / "environment_profiles.json"
)
CATALOG_PATH = ROOT / "config" / "module_catalog.json"

REQUIRED_KEYS = {
    "key",
    "modules",
    "capability",
    "stage",
    "sandbox_adapter",
    "primary_candidates",
    "fallback_candidates",
    "required_env",
    "events",
    "sensitive_data",
    "zero_cost_entry",
    "go_live_gate",
}
CRITICAL_MODULES = {
    "identity",
    "business",
    "finance",
    "marketplace",
    "delivery",
    "riders",
    "services",
    "mobility",
    "jobs",
    "erp",
    "stock",
    "health",
    "document",
    "api_hub",
    "permissions",
}
SECRET_WORDS = ("secret", "token", "password", "senha", "api_key", "client_secret")
REQUIRED_ENVIRONMENTS = ("sandbox", "homologacao", "producao")


def test_integration_provider_matrix_is_complete_and_secret_safe() -> None:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog_modules = {module["slug"] for module in catalog["modules"]}

    assert matrix["schema_version"] == 1
    assert matrix["strategy"] == "sandbox_first_with_provider_ports"
    assert matrix["integrations"]

    covered_modules: set[str] = set()
    covered_events: set[str] = set()
    integration_keys: set[str] = set()

    for integration in matrix["integrations"]:
        assert REQUIRED_KEYS <= set(integration), integration["key"]
        assert integration["key"] not in integration_keys
        integration_keys.add(integration["key"])
        assert integration["stage"] in {
            "planned",
            "sandbox_required",
            "provider_discovery",
            "partially_implemented",
        }
        assert integration["modules"], integration["key"]
        assert set(integration["modules"]) <= catalog_modules
        assert integration["sandbox_adapter"].startswith("local_") or integration[
            "sandbox_adapter"
        ].endswith("_simulator")
        assert integration["primary_candidates"], integration["key"]
        assert integration["fallback_candidates"], integration["key"]
        assert integration["required_env"], integration["key"]
        assert all(name.upper() == name for name in integration["required_env"])
        assert integration["events"], integration["key"]
        assert integration["sensitive_data"], integration["key"]
        assert "secret" not in integration.get("zero_cost_entry", "").casefold()

        for candidate_list in ("primary_candidates", "fallback_candidates"):
            for candidate in integration[candidate_list]:
                lowered = candidate.casefold()
                assert not any(f"{word}=" in lowered for word in SECRET_WORDS)

        covered_modules.update(integration["modules"])
        covered_events.update(integration["events"])

    assert CRITICAL_MODULES <= covered_modules
    assert {
        "identity.user.verified",
        "payment.escrow.created",
        "marketplace.order.paid",
        "delivery.completed",
        "mobility.ride.completed",
        "jobs.resume.ctps_imported",
        "health.appointment.completed",
    } <= covered_events


def test_integration_environment_profiles_gate_promotion() -> None:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    profiles = json.loads(ENVIRONMENT_PROFILES_PATH.read_text(encoding="utf-8"))

    assert profiles["schema_version"] == 1
    assert profiles["source_matrix"] == "config/integrations/provider_matrix.json"
    assert profiles["active_environment_variable"] == "ALL_IN_ONE_INTEGRATION_ENV"
    assert profiles["default_environment"] == "sandbox"
    assert profiles["promotion_order"] == list(REQUIRED_ENVIRONMENTS)
    assert tuple(profiles["profiles"]) == REQUIRED_ENVIRONMENTS

    sandbox = profiles["profiles"]["sandbox"]
    homologacao = profiles["profiles"]["homologacao"]
    producao = profiles["profiles"]["producao"]

    assert sandbox["allows_external_calls"] is False
    assert sandbox["allows_real_secret_values"] is False
    assert sandbox["requires_provider_contract"] is False
    assert "sem_chamada_externa" in sandbox["required_evidence"]

    for environment in (homologacao, producao):
        assert environment["allows_external_calls"] is True
        assert environment["allows_real_secret_values"] is True
        assert environment["requires_provider_contract"] is True
        assert environment["requires_human_approval"] is True
        assert "Google Secret Manager" in environment["secret_storage"]
        serialized = json.dumps(environment, ensure_ascii=False).casefold()
        assert not any(f"{word}=" in serialized for word in SECRET_WORDS)

    assert "teste_de_contrato_por_provider" in homologacao["required_evidence"]
    assert "go_live_gate_da_matriz_atendido" in producao["required_evidence"]
    assert "partially_implemented" in producao["required_matrix_stage"]

    matrix_stages = {integration["stage"] for integration in matrix["integrations"]}
    for environment_name in REQUIRED_ENVIRONMENTS:
        allowed_stages = set(
            profiles["profiles"][environment_name]["required_matrix_stage"]
        )
        assert allowed_stages <= matrix_stages | {
            "planned",
            "sandbox_required",
            "provider_discovery",
            "partially_implemented",
        }
