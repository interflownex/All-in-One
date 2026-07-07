from __future__ import annotations

import os
from uuid import UUID, uuid4

import psycopg
import pytest

from modules.shared.api_hub_postgres_store import ApiHubPostgresStore
from modules.shared.ai_core_postgres_store import AiCorePostgresStore
from modules.shared.bi_postgres_store import BiPostgresStore
from modules.shared.bpm_postgres_store import BpmPostgresStore
from modules.shared.business_postgres_store import BusinessPostgresStore
from modules.shared.crm_postgres_store import CrmPostgresStore
from modules.shared.delivery_postgres_store import DeliveryPostgresStore
from modules.shared.document_postgres_store import DocumentPostgresStore
from modules.shared.finance_postgres_store import FinancePostgresStore
from modules.shared.health_postgres_store import HealthPostgresStore
from modules.shared.identity_postgres_store import IdentityPostgresStore
from modules.shared.legal_postgres_store import LegalPostgresStore
from modules.shared.marketplace_postgres_store import MarketplacePostgresStore
from modules.shared.mobility_postgres_store import MobilityPostgresStore
from modules.shared.property_postgres_store import PropertyPostgresStore
from modules.shared.riders_postgres_store import RidersPostgresStore
from modules.shared.services_postgres_store import ServicesPostgresStore
from modules.shared.stock_postgres_store import StockPostgresStore
from modules.shared.tms_postgres_store import TmsPostgresStore
from modules.shared.vision_postgres_store import VisionPostgresStore
from modules.shared.wms_postgres_store import WmsPostgresStore


POSTGRES_DSN = os.getenv("ALL_IN_ONE_POSTGRES_MATRIX_DSN") or os.getenv("ALL_IN_ONE_BUSINESS_POSTGRES_DSN")
pytestmark = pytest.mark.skipif(not POSTGRES_DSN, reason="DSN PostgreSQL real nao configurada para testes de integracao.")


def seed_user(connection: psycopg.Connection, user_id: UUID, nonce: str) -> None:
    connection.execute(
        """INSERT INTO identity.users
           (id, full_name, cpf_document, birth_date, email, phone_e164, password_hash,
            face_hash, liveness_score, terms_accepted_at, lgpd_consent_at, status)
           VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s, 0.9900, NOW(), NOW(), 'active')
           ON CONFLICT (id) DO NOTHING""",
        (
            user_id,
            f"Usuario {nonce}",
            f"CPF-{nonce}",
            f"{nonce}@example.test",
            f"+55119{str(int(nonce[:7], 16)).zfill(8)[-8:]}",
            f"hash-{nonce}",
            f"face-{nonce}",
        ),
    )


def count_audit(connection: psycopg.Connection, module_name: str) -> int:
    return int(connection.execute("SELECT COUNT(*) FROM audit.logs WHERE module = %s", (module_name,)).fetchone()[0])


def count_events(connection: psycopg.Connection, module_name: str) -> int:
    if module_name == "finance":
        query = "SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE 'payment.%' OR routing_key LIKE 'finance.%'"
        return int(connection.execute(query).fetchone()[0])
    if module_name == "api_hub":
        query = "SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE 'api.%' OR routing_key LIKE 'api_hub.%'"
        return int(connection.execute(query).fetchone()[0])
    return int(
        connection.execute(
            "SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE %s",
            (f"{module_name}.%",),
        ).fetchone()[0]
    )


def test_finance_wallet_create_get_list_and_outbox() -> None:
    user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "finance")
        before_events = count_events(connection, "finance")

    store = FinancePostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="wallets",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={"wallet_type": "personal"},
        actor=str(actor_id),
        unique_fields=(),
        event="finance.wallet.created",
        idempotency_key=str(uuid4()),
    )
    fetched = store.get("wallets", created["id"])
    listed = store.list("wallets", user_id=str(user_id))

    assert created["status"] == "active"
    assert fetched is not None and fetched["id"] == created["id"]
    assert any(item["id"] == created["id"] for item in listed)

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "finance") >= before_audit + 1
        assert count_events(connection, "finance") >= before_events + 1


def test_business_company_create_get_list_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "business")
        before_events = count_events(connection, "business")

    store = BusinessPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="companies",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid4().hex[:14]}",
            "root_cnpj": uuid4().hex[:8],
            "legal_name": f"Empresa {nonce}",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="business.company.created",
        idempotency_key=str(uuid4()),
    )
    fetched = store.get("companies", created["id"])
    listed = store.list("companies", user_id=str(user_id))

    assert fetched is not None and fetched["id"] == created["id"]
    assert any(item["id"] == created["id"] for item in listed)

    store.soft_delete(fetched, str(actor_id))
    deleted = store.get("companies", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "business") >= before_audit + 2
        assert count_events(connection, "business") >= before_events + 1


def test_marketplace_store_create_get_list_and_outbox() -> None:
    owner_user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, owner_user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])

    business_store = BusinessPostgresStore(POSTGRES_DSN)
    company = business_store.create(
        resource_type="companies",
        user_id=str(owner_user_id),
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid4().hex[:14]}",
            "root_cnpj": uuid4().hex[:8],
            "legal_name": f"Loja Base {nonce}",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="business.company.created",
        idempotency_key=str(uuid4()),
    )

    with psycopg.connect(POSTGRES_DSN) as connection:
        before_audit = count_audit(connection, "marketplace")
        before_events = count_events(connection, "marketplace")

    store = MarketplacePostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="stores",
        user_id=str(owner_user_id),
        entity_id=None,
        status="active",
        payload={"company_id": company["id"], "name": f"Marketplace {nonce}"},
        actor=str(actor_id),
        unique_fields=(),
        event="marketplace.store.created",
        idempotency_key=str(uuid4()),
    )
    fetched = store.get("stores", created["id"])
    listed = store.list("stores", user_id=str(owner_user_id))

    assert fetched is not None and fetched["id"] == created["id"]
    assert any(item["id"] == created["id"] for item in listed)

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "marketplace") >= before_audit + 1
        assert count_events(connection, "marketplace") >= before_events + 1


def test_services_provider_create_update_and_soft_delete() -> None:
    provider_user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, provider_user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "services")
        before_events = count_events(connection, "services")

    store = ServicesPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="providers",
        user_id=str(provider_user_id),
        entity_id=None,
        status="active",
        payload={"category": "maintenance"},
        actor=str(actor_id),
        unique_fields=(),
        event="services.provider.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"category": "installation"},
        status="approved",
        actor=str(actor_id),
        action="approve",
        event="services.provider.approved",
    )
    assert updated["status"] == "approved"
    assert updated["payload"]["category"] == "installation"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("providers", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "services") >= before_audit + 3
        assert count_events(connection, "services") >= before_events + 2


def test_identity_user_create_update_and_soft_delete() -> None:
    nonce = uuid4().hex[:12]
    user_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        before_audit = count_audit(connection, "identity")
        before_events = count_events(connection, "identity")

    store = IdentityPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="users",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={
            "id": str(user_id),
            "full_name": f"Usuario {nonce}",
            "cpf_document": f"CPF-{nonce}",
            "birth_date": "1990-01-01",
            "email": f"{nonce}@example.test",
            "phone_e164": "+5511999999999",
            "password_hash": f"hash-{nonce}",
            "face_hash": f"face-{nonce}",
            "liveness_score": "0.99",
            "terms_accepted_at": "2026-01-01T00:00:00+00:00",
            "lgpd_consent_at": "2026-01-01T00:00:00+00:00",
        },
        actor=str(user_id),
        unique_fields=(),
        event="identity.user.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"full_name": f"Usuario {nonce} Atualizado"},
        status="verified",
        actor=str(user_id),
        action="verify",
        event="identity.user.verified",
    )
    assert updated["status"] == "verified"
    assert updated["payload"]["full_name"] == f"Usuario {nonce} Atualizado"

    store.soft_delete(updated, str(user_id))
    deleted = store.get("users", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "identity") >= before_audit + 3
        assert count_events(connection, "identity") >= before_events + 2


def test_api_hub_client_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "api_hub")
        before_events = count_events(connection, "api_hub")

    store = ApiHubPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="api_clients",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={
            "client_name": f"Client {nonce}",
            "client_id_hash": f"cid-{uuid4().hex}",
            "secret_reference": f"secret://{uuid4().hex}",
            "scopes": ["catalog:read"],
        },
        actor=str(actor_id),
        unique_fields=(),
        event="api_hub.client.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"client_name": f"Client {nonce} v2", "scopes": ["catalog:read", "orders:write"]},
        status="rotated",
        actor=str(actor_id),
        action="rotate",
        event="api_hub.client.rotated",
    )
    assert updated["status"] == "rotated"
    assert updated["payload"]["client_name"] == f"Client {nonce} v2"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("api_clients", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "api_hub") >= before_audit + 3
        assert count_events(connection, "api_hub") >= before_events + 2


def test_delivery_request_create_update_and_soft_delete() -> None:
    customer_user_id = uuid4()
    actor_id = uuid4()
    rider_user_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, customer_user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        seed_user(connection, rider_user_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "delivery")
        before_events = count_events(connection, "delivery")

    store = DeliveryPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="delivery_requests",
        user_id=str(customer_user_id),
        entity_id=None,
        status="quoted",
        payload={
            "service_type": "delivery",
            "origin": {"lat": -23.55, "lng": -46.63},
            "destination": {"lat": -23.56, "lng": -46.64},
            "distance_km": "4.2",
            "quoted_brl": "19.90",
            "insurance_required": False,
        },
        actor=str(actor_id),
        unique_fields=(),
        event="delivery.request.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"assigned_rider_user_id": str(rider_user_id)},
        status="assigned",
        actor=str(actor_id),
        action="assign",
        event="delivery.request.assigned",
    )
    assert updated["status"] == "assigned"
    assert updated["payload"]["assigned_rider_user_id"] == str(rider_user_id)

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("delivery_requests", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "delivery") >= before_audit + 3
        assert count_events(connection, "delivery") >= before_events + 2


def test_mobility_ride_create_update_and_soft_delete() -> None:
    passenger_user_id = uuid4()
    actor_id = uuid4()
    driver_user_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, passenger_user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        seed_user(connection, driver_user_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "mobility")
        before_events = count_events(connection, "mobility")

    store = MobilityPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="rides",
        user_id=str(passenger_user_id),
        entity_id=None,
        status="requested",
        payload={
            "origin": {"lat": -23.55, "lng": -46.63},
            "destination": {"lat": -23.54, "lng": -46.62},
            "fare_brl": "27.40",
            "vehicle_type": "car",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="mobility.ride.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"driver_user_id": str(driver_user_id)},
        status="accepted",
        actor=str(actor_id),
        action="accept",
        event="mobility.ride.accepted",
    )
    assert updated["status"] == "accepted"
    assert updated["payload"]["driver_user_id"] == str(driver_user_id)

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("rides", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "mobility") >= before_audit + 3
        assert count_events(connection, "mobility") >= before_events + 2


def test_stock_supplier_create_update_and_soft_delete() -> None:
    owner_user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, owner_user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])

    business_store = BusinessPostgresStore(POSTGRES_DSN)
    company = business_store.create(
        resource_type="companies",
        user_id=str(owner_user_id),
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid4().hex[:14]}",
            "root_cnpj": uuid4().hex[:8],
            "legal_name": f"Fornecedor Base {nonce}",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="business.company.created",
        idempotency_key=str(uuid4()),
    )

    with psycopg.connect(POSTGRES_DSN) as connection:
        before_audit = count_audit(connection, "stock")
        before_events = count_events(connection, "stock")

    store = StockPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="suppliers",
        user_id=str(owner_user_id),
        entity_id=company["id"],
        status="pending_validation",
        payload={},
        actor=str(actor_id),
        unique_fields=(),
        event="stock.supplier.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"api_configuration": {"mode": "sandbox"}},
        status="homologated",
        actor=str(actor_id),
        action="homologate",
        event="stock.supplier.homologated",
    )
    assert updated["status"] == "homologated"
    assert updated["entity_id"] == company["id"]

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("suppliers", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "stock") >= before_audit + 3
        assert count_events(connection, "stock") >= before_events + 2


def test_health_patient_create_update_and_soft_delete() -> None:
    patient_user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, patient_user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "health")
        before_events = count_events(connection, "health")

    store = HealthPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="patients",
        user_id=str(patient_user_id),
        entity_id=None,
        status="active",
        payload={"blood_type": "O+"},
        actor=str(actor_id),
        unique_fields=(),
        event="health.patient.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"blood_type": "A+"},
        status="reviewed",
        actor=str(actor_id),
        action="review",
        event="health.patient.reviewed",
    )
    assert updated["status"] == "reviewed"
    assert updated["payload"]["blood_type"] == "A+"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("patients", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "health") >= before_audit + 3
        assert count_events(connection, "health") >= before_events + 2


def test_riders_profile_create_update_and_soft_delete() -> None:
    rider_user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, rider_user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "riders")
        before_events = count_events(connection, "riders")

    finance_store = FinancePostgresStore(POSTGRES_DSN)
    wallet = finance_store.create(
        resource_type="wallets",
        user_id=str(rider_user_id),
        entity_id=None,
        status="active",
        payload={"wallet_type": "personal"},
        actor=str(actor_id),
        unique_fields=(),
        event="finance.wallet.created",
        idempotency_key=str(uuid4()),
    )

    store = RidersPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="rider_profiles",
        user_id=str(rider_user_id),
        entity_id=None,
        status="pending_documents",
        payload={
            "wallet_id": wallet["id"],
            "cnh_number_hash": f"cnh-{uuid4().hex[:10]}",
            "cnh_category": "AB",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="rider.submitted",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"cnh_category": "A"},
        status="approved",
        actor=str(actor_id),
        action="approve",
        event="rider.approved",
    )
    assert updated["status"] == "approved"
    assert updated["payload"]["cnh_category"] == "A"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("rider_profiles", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "riders") >= before_audit + 3
        assert count_events(connection, "riders") >= before_events + 2


def test_vision_device_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "vision")
        before_events = count_events(connection, "vision")

    store = VisionPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="devices",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={"device_fingerprint": f"dev-{nonce}"},
        actor=str(actor_id),
        unique_fields=(),
        event="vision.device.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"device_fingerprint": f"dev-{nonce}", "location_label": "Portaria"},
        status="reviewed",
        actor=str(actor_id),
        action="review",
        event="vision.device.reviewed",
    )
    assert updated["status"] == "reviewed"
    assert updated["payload"]["location_label"] == "Portaria"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("devices", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "vision") >= before_audit + 3
        assert count_events(connection, "vision") >= before_events + 2


def test_legal_case_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "legal")
        before_events = count_events(connection, "legal")

    store = LegalPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="cases",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={"case_number": f"CASE-{nonce}"},
        actor=str(actor_id),
        unique_fields=(),
        event="legal.case.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"case_number": f"CASE-{nonce}", "risk_brl": "1000.00"},
        status="triaged",
        actor=str(actor_id),
        action="triage",
        event="legal.case.triaged",
    )
    assert updated["status"] == "triaged"
    assert updated["payload"]["risk_brl"] == "1000.00"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("cases", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "legal") >= before_audit + 3
        assert count_events(connection, "legal") >= before_events + 2


def test_property_create_update_and_soft_delete() -> None:
    owner_user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, owner_user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "property")
        before_events = count_events(connection, "property")

    store = PropertyPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="properties",
        user_id=str(owner_user_id),
        entity_id=None,
        status="active",
        payload={
            "address": {"city": "Sao Paulo", "street": "Rua Um"},
            "property_type": "house",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="property.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={
            "address": {"city": "Sao Paulo", "street": "Rua Dois"},
            "property_type": "apartment",
        },
        status="reviewed",
        actor=str(actor_id),
        action="review",
        event="property.reviewed",
    )
    assert updated["status"] == "reviewed"
    assert updated["payload"]["property_type"] == "apartment"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("properties", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "property") >= before_audit + 3
        assert count_events(connection, "property") >= before_events + 2


def test_wms_warehouse_create_update_and_soft_delete() -> None:
    owner_user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, owner_user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])

    business_store = BusinessPostgresStore(POSTGRES_DSN)
    company = business_store.create(
        resource_type="companies",
        user_id=str(owner_user_id),
        entity_id=None,
        status="active",
        payload={
            "cnpj": f"{uuid4().hex[:14]}",
            "root_cnpj": uuid4().hex[:8],
            "legal_name": f"Armazem Base {nonce}",
        },
        actor=str(actor_id),
        unique_fields=(),
        event="business.company.created",
        idempotency_key=str(uuid4()),
    )

    with psycopg.connect(POSTGRES_DSN) as connection:
        before_audit = count_audit(connection, "wms")
        before_events = count_events(connection, "wms")

    store = WmsPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="warehouses",
        user_id=str(owner_user_id),
        entity_id=company["id"],
        status="active",
        payload={"name": "CD Principal"},
        actor=str(actor_id),
        unique_fields=(),
        event="wms.warehouse.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"name": "CD Principal 2", "addressing_rules": {"bin_format": "A-01"}},
        status="reviewed",
        actor=str(actor_id),
        action="review",
        event="wms.warehouse.reviewed",
    )
    assert updated["status"] == "reviewed"
    assert updated["payload"]["name"] == "CD Principal 2"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("warehouses", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "wms") >= before_audit + 3
        assert count_events(connection, "wms") >= before_events + 2


def test_tms_carrier_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "tms")
        before_events = count_events(connection, "tms")

    store = TmsPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="carriers",
        user_id=str(user_id),
        entity_id=None,
        status="draft",
        payload={"name": "Transportadora Base", "coverage": ["sp", "rj"]},
        actor=str(actor_id),
        unique_fields=(),
        event="tms.carrier.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"name": "Transportadora Prime", "coverage": ["sp", "rj", "mg"]},
        status="approved",
        actor=str(actor_id),
        action="approve",
        event="tms.carrier.approved",
    )
    assert updated["status"] == "approved"
    assert updated["payload"]["name"] == "Transportadora Prime"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("carriers", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "tms") >= before_audit + 3
        assert count_events(connection, "tms") >= before_events + 2


def test_crm_lead_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()
    nonce = uuid4().hex[:12]

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, nonce)
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "crm")
        before_events = count_events(connection, "crm")

    store = CrmPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="leads",
        user_id=str(user_id),
        entity_id=None,
        status="new",
        payload={"name": f"Lead {nonce}", "source": "landing-page"},
        actor=str(actor_id),
        unique_fields=(),
        event="crm.lead.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"name": f"Lead {nonce}", "source": "partner", "score": 85},
        status="qualified",
        actor=str(actor_id),
        action="qualify",
        event="crm.lead.qualified",
    )
    assert updated["status"] == "qualified"
    assert updated["payload"]["score"] == 85

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("leads", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "crm") >= before_audit + 3
        assert count_events(connection, "crm") >= before_events + 2


def test_bpm_process_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "bpm")
        before_events = count_events(connection, "bpm")

    store = BpmPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="processes",
        user_id=str(user_id),
        entity_id=None,
        status="draft",
        payload={"name": "Onboarding PJ", "version": 1},
        actor=str(actor_id),
        unique_fields=(),
        event="bpm.process.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"name": "Onboarding PJ", "version": 2, "published": True},
        status="published",
        actor=str(actor_id),
        action="publish",
        event="bpm.process.published",
    )
    assert updated["status"] == "published"
    assert updated["payload"]["version"] == 2

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("processes", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "bpm") >= before_audit + 3
        assert count_events(connection, "bpm") >= before_events + 2


def test_document_folder_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "document")
        before_events = count_events(connection, "document")

    store = DocumentPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="folders",
        user_id=str(user_id),
        entity_id=None,
        status="active",
        payload={"name": "Contratos 2026", "classification": "restricted"},
        actor=str(actor_id),
        unique_fields=(),
        event="document.folder.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"name": "Contratos 2026", "classification": "confidential"},
        status="reviewed",
        actor=str(actor_id),
        action="review",
        event="document.folder.reviewed",
    )
    assert updated["status"] == "reviewed"
    assert updated["payload"]["classification"] == "confidential"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("folders", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "document") >= before_audit + 3
        assert count_events(connection, "document") >= before_events + 2


def test_bi_dataset_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "bi")
        before_events = count_events(connection, "bi")

    store = BiPostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="datasets",
        user_id=str(user_id),
        entity_id=None,
        status="draft",
        payload={"name": "Receita Consolidada", "refresh_mode": "daily"},
        actor=str(actor_id),
        unique_fields=(),
        event="bi.dataset.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"name": "Receita Consolidada", "refresh_mode": "hourly"},
        status="published",
        actor=str(actor_id),
        action="publish",
        event="bi.dataset.published",
    )
    assert updated["status"] == "published"
    assert updated["payload"]["refresh_mode"] == "hourly"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("datasets", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "bi") >= before_audit + 3
        assert count_events(connection, "bi") >= before_events + 2


def test_ai_core_memory_create_update_and_soft_delete() -> None:
    user_id = uuid4()
    actor_id = uuid4()

    with psycopg.connect(POSTGRES_DSN) as connection:
        seed_user(connection, user_id, uuid4().hex[:12])
        seed_user(connection, actor_id, uuid4().hex[:12])
        before_audit = count_audit(connection, "ai_core")
        before_events = count_events(connection, "ai_core")

    store = AiCorePostgresStore(POSTGRES_DSN)
    created = store.create(
        resource_type="ai_memories",
        user_id=str(user_id),
        entity_id=None,
        status="draft",
        payload={"memory_key": f"mk-{uuid4().hex[:8]}", "summary": "Memoria inicial"},
        actor=str(actor_id),
        unique_fields=(),
        event="ai_core.memory.created",
        idempotency_key=str(uuid4()),
    )
    updated = store.update(
        created,
        payload={"memory_key": created["payload"]["memory_key"], "summary": "Memoria consolidada"},
        status="indexed",
        actor=str(actor_id),
        action="index",
        event="ai_core.memory.indexed",
    )
    assert updated["status"] == "indexed"
    assert updated["payload"]["summary"] == "Memoria consolidada"

    store.soft_delete(updated, str(actor_id))
    deleted = store.get("ai_memories", created["id"])
    assert deleted is None

    with psycopg.connect(POSTGRES_DSN) as connection:
        assert count_audit(connection, "ai_core") >= before_audit + 3
        assert count_events(connection, "ai_core") >= before_events + 2
