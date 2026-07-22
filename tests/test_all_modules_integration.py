import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.shared.domain_rules import MODULE_ENTITIES
from modules.shared.runtime import create_module_app


# Desabilita o banco de dados em rede forçando fallback in-memory SQLite durante os testes de inicializacao a frio
@pytest.fixture(autouse=True)
def disable_postgres_dsn_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    for module_name in MODULE_ENTITIES:
        env_var = f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN"
        monkeypatch.delenv(env_var, raising=False)
    monkeypatch.setenv("ALL_IN_ONE_STORAGE_DIR", "")


@pytest.mark.parametrize("module_name", list(MODULE_ENTITIES.keys()))
def test_module_sanity_cold_start(module_name: str) -> None:
    """Verifica se o modulo instancia sem crash e garante rotas base."""
    app = create_module_app(module_name)
    client = TestClient(app)

    # Valida /health
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"
    assert health_response.json()["module"] == module_name
    assert (
        health_response.json()["storage"]
        in (
            "sqlite",
            "postgres_identity_typed_store",
            "postgres_business_typed_store",
            "postgres_hr_typed_store",
        )
        or "sqlite" in health_response.json()["storage"].lower()
        or "memory" in health_response.json()["storage"].lower()
        or "postgres" in health_response.json()["storage"].lower()
    )

    # Valida /version
    version_response = client.get("/version")
    assert version_response.status_code == 200
    assert version_response.json()["module"] == module_name

    # Valida /catalog
    catalog_response = client.get("/catalog")
    assert catalog_response.status_code == 200
    catalog = catalog_response.json()
    assert catalog["module"] == module_name
    assert "resources" in catalog
    assert "primary_resource" in catalog

    # Valida se os resources do endpoint conferem com o schema raiz
    schema_resources = set(MODULE_ENTITIES[module_name])
    endpoint_resources = set(catalog["resources"])
    assert endpoint_resources == schema_resources


@pytest.mark.parametrize("module_name", list(MODULE_ENTITIES.keys()))
def test_module_status_unauthorized(module_name: str) -> None:
    """Valida se o /status requer credencial Actor (Depends) garantindo seguranca basica de rotas."""
    app = create_module_app(module_name)
    client = TestClient(app)

    response = client.get("/status")
    # A rota requer actor_from_headers, se nao tem X-Actor-User-Id da 401 ou 422 dependendo da injecao (geralmente fastapi 422 sem header/roles, ou 403)
    assert response.status_code in (401, 403, 422)


def test_all_modules_instantiated_together() -> None:
    """Testa se conflitos de memoria ocorrem ao criar todas as apps no mesmo runtime."""
    apps = [create_module_app(m) for m in MODULE_ENTITIES]
    assert len(apps) == len(MODULE_ENTITIES)
    for app in apps:
        assert app.title.startswith("All-in-One")
