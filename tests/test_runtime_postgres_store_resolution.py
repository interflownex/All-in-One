from __future__ import annotations

import types

import pytest

from modules.shared import runtime
from modules.shared.riders_postgres_store import RidersPostgresStore


class DummyConnection:
    def execute(self, *args, **kwargs):  # pragma: no cover - nao deve ser chamado nestes testes
        raise AssertionError("Teste de resolucao nao deve executar queries.")


@pytest.mark.parametrize("module_name", sorted(runtime.MODULE_ENTITIES))
def test_store_for_resolves_typed_postgres_store_for_all_known_modules(
    module_name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN", "postgresql://test")
    monkeypatch.setattr("psycopg.connect", lambda *args, **kwargs: DummyConnection())

    store = runtime._store_for(module_name)

    assert store.module == module_name
    assert "postgres" in store.backend
    assert "typed_store" in store.backend or store.backend == "postgres_erp_typed_store"


def test_store_for_rejects_fallback_to_generic_postgres_for_known_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module_name = "identity"
    module_path = ".identity_postgres_store"
    monkeypatch.setenv("ALL_IN_ONE_IDENTITY_POSTGRES_DSN", "postgresql://test")

    original_import = runtime.importlib.import_module

    def fake_import(name: str, package: str | None = None):
        if name == module_path:
            raise ImportError("simulated missing typed store")
        return original_import(name, package)

    monkeypatch.setattr(runtime.importlib, "import_module", fake_import)

    with pytest.raises(RuntimeError, match="Store PostgreSQL tipado obrigatorio ausente"):
        runtime._store_for(module_name)


def test_store_for_keeps_generic_fallback_outside_typed_matrix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALL_IN_ONE_EXPERIMENTAL_POSTGRES_DSN", "postgresql://test")
    monkeypatch.setattr("psycopg.connect", lambda *args, **kwargs: DummyConnection())
    monkeypatch.setattr(
        runtime.importlib,
        "import_module",
        lambda *args, **kwargs: (_ for _ in ()).throw(ImportError("missing optional module")),
    )

    store = runtime._store_for("experimental")

    assert store.__class__.__name__ == "BasePostgresStore"


def test_get_erp_store_uses_memory_store_without_dsn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ALL_IN_ONE_ERP_POSTGRES_DSN", raising=False)
    monkeypatch.setattr(runtime, "_ERP_FALLBACK_STORE", None)

    store = runtime.get_erp_store()

    assert store.__class__.__name__ == "ErpMemoryStore"


def test_riders_postgres_store_uses_delivery_schema_tables() -> None:
    assert RidersPostgresStore.tables == {
        "rider_profiles": "delivery.rider_profiles",
        "rider_documents": "delivery.rider_documents",
        "vehicles": "delivery.vehicles",
        "rider_reviews": "delivery.rider_reviews",
    }


def test_get_config_skips_gcloud_fallback_when_google_mode_is_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_INTEGRATIONS_ENABLED", "false")
    monkeypatch.setenv("GOOGLE_CLOUD_ENABLED", "false")

    called = False

    def fake_run(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("gcloud nao deve ser chamado em modo local-first")

    monkeypatch.setattr(runtime.subprocess, "run", fake_run)

    assert runtime.get_config("ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY", "local-default") == "local-default"
    assert called is False
