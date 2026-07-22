from pathlib import Path

from modules.dynamic_forms.main import app

ROOT = Path(__file__).resolve().parents[1]


def test_openapi_expoe_ciclo_governado_com_modelos_de_request() -> None:
    schema = app.openapi()
    expected = {
        "/catalog",
        "/catalog/bindings",
        "/definitions",
        "/versions/{version_id}/blueprint",
        "/versions/{version_id}/homologations",
        "/homologations/{homologation_id}/review",
        "/versions/{version_id}/publish",
        "/forms/{definition_id}/submissions",
    }
    assert expected.issubset(schema["paths"])
    for path in expected - {"/catalog", "/catalog/bindings"}:
        assert any(
            operation.get("requestBody") for operation in schema["paths"][path].values()
        )


def test_store_aplica_tenant_lock_idempotencia_evento_e_persistencia_normalizada() -> (
    None
):
    source = (ROOT / "modules/shared/dynamic_forms_postgres_store.py").read_text(
        encoding="utf-8"
    )
    assert source.count("tenant_id") >= 30
    assert "FOR UPDATE" in source
    assert "idempotency_key" in source
    assert "forms.form_submission_values" in source
    assert "INSERT INTO audit.domain_events" in source
    assert "build_event_envelope" in source
    assert "forms.form_billing_events" in source


def test_api_hub_e_compose_publicam_servico_sem_segredo_versionado() -> None:
    hub = (ROOT / "modules/api_hub/main.py").read_text(encoding="utf-8")
    compose = (ROOT / "infra/docker/docker-compose.yml").read_text(encoding="utf-8")
    assert '"dynamic_forms"' in hub
    assert "dynamic_forms:" in compose
    assert "ALL_IN_ONE_DYNAMIC_FORMS_POSTGRES_DSN" in compose
    assert "DYNAMIC_FORMS_SERVICE_URL" in compose
