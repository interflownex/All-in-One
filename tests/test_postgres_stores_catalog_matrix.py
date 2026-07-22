from __future__ import annotations

import importlib
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from all_in_one_test_support.runtime_event_generation import (  # noqa: E402
    generate_payload,
    get_primary_resource,
    load_module_catalog,
)
from modules.shared.business_postgres_store import BusinessPostgresStore  # noqa: E402
from modules.shared.domain_rules import event_for_create, rule_for  # noqa: E402
from modules.shared.identity_postgres_store import IdentityPostgresStore  # noqa: E402


DEFAULT_DSN = os.environ.get(
    "ALL_IN_ONE_POSTGRES_MATRIX_DSN",
    "postgresql://all_in_one:local-development-only@localhost:5432/all_in_one?connect_timeout=3",
)

PRIORITY_MODULES = {
    "identity",
    "business",
    "api_hub",
    "finance",
    "marketplace",
    "delivery",
    "services",
    "mobility",
    "jobs",
}

CATALOG_MODULES = [module["slug"] for module in load_module_catalog()["modules"] if module["slug"] not in PRIORITY_MODULES]


def _dsn_for(module_name: str) -> str:
    dsn = os.environ.get(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN") or DEFAULT_DSN
    if "connect_timeout" in dsn:
        return dsn
    return f"{dsn}&connect_timeout=3" if "?" in dsn else f"{dsn}?connect_timeout=3"


def _unique_phone_e164() -> str:
    return f"+55{uuid4().int % 10**11:011d}"


def _seed_dependencies(dsn: str) -> dict[str, str]:
    identity_store = IdentityPostgresStore(dsn=dsn)
    seed_user_id = str(uuid4())
    seed_user = identity_store.create(
        resource_type="users",
        user_id=seed_user_id,
        entity_id=None,
        status="active",
        payload={
            "id": seed_user_id,
            "full_name": f"Seed User {uuid4().hex[:6]}",
            "cpf_document": f"{uuid4().hex[:11]}",
            "birth_date": "1990-01-01",
            "email": f"seed_{uuid4().hex[:8]}@test.com",
            "phone_e164": _unique_phone_e164(),
            "password_hash": "seed-password-hash",
            "face_hash": f"seed-face-{uuid4().hex[:8]}",
            "liveness_score": 0.99,
            "terms_accepted_at": datetime.now(UTC).isoformat(),
            "lgpd_consent_at": datetime.now(UTC).isoformat(),
        },
        actor=seed_user_id,
        unique_fields=(),
        event="identity.user.created",
        idempotency_key=f"seed-user-{uuid4()}",
    )

    business_store = BusinessPostgresStore(dsn=dsn)
    seed_company = business_store.create(
        resource_type="companies",
        user_id=seed_user["id"],
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid4().hex[:14]}",
            "root_cnpj": f"{uuid4().hex[:14]}",
            "legal_name": f"Seed Company {uuid4().hex[:6]} LTDA",
            "trade_name": f"Seed Company {uuid4().hex[:6]}",
            "cnae": "6201500",
            "state_registration": "ISENTO",
            "municipal_registration": "ISENTO",
        },
        actor=seed_user["id"],
        unique_fields=(),
        event="business.company.created",
        idempotency_key=f"seed-company-{uuid4()}",
    )
    return {"user_id": seed_user["id"], "company_id": seed_company["id"]}


def _store_for(module_name: str, dsn: str) -> Any:
    module = importlib.import_module(f"modules.shared.{module_name}_postgres_store")
    class_name = f"{module_name.title().replace('_', '')}PostgresStore"
    return getattr(module, class_name)(dsn=dsn)


def _build_payload(module_name: str, seeds: dict[str, str], rule: Any) -> dict[str, Any]:
    payload = generate_payload(rule, seeds["user_id"])
    if module_name in {"stock", "hr"}:
        payload["company_id"] = seeds["company_id"]
    if module_name == "property":
        payload.setdefault("property_type", "apartment")
    return payload


@pytest.mark.parametrize("module_name", CATALOG_MODULES)
def test_postgres_store_catalog_matrix(module_name: str) -> None:
    dsn = _dsn_for(module_name)
    try:
        seeds = _seed_dependencies(dsn)
        primary_resource = get_primary_resource(module_name)
        rule = rule_for(module_name, primary_resource)
        store = _store_for(module_name, dsn)
    except Exception as exc:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {exc}")

    payload = _build_payload(module_name, seeds, rule)
    actor_id = seeds["user_id"]
    entity_id = seeds["company_id"]
    created = store.create(
        primary_resource,
        seeds["user_id"],
        entity_id,
        rule.initial_status,
        payload,
        actor_id,
        rule.unique_fields,
        event_for_create(module_name, primary_resource),
        str(uuid4()),
    )

    fetched = store.get(primary_resource, created["id"])
    listed = store.list(primary_resource, seeds["user_id"])
    assert fetched is not None
    assert any(item["id"] == created["id"] for item in listed)

    table_columns = store._table_columns(primary_resource) if hasattr(store, "_table_columns") else set()
    if "idempotency_key" in table_columns:
        assert created["idempotency_key"] is not None
        duplicated = store.create(
            primary_resource,
            seeds["user_id"],
            entity_id,
            rule.initial_status,
            payload,
            actor_id,
            rule.unique_fields,
            event_for_create(module_name, primary_resource),
            created["idempotency_key"],
        )
        assert duplicated["id"] == created["id"]

    update_payload = dict(created["payload"])
    update_payload["_matrix_marker"] = module_name
    updated = store.update(created, update_payload, rule.initial_status, actor_id, "update", None)
    assert updated["id"] == created["id"]
    assert updated["payload"]["_matrix_marker"] == module_name

    if primary_resource in getattr(store, "soft_deletable", frozenset()):
        store.soft_delete(item=fetched, actor=actor_id)
        assert store.get(primary_resource, created["id"]) is None

    assert store.audit_log()
    assert store.outbox()
