from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import uuid4

import psycopg
import pytest

from marketplace_checkout_test_support import (
    POSTGRES_DSN,
    _context,
    _create_checkout,
    _seed_buyer_workspace,
    _seed_user,
)
from modules.shared.correlation import set_correlation_id
from modules.shared.marketplace_checkout_postgres_store import (
    CheckoutConflictError,
    CheckoutIdempotencyConflictError,
    CheckoutNotFoundError,
    MarketplaceCheckoutPostgresStore,
)

pytestmark = pytest.mark.skipif(
    not POSTGRES_DSN,
    reason="DSN PostgreSQL do Marketplace não configurada para integração.",
)


def test_checkout_idempotency_approval_ledger_and_outbox() -> None:
    context = _context()
    store = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
    key = f"checkout-{uuid4()}"

    checkout = _create_checkout(store, context, key=key)
    replay = _create_checkout(store, context, key=key)
    assert checkout["checkout_id"] == replay["checkout_id"]
    assert checkout["order_id"] == replay["order_id"]
    assert checkout["status"] == "pending_payment"
    assert checkout["total_brl"] == "39.8"
    assert checkout["snapshot"]["total_brl"] == "39.8"

    with pytest.raises(CheckoutIdempotencyConflictError):
        _create_checkout(
            store,
            context,
            key=key,
            expected_total_brl=Decimal("40.00"),
        )
    with pytest.raises(CheckoutNotFoundError):
        _create_checkout(
            store,
            context,
            key=f"other-user-{uuid4()}",
            user_id=context["other_user_id"],
        )

    payment_key = f"payment-{uuid4()}"
    provider_reference = f"provider-{uuid4()}"
    correlation_id = str(uuid4())
    set_correlation_id(correlation_id)
    paid = store.apply_payment_result(
        checkout_id=str(checkout["checkout_id"]),
        outcome="approved",
        actor=str(context["owner_id"]),
        idempotency_key=payment_key,
        correlation_id=correlation_id,
        provider_reference=provider_reference,
        reason=None,
    )
    replay_paid = store.apply_payment_result(
        checkout_id=str(checkout["checkout_id"]),
        outcome="approved",
        actor=str(context["owner_id"]),
        idempotency_key=payment_key,
        correlation_id=correlation_id,
        provider_reference=provider_reference,
        reason=None,
    )
    assert paid["status"] == "confirmed"
    assert paid["payment_status"] == "authorized"
    assert replay_paid["checkout_id"] == paid["checkout_id"]

    another_result = store.apply_payment_result(
        checkout_id=str(checkout["checkout_id"]),
        outcome="approved",
        actor=str(context["owner_id"]),
        idempotency_key=f"payment-terminal-{uuid4()}",
        correlation_id=str(uuid4()),
        provider_reference=None,
        reason=None,
    )
    assert another_result["status"] == "confirmed"

    with psycopg.connect(POSTGRES_DSN) as connection:
        ledger_count = connection.execute(
            """SELECT COUNT(*) FROM finance.ledger_entries
               WHERE reference_type = 'marketplace.checkout'
                 AND reference_id = %s""",
            (checkout["checkout_id"],),
        ).fetchone()[0]
        assert ledger_count == 1
        inventory = connection.execute(
            """SELECT physical_quantity, reserved_quantity, available_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (context["inventory_id"],),
        ).fetchone()
        assert inventory == (
            Decimal("3.0000"),
            Decimal("0.0000"),
            Decimal("3.0000"),
        )
        reservation_statuses = connection.execute(
            """SELECT status FROM stock.stock_reservations
               WHERE order_id = %s""",
            (checkout["order_id"],),
        ).fetchall()
        assert reservation_statuses == [("committed",)]
        cart_status = connection.execute(
            "SELECT status FROM marketplace.carts WHERE id = %s",
            (context["cart_id"],),
        ).fetchone()[0]
        assert cart_status == "converted"
        event_keys = {
            row[0]
            for row in connection.execute(
                """SELECT routing_key FROM audit.domain_events
                   WHERE aggregate_id IN (%s, %s)""",
                (checkout["checkout_id"], checkout["order_id"]),
            ).fetchall()
        }
        assert "marketplace.checkout.started" in event_keys
        assert "marketplace.order.created" in event_keys
        assert "finance.payment.pending" in event_keys
        assert "marketplace.checkout.confirmed" in event_keys
    store.connection.close()


def test_rejection_and_expiration_release_stock_and_reactivate_cart() -> None:
    rejected_context = _context(stock_quantity=Decimal("4"), cart_quantity=1)
    rejected_store = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
    rejected = _create_checkout(
        rejected_store,
        rejected_context,
        key=f"checkout-reject-{uuid4()}",
    )
    result = rejected_store.apply_payment_result(
        checkout_id=str(rejected["checkout_id"]),
        outcome="rejected",
        actor=str(rejected_context["owner_id"]),
        idempotency_key=f"payment-reject-{uuid4()}",
        correlation_id=str(uuid4()),
        provider_reference=None,
        reason="provider_rejected",
    )
    assert result["status"] == "payment_failed"
    with psycopg.connect(POSTGRES_DSN) as connection:
        balance = connection.execute(
            """SELECT physical_quantity, reserved_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (rejected_context["inventory_id"],),
        ).fetchone()
        assert balance == (Decimal("4.0000"), Decimal("0.0000"))
        assert connection.execute(
            "SELECT status FROM marketplace.carts WHERE id = %s",
            (rejected_context["cart_id"],),
        ).fetchone()[0] == "active"
        assert connection.execute(
            """SELECT COUNT(*) FROM finance.ledger_entries
               WHERE reference_id = %s""",
            (rejected["checkout_id"],),
        ).fetchone()[0] == 0
    rejected_store.connection.close()

    expired_context = _context(stock_quantity=Decimal("2"), cart_quantity=1)
    expired_store = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
    expiring = _create_checkout(
        expired_store,
        expired_context,
        key=f"checkout-expire-{uuid4()}",
        expires_in_seconds=60,
    )
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """UPDATE marketplace.checkouts
               SET reservation_expires_at = NOW() - INTERVAL '1 second'
               WHERE id = %s""",
            (expiring["checkout_id"],),
        )
        connection.execute(
            """UPDATE stock.stock_reservations
               SET expires_at = NOW() - INTERVAL '1 second'
               WHERE order_id = %s""",
            (expiring["order_id"],),
        )
    expired = expired_store.expire_due_checkouts(
        actor=str(expired_context["owner_id"]),
        correlation_id=str(uuid4()),
        limit=10,
    )
    assert any(item["checkout_id"] == expiring["checkout_id"] for item in expired)
    with psycopg.connect(POSTGRES_DSN) as connection:
        balance = connection.execute(
            """SELECT physical_quantity, reserved_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (expired_context["inventory_id"],),
        ).fetchone()
        assert balance == (Decimal("2.0000"), Decimal("0.0000"))
        assert connection.execute(
            "SELECT status FROM marketplace.carts WHERE id = %s",
            (expired_context["cart_id"],),
        ).fetchone()[0] == "active"
    expired_store.connection.close()


def test_concurrent_checkouts_do_not_duplicate_order_or_make_stock_negative() -> None:
    context = _context(stock_quantity=Decimal("1"), cart_quantity=1)
    second_buyer = uuid4()
    with psycopg.connect(POSTGRES_DSN) as connection:
        _seed_user(connection, second_buyer)
        second_cart, second_wallet = _seed_buyer_workspace(
            connection,
            buyer_id=second_buyer,
            company_id=context["company_id"],
            product_id=context["product_id"],
            quantity=1,
        )

    attempts = [
        {
            **context,
            "cart_id": context["cart_id"],
            "wallet_id": context["wallet_id"],
            "buyer_id": context["buyer_id"],
        },
        {
            **context,
            "cart_id": second_cart,
            "wallet_id": second_wallet,
            "buyer_id": second_buyer,
        },
    ]

    def attempt(candidate: dict[str, object]) -> str:
        worker = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
        try:
            _create_checkout(
                worker,
                candidate,
                key=f"concurrent-{uuid4()}",
            )
            return "reserved"
        except CheckoutConflictError:
            return "rejected"
        finally:
            worker.connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(attempt, attempts))
    assert sorted(outcomes) == ["rejected", "reserved"]

    with psycopg.connect(POSTGRES_DSN) as connection:
        balance = connection.execute(
            """SELECT physical_quantity, reserved_quantity, available_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (context["inventory_id"],),
        ).fetchone()
        assert balance == (
            Decimal("1.0000"),
            Decimal("1.0000"),
            Decimal("0.0000"),
        )
        active_orders = connection.execute(
            """SELECT COUNT(*) FROM marketplace.orders
               WHERE store_id = %s AND status = 'pending_payment'""",
            (context["store_id"],),
        ).fetchone()[0]
        assert active_orders == 1
