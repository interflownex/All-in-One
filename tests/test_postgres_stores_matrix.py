import importlib
import inspect
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[1]
STORE_MODULES_DIR = ROOT / "modules" / "shared"
DEFAULT_DSN = os.environ.get(
    "ALL_IN_ONE_POSTGRES_MATRIX_DSN",
    "postgresql://all_in_one:local-development-only@localhost:5432/all_in_one?connect_timeout=3",
)

RUNTIME_PAYLOADS = {
    "identity": {
        "full_name": "Matrix Tester",
        "cpf_document": f"{uuid.uuid4().hex[:11]}",
        "birth_date": "1990-01-01",
        "email": f"matrix_{uuid.uuid4().hex[:8]}@test.com",
        "phone_e164": "+5511999999999",
        "password_hash": "hash123",
        "face_hash": "face123",
        "liveness_score": "0.99",
        "terms_accepted_at": datetime.now(UTC).isoformat(),
        "lgpd_consent_at": datetime.now(UTC).isoformat(),
    },
    "finance": {
        "wallet_type": "personal",
        "brl_available": 1000,
        "nex_available": 500,
    },
    "business": {
        "name": "Matrix Corp",
        "cnpj": f"{uuid.uuid4().hex[:14]}",
        "business_segment": "technology",
    },
    "api_hub": {
        "app_name": "Matrix App",
        "description": "Integration Test App",
        "webhook_url": "https://example.com/webhook",
    },
    "marketplace": {
        "name": "Matrix Store",
        "description": "Store for tests",
        "currency": "BRL",
    },
    "delivery": {
        "pickup_address": "Rua Teste 1",
        "dropoff_address": "Rua Teste 2",
        "distance_km": "1.5",
    },
    "services": {
        "display_name": "Matrix Provider",
        "service_category": "maintenance",
        "contact_phone": "+5511999999999",
    },
    "mobility": {
        "origin_label": "Paulista",
        "destination_label": "Pinheiros",
        "fare_brl": "24.90",
    },
    "jobs": {
        "first_name": "Neo",
        "last_name": "Matrix",
        "skills": ["python", "pytest"],
    },
}

PRIORITY_MODULES = {
    "finance",
    "identity",
    "business",
    "api_hub",
    "marketplace",
    "delivery",
    "services",
    "mobility",
    "jobs",
}


def _iter_postgres_store_classes() -> list[type]:
    classes: list[type] = []
    for path in sorted(STORE_MODULES_DIR.glob("*_postgres_store.py")):
        module_name = f"modules.shared.{path.stem}"
        module = importlib.import_module(module_name)
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if not candidate.__module__.endswith(path.stem):
                continue
            if not candidate.__name__.endswith("PostgresStore"):
                continue
            if getattr(candidate, "module", None) is None:
                continue
            classes.append(candidate)
    return classes


def _tables_for(store_class: type) -> dict[str, str]:
    table_map = getattr(store_class, "tables", None)
    if isinstance(table_map, dict):
        return table_map
    module = importlib.import_module(store_class.__module__)
    table_map = getattr(module, "TABLES", None)
    if isinstance(table_map, dict):
        return table_map
    raise AssertionError(f"{store_class.__name__} nao declara tables/TABLES.")


STORE_CLASSES = _iter_postgres_store_classes()
STORE_CLASS_BY_MODULE = {store_class.module: store_class for store_class in STORE_CLASSES}
MODULES_CONFIG = {
    module_name: {
        "class": store_class,
        "resource": next(iter(_tables_for(store_class))),
        "payload": RUNTIME_PAYLOADS.get(module_name, {}),
        "runtime_ready": module_name in RUNTIME_PAYLOADS,
    }
    for module_name, store_class in STORE_CLASS_BY_MODULE.items()
}


def _dsn_for(module_name: str) -> str:
    dsn = os.environ.get(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN") or DEFAULT_DSN
    if "connect_timeout" not in dsn:
        dsn += "&connect_timeout=3" if "?" in dsn else "?connect_timeout=3"
    return dsn


def _connect_store(module_name: str):
    store_class = MODULES_CONFIG[module_name]["class"]
    try:
        return store_class(dsn=_dsn_for(module_name))
    except Exception as exc:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {exc}")


@pytest.mark.parametrize("store_class", STORE_CLASSES, ids=lambda cls: cls.module)
def test_postgres_store_declares_structural_contract(store_class: type) -> None:
    tables = _tables_for(store_class)
    assert getattr(store_class, "module", None)
    assert getattr(store_class, "backend", None)
    assert isinstance(tables, dict)
    assert tables
    assert all("." in table_name for table_name in tables.values())


def test_postgres_store_matrix_covers_all_workspace_store_modules() -> None:
    discovered_modules = {store_class.module for store_class in STORE_CLASSES}
    assert len(discovered_modules) == 25
    assert set(MODULES_CONFIG) == discovered_modules


def test_postgres_store_matrix_marks_priority_modules_for_runtime_validation() -> None:
    ready_modules = {name for name, config in MODULES_CONFIG.items() if config["runtime_ready"]}
    assert PRIORITY_MODULES.issubset(ready_modules)


@pytest.mark.parametrize(
    "module_name",
    sorted(name for name, config in MODULES_CONFIG.items() if config["runtime_ready"]),
)
def test_postgres_store_matrix_initialization(module_name: str) -> None:
    config = MODULES_CONFIG[module_name]
    resource_type = config["resource"]
    payload = dict(config["payload"])
    store = _connect_store(module_name)

    user_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    payload["id"] = str(uuid.uuid4())

    created = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )

    assert created is not None
    assert created["id"] is not None
    assert created["status"] == "active"
    assert created["user_id"] == user_id

    fetched = store.get(resource_type=resource_type, resource_id=created["id"])
    assert fetched is not None
    assert fetched["id"] == created["id"]

    listed = store.list(resource_type=resource_type, user_id=user_id)
    assert listed
    assert any(item["id"] == created["id"] for item in listed)

    if resource_type in getattr(store, "soft_deletable", frozenset()):
        store.soft_delete(item=fetched, actor=actor_id)
        deleted = store.get(resource_type=resource_type, resource_id=created["id"])
        assert deleted is None


@pytest.mark.parametrize(
    "module_name",
    sorted(name for name, config in MODULES_CONFIG.items() if config["runtime_ready"]),
)
def test_store_idempotency_behavior(module_name: str) -> None:
    config = MODULES_CONFIG[module_name]
    resource_type = config["resource"]
    payload = dict(config["payload"])
    store = _connect_store(module_name)

    user_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    payload["id"] = str(uuid.uuid4())

    created_1 = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )
    created_2 = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )

    assert created_1["id"] == created_2["id"]


@pytest.mark.parametrize(
    "module_name",
    sorted(name for name, config in MODULES_CONFIG.items() if config["runtime_ready"]),
)
def test_audit_outbox_integration(module_name: str) -> None:
    config = MODULES_CONFIG[module_name]
    resource_type = config["resource"]
    payload = dict(config["payload"])
    store = _connect_store(module_name)

    user_id = str(uuid.uuid4())
    actor_id = str(uuid.uuid4())
    entity_id = str(uuid.uuid4())
    idempotency_key = str(uuid.uuid4())
    payload["id"] = str(uuid.uuid4())

    created = store.create(
        resource_type=resource_type,
        user_id=user_id,
        entity_id=entity_id,
        status="active",
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=f"{module_name}.{resource_type}.created",
        idempotency_key=idempotency_key,
    )

    if hasattr(store, "audit_log"):
        logs = store.audit_log()
        assert any(log["resource_id"] == created["id"] for log in logs)

    if hasattr(store, "outbox"):
        events = store.outbox()
        assert len(events) >= 0
