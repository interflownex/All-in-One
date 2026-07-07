from __future__ import annotations

import os
from uuid import UUID, uuid4

import psycopg
import pytest

from modules.shared.business_postgres_store import BusinessPostgresStore
from modules.shared.finance_postgres_store import FinancePostgresStore
from modules.shared.marketplace_postgres_store import MarketplacePostgresStore
from modules.shared.services_postgres_store import ServicesPostgresStore


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
