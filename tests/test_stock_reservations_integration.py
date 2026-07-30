from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID, uuid4

import psycopg
import pytest

from modules.shared.correlation import set_correlation_id
from modules.shared.stock_postgres_store import (
    StockIdempotencyConflictError,
    StockNotFoundError,
    StockPostgresStore,
)

POSTGRES_DSN = os.getenv("ALL_IN_ONE_STOCK_POSTGRES_TEST_DSN")
pytestmark = pytest.mark.skipif(
    not POSTGRES_DSN,
    reason="DSN PostgreSQL do Stock não configurada para testes de integração.",
)


def _phone(nonce: str) -> str:
    return f"+55119{str(int(nonce[:7], 16)).zfill(8)[-8:]}"


def _seed_user(connection: psycopg.Connection, user_id: UUID) -> None:
    nonce = uuid4().hex[:12]
    connection.execute(
        """INSERT INTO identity.users
           (id, full_name, cpf_document, birth_date, email, phone_e164, password_hash,
            face_hash, liveness_score, terms_accepted_at, lgpd_consent_at, status)
           VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s, 0.9900,
                   NOW(), NOW(), 'active')""",
        (
            user_id,
            f"Usuário Stock {nonce}",
            f"CPF-{nonce}",
            f"{nonce}@example.test",
            _phone(nonce),
            f"hash-{nonce}",
            f"face-{nonce}",
        ),
    )


def _seed_catalog(
    connection: psycopg.Connection,
    *,
    owner_id: UUID,
    company_id: UUID,
    store_id: UUID,
    product_id: UUID,
    sku: str,
) -> None:
    nonce = uuid4().hex[:12]
    connection.execute(
        """INSERT INTO business.companies
           (id, user_id, cnpj, root_cnpj, legal_name,
            legal_representative_user_id, status, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)""",
        (
            company_id,
            owner_id,
            nonce[:14],
            nonce[:8],
            f"Empresa Stock {nonce}",
            owner_id,
            owner_id,
            owner_id,
        ),
    )
    connection.execute(
        """INSERT INTO marketplace.stores
           (id, user_id, company_id, name, status, created_by, updated_by)
           VALUES (%s, %s, %s, %s, 'active', %s, %s)""",
        (store_id, owner_id, company_id, f"Loja {nonce}", owner_id, owner_id),
    )
    connection.execute(
        """INSERT INTO marketplace.products
           (id, user_id, store_id, sku, name, price_brl, stock_quantity,
            status, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, 10.00, 999, 'published', %s, %s)""",
        (
            product_id,
            owner_id,
            store_id,
            sku,
            f"Produto {nonce}",
            owner_id,
            owner_id,
        ),
    )


def _context() -> dict[str, UUID | str]:
    owner_id = uuid4()
    buyer_id = uuid4()
    company_id = uuid4()
    store_id = uuid4()
    product_id = uuid4()
    sku = f"SKU-{uuid4().hex[:12]}"
    with psycopg.connect(POSTGRES_DSN) as connection:
        _seed_user(connection, owner_id)
        _seed_user(connection, buyer_id)
        _seed_catalog(
            connection,
            owner_id=owner_id,
            company_id=company_id,
            store_id=store_id,
            product_id=product_id,
            sku=sku,
        )
    return {
        "owner_id": owner_id,
        "buyer_id": buyer_id,
        "company_id": company_id,
        "store_id": store_id,
        "product_id": product_id,
        "sku": sku,
    }


def _create_inventory(
    store: StockPostgresStore,
    context: dict[str, UUID | str],
    quantity: Decimal,
) -> dict[str, object]:
    set_correlation_id(str(uuid4()))
    return store.create_inventory_item(
        user_id=str(context["owner_id"]),
        company_id=str(context["company_id"]),
        warehouse_id=None,
        product_id=str(context["product_id"]),
        sku=str(context["sku"]),
        physical_quantity=quantity,
        actor=str(context["owner_id"]),
        metadata={"source": "integration_test"},
    )


def _reserve(
    store: StockPostgresStore,
    *,
    context: dict[str, UUID | str],
    inventory_id: str,
    quantity: Decimal,
    key: str,
    order_id: UUID | None = None,
    expires_in_seconds: int = 900,
) -> dict[str, object]:
    correlation_id = uuid4()
    set_correlation_id(str(correlation_id))
    return store.reserve_inventory(
        user_id=str(context["buyer_id"]),
        company_id=str(context["company_id"]),
        inventory_item_id=inventory_id,
        order_id=str(order_id or uuid4()),
        quantity=quantity,
        expires_in_seconds=expires_in_seconds,
        actor=str(context["buyer_id"]),
        idempotency_key=key,
        correlation_id=str(correlation_id),
        causation_id=None,
    )


def test_reservation_idempotency_commit_release_expiration_and_events() -> None:
    context = _context()
    store = StockPostgresStore(POSTGRES_DSN)
    inventory = _create_inventory(store, context, Decimal("10"))
    order_id = uuid4()
    key = f"reserve-{uuid4()}"

    with psycopg.connect(POSTGRES_DSN) as connection:
        events_before = connection.execute(
            "SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE 'stock.reservation.%'"
        ).fetchone()[0]
        audits_before = connection.execute(
            "SELECT COUNT(*) FROM audit.logs WHERE module = 'stock'"
        ).fetchone()[0]

    reserved = _reserve(
        store,
        context=context,
        inventory_id=str(inventory["id"]),
        quantity=Decimal("2"),
        key=key,
        order_id=order_id,
    )
    repeated = _reserve(
        store,
        context=context,
        inventory_id=str(inventory["id"]),
        quantity=Decimal("2.0000"),
        key=key,
        order_id=order_id,
    )

    assert reserved["status"] == "reserved"
    assert repeated["reservation_id"] == reserved["reservation_id"]

    with pytest.raises(StockIdempotencyConflictError):
        _reserve(
            store,
            context=context,
            inventory_id=str(inventory["id"]),
            quantity=Decimal("3"),
            key=key,
            order_id=order_id,
        )

    set_correlation_id(str(uuid4()))
    committed = store.commit_reservation(
        reservation_id=str(reserved["reservation_id"]),
        expected_user_id=str(context["buyer_id"]),
        actor=str(context["buyer_id"]),
    )
    committed_again = store.commit_reservation(
        reservation_id=str(reserved["reservation_id"]),
        expected_user_id=str(context["buyer_id"]),
        actor=str(context["buyer_id"]),
    )
    assert committed["status"] == "committed"
    assert committed_again["reservation_id"] == committed["reservation_id"]

    releasable = _reserve(
        store,
        context=context,
        inventory_id=str(inventory["id"]),
        quantity=Decimal("1"),
        key=f"release-{uuid4()}",
    )
    set_correlation_id(str(uuid4()))
    released = store.release_reservation(
        reservation_id=str(releasable["reservation_id"]),
        expected_user_id=str(context["buyer_id"]),
        actor=str(context["buyer_id"]),
        reason="checkout_cancelled",
    )
    released_again = store.release_reservation(
        reservation_id=str(releasable["reservation_id"]),
        expected_user_id=str(context["buyer_id"]),
        actor=str(context["buyer_id"]),
        reason="checkout_cancelled",
    )
    assert released["status"] == "released"
    assert released_again["reservation_id"] == released["reservation_id"]

    expiring = _reserve(
        store,
        context=context,
        inventory_id=str(inventory["id"]),
        quantity=Decimal("1"),
        key=f"expire-{uuid4()}",
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            "UPDATE stock.stock_reservations SET expires_at = NOW() - INTERVAL '1 second' WHERE id = %s",
            (expiring["reservation_id"],),
        )
    set_correlation_id(str(uuid4()))
    expired = store.expire_due_reservations(actor=str(context["owner_id"]), limit=10)
    assert any(item["reservation_id"] == expiring["reservation_id"] for item in expired)

    with psycopg.connect(POSTGRES_DSN) as connection:
        inventory_row = connection.execute(
            "SELECT physical_quantity, reserved_quantity, available_quantity FROM stock.inventory_items WHERE id = %s",
            (inventory["id"],),
        ).fetchone()
        assert inventory_row[0] == Decimal("8.0000")
        assert inventory_row[1] == Decimal("0.0000")
        assert inventory_row[2] == Decimal("8.0000")
        events_after = connection.execute(
            "SELECT COUNT(*) FROM audit.domain_events WHERE routing_key LIKE 'stock.reservation.%'"
        ).fetchone()[0]
        audits_after = connection.execute(
            "SELECT COUNT(*) FROM audit.logs WHERE module = 'stock'"
        ).fetchone()[0]
        assert events_after == events_before + 6
        assert audits_after >= audits_before + 7
    store.connection.close()


def test_insufficient_stock_and_company_isolation_do_not_change_balance() -> None:
    context = _context()
    other = _context()
    store = StockPostgresStore(POSTGRES_DSN)
    inventory = _create_inventory(store, context, Decimal("2"))

    rejected = _reserve(
        store,
        context=context,
        inventory_id=str(inventory["id"]),
        quantity=Decimal("3"),
        key=f"insufficient-{uuid4()}",
    )
    assert rejected["status"] == "rejected"

    with pytest.raises(StockNotFoundError):
        _reserve(
            store,
            context=other,
            inventory_id=str(inventory["id"]),
            quantity=Decimal("1"),
            key=f"wrong-company-{uuid4()}",
        )

    with psycopg.connect(POSTGRES_DSN) as connection:
        balance = connection.execute(
            "SELECT physical_quantity, reserved_quantity FROM stock.inventory_items WHERE id = %s",
            (inventory["id"],),
        ).fetchone()
        assert balance == (Decimal("2.0000"), Decimal("0.0000"))
    store.connection.close()


def test_concurrent_reservations_never_make_stock_negative() -> None:
    context = _context()
    setup_store = StockPostgresStore(POSTGRES_DSN)
    inventory = _create_inventory(setup_store, context, Decimal("1"))
    setup_store.connection.close()

    def attempt(key: str) -> dict[str, object]:
        worker_store = StockPostgresStore(POSTGRES_DSN)
        try:
            return _reserve(
                worker_store,
                context=context,
                inventory_id=str(inventory["id"]),
                quantity=Decimal("1"),
                key=key,
            )
        finally:
            worker_store.connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(
            executor.map(
                attempt,
                [f"concurrent-a-{uuid4()}", f"concurrent-b-{uuid4()}"],
            )
        )

    assert sorted(item["status"] for item in results) == ["rejected", "reserved"]
    with psycopg.connect(POSTGRES_DSN) as connection:
        balance = connection.execute(
            "SELECT physical_quantity, reserved_quantity, available_quantity FROM stock.inventory_items WHERE id = %s",
            (inventory["id"],),
        ).fetchone()
        assert balance == (Decimal("1.0000"), Decimal("1.0000"), Decimal("0.0000"))
