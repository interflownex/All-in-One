from __future__ import annotations

import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.shared.api_hub_postgres_store import ApiHubPostgresStore
from modules.shared.business_postgres_store import BusinessPostgresStore
from modules.shared.delivery_postgres_store import DeliveryPostgresStore
from modules.shared.finance_postgres_store import FinancePostgresStore
from modules.shared.identity_postgres_store import IdentityPostgresStore
from modules.shared.jobs_postgres_store import JobsPostgresStore
from modules.shared.marketplace_postgres_store import MarketplacePostgresStore
from modules.shared.mobility_postgres_store import MobilityPostgresStore
from modules.shared.outbox_dispatcher import SAFE_PAYLOAD_FIELDS, publication_message
from modules.shared.services_postgres_store import ServicesPostgresStore

DEFAULT_DSN = os.environ.get(
    "ALL_IN_ONE_POSTGRES_MATRIX_DSN",
    "postgresql://all_in_one:local-development-only@localhost:5432/all_in_one?connect_timeout=3",
)


MODULES_CONFIG = {
    "identity": {
        "class": IdentityPostgresStore,
        "resource": "users",
        "status": "active",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "finance": {
        "class": FinancePostgresStore,
        "resource": "valley_gold_ledger_entries",
        "status": "posted",
        "supports_update": False,
        "uses_seed_user_as_actor": True,
    },
    "business": {
        "class": BusinessPostgresStore,
        "resource": "companies",
        "status": "active",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "api_hub": {
        "class": ApiHubPostgresStore,
        "resource": "api_clients",
        "status": "active",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "marketplace": {
        "class": MarketplacePostgresStore,
        "resource": "stores",
        "status": "pending_validation",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "delivery": {
        "class": DeliveryPostgresStore,
        "resource": "delivery_requests",
        "status": "created",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "services": {
        "class": ServicesPostgresStore,
        "resource": "providers",
        "status": "pending_review",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "mobility": {
        "class": MobilityPostgresStore,
        "resource": "rides",
        "status": "requested",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
    "jobs": {
        "class": JobsPostgresStore,
        "resource": "resumes",
        "status": "active",
        "supports_update": True,
        "uses_seed_user_as_actor": True,
    },
}

EVENTS = {
    "identity": "identity.user.created",
    "finance": "valley.gold.ledger.posted",
    "business": "business.company.created",
    "api_hub": "api_hub.api_client.created",
    "marketplace": "marketplace.store.created",
    "delivery": "delivery.delivery_request.created",
    "services": "services.provider.created",
    "mobility": "mobility.ride.requested",
    "jobs": "jobs.resume.created",
}


def _dsn_for(module_name: str) -> str:
    dsn = os.environ.get(f"ALL_IN_ONE_{module_name.upper()}_POSTGRES_DSN") or DEFAULT_DSN
    if "connect_timeout" in dsn:
        return dsn
    return f"{dsn}&connect_timeout=3" if "?" in dsn else f"{dsn}?connect_timeout=3"


def _store_for(store_class: type[Any], dsn: str) -> Any:
    return store_class(dsn=dsn)


def _seed_dependencies(dsn: str) -> dict[str, str]:
    identity_store = IdentityPostgresStore(dsn=dsn)
    seed_user_id = str(uuid.uuid4())
    seed_user = identity_store.create(
        resource_type="users",
        user_id=seed_user_id,
        entity_id=None,
        status="active",
        payload={
            "id": seed_user_id,
            "full_name": f"Seed User {uuid.uuid4().hex[:6]}",
            "cpf_document": f"{uuid.uuid4().hex[:11]}",
            "birth_date": "1990-01-01",
            "email": f"seed_{uuid.uuid4().hex[:8]}@test.com",
            "phone_e164": "+5511999999999",
            "password_hash": "seed-password-hash",
            "face_hash": f"seed-face-{uuid.uuid4().hex[:8]}",
            "liveness_score": 0.99,
            "terms_accepted_at": datetime.now(UTC).isoformat(),
            "lgpd_consent_at": datetime.now(UTC).isoformat(),
        },
        actor=seed_user_id,
        unique_fields=(),
        event=EVENTS["identity"],
        idempotency_key=f"seed-user-{uuid.uuid4()}",
    )

    business_store = BusinessPostgresStore(dsn=dsn)
    seed_company = business_store.create(
        resource_type="companies",
        user_id=seed_user["id"],
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid.uuid4().hex[:14]}",
            "root_cnpj": f"{uuid.uuid4().hex[:14]}",
            "legal_name": f"Seed Company {uuid.uuid4().hex[:6]} LTDA",
            "trade_name": f"Seed Company {uuid.uuid4().hex[:6]}",
            "cnae": "6201500",
            "state_registration": "ISENTO",
            "municipal_registration": "ISENTO",
        },
        actor=seed_user["id"],
        unique_fields=(),
        event=EVENTS["business"],
        idempotency_key=f"seed-company-{uuid.uuid4()}",
    )
    return {"user_id": seed_user["id"], "company_id": seed_company["id"]}


def _create_payload(module_name: str, seeds: dict[str, str]) -> dict[str, Any]:
    suffix = uuid.uuid4().hex[:8]
    if module_name == "identity":
        user_id = str(uuid.uuid4())
        return {
            "id": user_id,
            "full_name": f"Matrix Tester {suffix}",
            "cpf_document": f"{uuid.uuid4().hex[:11]}",
            "birth_date": "1990-01-01",
            "email": f"matrix_{suffix}@test.com",
            "phone_e164": "+5511999999999",
            "password_hash": f"hash-{suffix}",
            "face_hash": f"face-{suffix}",
            "liveness_score": 0.99,
            "terms_accepted_at": datetime.now(UTC).isoformat(),
            "lgpd_consent_at": datetime.now(UTC).isoformat(),
        }
    if module_name == "finance":
        return {
            "merchant_business_id": seeds["company_id"],
            "entry_type": "purchase_credit",
            "amount_gold_delta": 1000,
            "reference_type": "gold_purchase",
            "reference_id": str(uuid.uuid4()),
        }
    if module_name == "business":
        return {
            "cnpj": f"{uuid.uuid4().hex[:14]}",
            "root_cnpj": f"{uuid.uuid4().hex[:14]}",
            "legal_name": f"Matrix Corp {suffix} LTDA",
            "trade_name": f"Matrix Corp {suffix}",
            "cnae": "6201500",
            "state_registration": "ISENTO",
            "municipal_registration": "ISENTO",
        }
    if module_name == "api_hub":
        return {
            "client_name": f"Matrix App {suffix}",
            "client_id_hash": f"client-{suffix}",
            "secret_reference": f"secret/matrix/{suffix}",
            "scopes": ["catalog:read", "orders:write"],
        }
    if module_name == "marketplace":
        return {
            "company_id": seeds["company_id"],
            "name": f"Matrix Store {suffix}",
        }
    if module_name == "delivery":
        return {
            "service_type": "delivery",
            "origin": {
                "address": "Rua Teste 1",
                "lat": -23.5505,
                "lng": -46.6333,
            },
            "destination": {
                "address": "Rua Teste 2",
                "lat": -23.561,
                "lng": -46.644,
            },
            "distance_km": 1.5,
            "weight_kg": 2.0,
            "volume_m3": 0.1,
            "quoted_brl": "25.00",
            "insurance_required": False,
        }
    if module_name == "services":
        return {
            "category": f"maintenance-{suffix}",
        }
    if module_name == "mobility":
        return {
            "origin": {
                "address": "Av. Paulista, 1000",
                "lat": -23.561,
                "lng": -46.656,
            },
            "destination": {
                "address": "Rua Augusta, 200",
                "lat": -23.553,
                "lng": -46.643,
            },
            "fare_brl": "18.50",
            "vehicle_type": "car",
        }
    if module_name == "jobs":
        return {
            "headline": f"Neo Matrix {suffix}",
            "professional_summary": "Resumo profissional de teste.",
            "skills": ["python", "pytest"],
            "education": ["BSc"],
            "recruiter_visibility": "private",
        }
    raise ValueError(f"Modulo sem payload de teste: {module_name}")


def _update_payload(module_name: str, created: dict[str, Any], seeds: dict[str, str]) -> dict[str, Any]:
    suffix = uuid.uuid4().hex[:6]
    if module_name == "identity":
        return {
            "full_name": f"{created['payload']['full_name']} Atualizado {suffix}",
        }
    if module_name == "business":
        return {
            "legal_name": f"{created['payload']['legal_name']} Atualizada",
            "trade_name": f"{created['payload']['trade_name']} Atualizada",
        }
    if module_name == "api_hub":
        return {
            "client_name": f"{created['payload']['client_name']} v2",
            "scopes": ["catalog:read"],
        }
    if module_name == "marketplace":
        return {
            "name": f"{created['payload']['name']} Atualizada",
            "published_at": datetime.now(UTC).isoformat(),
        }
    if module_name == "delivery":
        return {
            "assigned_rider_user_id": seeds["user_id"],
        }
    if module_name == "services":
        return {
            "category": f"{created['payload']['category']}-v2",
        }
    if module_name == "mobility":
        return {
            "driver_user_id": seeds["user_id"],
        }
    if module_name == "jobs":
        return {
            "headline": f"{created['payload']['headline']} Senior",
            "professional_summary": "Resumo atualizado.",
            "skills": ["python", "pytest", "sql"],
            "education": ["BSc"],
            "recruiter_visibility": "business_recruiters",
        }
    raise ValueError(f"Modulo sem payload de update: {module_name}")


def _create_resource(module_name: str, seeds: dict[str, str]) -> tuple[Any, dict[str, Any], str]:
    config = MODULES_CONFIG[module_name]
    store = _store_for(config["class"], _dsn_for(module_name))
    payload = _create_payload(module_name, seeds)
    actor_id = seeds["user_id"] if config["uses_seed_user_as_actor"] else str(uuid.uuid4())
    entity_id = seeds["company_id"] if module_name in {"finance", "api_hub", "marketplace", "business"} else None
    created = store.create(
        resource_type=config["resource"],
        user_id=seeds["user_id"],
        entity_id=entity_id,
        status=config["status"],
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=EVENTS[module_name],
        idempotency_key=f"{module_name}-{uuid.uuid4()}",
    )
    return store, created, actor_id


@pytest.mark.parametrize("module_name", list(MODULES_CONFIG.keys()))
def test_postgres_store_matrix_initialization(module_name: str) -> None:
    """
    Testa a inicialização, CRUD básico, update e soft delete para os modulos
    prioritários definidos no EXECUTION_PLAN.md (Fase 2).
    """
    dsn = _dsn_for(module_name)
    try:
        seeds = _seed_dependencies(dsn)
        store, created, actor_id = _create_resource(module_name, seeds)
    except Exception as exc:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {exc}")

    config = MODULES_CONFIG[module_name]
    resource_type = config["resource"]

    assert created is not None
    assert created["id"] is not None
    assert created["status"] == config["status"]
    if module_name == "identity":
        assert created["user_id"] == created["id"]
    else:
        assert created["user_id"] == seeds["user_id"]

    fetched = store.get(resource_type=resource_type, resource_id=created["id"])
    assert fetched is not None
    assert fetched["id"] == created["id"]

    listed = store.list(resource_type=resource_type, user_id=seeds["user_id"])
    assert len(listed) >= 1
    assert any(item["id"] == created["id"] for item in listed)

    if config["supports_update"]:
        update_payload = _update_payload(module_name, created, seeds)
        updated = store.update(
            created,
            update_payload,
            config["status"],
            actor_id,
            "update",
        )
        assert updated["id"] == created["id"]
        assert updated["status"] == config["status"]
        assert updated["payload"] == update_payload

        refetched = store.get(resource_type=resource_type, resource_id=created["id"])
        assert refetched is not None
        assert refetched["payload"] == update_payload

    if hasattr(store, "soft_deletable") and resource_type in getattr(store, "soft_deletable", frozenset()):
        store.soft_delete(item=fetched, actor=actor_id)
        deleted = store.get(resource_type=resource_type, resource_id=created["id"])
        assert deleted is None


@pytest.mark.parametrize("module_name", list(MODULES_CONFIG.keys()))
def test_store_idempotency_behavior(module_name: str) -> None:
    dsn = _dsn_for(module_name)
    try:
        seeds = _seed_dependencies(dsn)
        config = MODULES_CONFIG[module_name]
        store = _store_for(config["class"], dsn)
    except Exception as exc:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {exc}")

    payload = _create_payload(module_name, seeds)
    actor_id = seeds["user_id"] if config["uses_seed_user_as_actor"] else str(uuid.uuid4())
    entity_id = seeds["company_id"] if module_name in {"finance", "api_hub", "marketplace", "business"} else None
    idempotency_key = str(uuid.uuid4())

    created_1 = store.create(
        resource_type=config["resource"],
        user_id=seeds["user_id"],
        entity_id=entity_id,
        status=config["status"],
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=EVENTS[module_name],
        idempotency_key=idempotency_key,
    )

    created_2 = store.create(
        resource_type=config["resource"],
        user_id=seeds["user_id"],
        entity_id=entity_id,
        status=config["status"],
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=EVENTS[module_name],
        idempotency_key=idempotency_key,
    )

    assert created_1["id"] == created_2["id"]


@pytest.mark.parametrize("module_name", list(MODULES_CONFIG.keys()))
def test_audit_outbox_integration(module_name: str) -> None:
    dsn = _dsn_for(module_name)
    try:
        seeds = _seed_dependencies(dsn)
        config = MODULES_CONFIG[module_name]
        store = _store_for(config["class"], dsn)
    except Exception as exc:
        pytest.skip(f"Banco de dados nao disponivel para {module_name}: {exc}")

    payload = _create_payload(module_name, seeds)
    actor_id = seeds["user_id"] if config["uses_seed_user_as_actor"] else str(uuid.uuid4())
    entity_id = seeds["company_id"] if module_name in {"finance", "api_hub", "marketplace", "business"} else None
    created = store.create(
        resource_type=config["resource"],
        user_id=seeds["user_id"],
        entity_id=entity_id,
        status=config["status"],
        payload=payload,
        actor=actor_id,
        unique_fields=(),
        event=EVENTS[module_name],
        idempotency_key=str(uuid.uuid4()),
    )

    if hasattr(store, "audit_log"):
        logs = store.audit_log()
        assert any(log["resource_id"] == created["id"] for log in logs)
        assert any(log["action"] == "create" for log in logs)

    if hasattr(store, "outbox"):
        events = store.outbox()
        assert events
        event = events[0]
        message = publication_message(event)
        expected_payload = {
            key: payload[key]
            for key in SAFE_PAYLOAD_FIELDS.get(event["aggregate_type"], frozenset())
            if key in payload
        }
        assert message["routing_key"] == event["routing_key"]
        assert message["aggregate_type"] == event["aggregate_type"]
        assert message["aggregate_id"] == str(event["aggregate_id"])
        assert message["event_id"] == str(event["id"])
        assert message["correlation_id"] == str(event["correlation_id"])
        assert message["occurred_at"] == event["created_at"].isoformat()
        assert message["payload"] == expected_payload
