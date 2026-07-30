from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from uuid import UUID, uuid4

import psycopg
import pytest

from modules.shared.audit_contract import AuditContext, set_audit_context
from modules.shared.correlation import set_correlation_id
from modules.shared.finance_postgres_store import FinancePostgresStore
from modules.shared.marketplace_checkout_postgres_store import (
    MarketplaceCheckoutConflictError,
    MarketplaceCheckoutIdempotencyConflictError,
    MarketplaceCheckoutPaymentError,
    MarketplaceCheckoutPostgresStore,
)
from modules.shared.marketplace_postgres_store import MarketplacePostgresStore
from modules.shared.stock_postgres_store import StockPostgresStore

POSTGRES_DSN = os.getenv("ALL_IN_ONE_MARKETPLACE_CHECKOUT_TEST_DSN")
pytestmark = pytest.mark.skipif(
    not POSTGRES_DSN,
    reason="DSN PostgreSQL do checkout Marketplace não configurada.",
)


def _phone(nonce: str) -> str:
    return f"+55119{str(int(nonce[:7], 16)).zfill(8)[-8:]}"


def _seed_user(connection: psycopg.Connection, user_id: UUID) -> None:
    nonce = uuid4().hex[:12]
    connection.execute(
        """INSERT INTO identity.users
           (id, full_name, cpf_document, birth_date, email, phone_e164,
            password_hash, face_hash, liveness_score, terms_accepted_at,
            lgpd_consent_at, status)
           VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s,
                   0.9900, NOW(), NOW(), 'active')""",
        (
            user_id,
            f"Usuário Checkout {nonce}",
            f"CPF-{nonce}",
            f"{nonce}@example.test",
            _phone(nonce),
            f"hash-{nonce}",
            f"face-{nonce}",
        ),
    )


def _seed_company_store_product(
    connection: psycopg.Connection,
    *,
    owner_id: UUID,
    company_id: UUID,
    store_id: UUID,
    product_id: UUID,
    sku: str,
    price_brl: Decimal = Decimal("10.00"),
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
            f"Empresa Checkout {nonce}",
            owner_id,
            owner_id,
            owner_id,
        ),
    )
    connection.execute(
        """INSERT INTO marketplace.stores
           (id, user_id, company_id, name, status, metadata, created_by, updated_by)
           VALUES (%s, %s, %s, %s, 'active', %s, %s, %s)""",
        (
            store_id,
            owner_id,
            company_id,
            f"Loja Checkout {nonce}",
            psycopg.types.json.Jsonb(
                {"runtime_payload": {"name": f"Loja Checkout {nonce}"}}
            ),
            owner_id,
            owner_id,
        ),
    )
    connection.execute(
        """INSERT INTO marketplace.products
           (id, user_id, store_id, sku, name, price_brl, stock_quantity,
            status, metadata, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, %s, 999, 'published', %s, %s, %s)""",
        (
            product_id,
            owner_id,
            store_id,
            sku,
            f"Produto Checkout {nonce}",
            price_brl,
            psycopg.types.json.Jsonb(
                {
                    "runtime_payload": {
                        "store_id": str(store_id),
                        "sku": sku,
                        "name": f"Produto Checkout {nonce}",
                        "price_brl": str(price_brl),
                        "currency": "BRL",
                    }
                }
            ),
            owner_id,
            owner_id,
        ),
    )


def _audit_context(company_id: UUID | None = None) -> None:
    set_audit_context(
        AuditContext(
            tenant_id=str(company_id) if company_id else None,
            company_id=str(company_id) if company_id else None,
            origin="test",
            channel="integration",
        )
    )


def _create_cart(*, buyer_id: UUID, product_id: UUID, quantity: int) -> str:
    store = MarketplacePostgresStore(POSTGRES_DSN)
    try:
        cart = store.create(
            resource_type="carts",
            user_id=str(buyer_id),
            entity_id=None,
            status="active",
            payload={
                "cart_type": "cart",
                "items": [{"product_id": str(product_id), "quantity": quantity}],
            },
            actor=str(buyer_id),
            unique_fields=(),
            event="marketplace.cart.created",
            idempotency_key=f"cart-{uuid4()}",
        )
        return str(cart["id"])
    finally:
        store.connection.close()


def _create_wallet(*, buyer_id: UUID, available: Decimal) -> str:
    store = FinancePostgresStore(POSTGRES_DSN)
    try:
        wallet = store.create(
            resource_type="wallets",
            user_id=str(buyer_id),
            entity_id=None,
            status="active",
            payload={"wallet_type": "personal"},
            actor=str(buyer_id),
            unique_fields=(),
            event="finance.wallet.created",
            idempotency_key=f"wallet-{uuid4()}",
        )
    finally:
        store.connection.close()
    with psycopg.connect(POSTGRES_DSN) as connection:
        connection.execute(
            """UPDATE finance.wallets
               SET brl_available = %s, brl_held = 0, updated_at = NOW()
               WHERE id = %s""",
            (available, wallet["id"]),
        )
    return str(wallet["id"])


def _create_inventory(
    *,
    owner_id: UUID,
    company_id: UUID,
    product_id: UUID,
    sku: str,
    quantity: Decimal,
) -> str:
    store = StockPostgresStore(POSTGRES_DSN)
    try:
        inventory = store.create_inventory_item(
            user_id=str(owner_id),
            company_id=str(company_id),
            warehouse_id=None,
            product_id=str(product_id),
            sku=sku,
            physical_quantity=quantity,
            actor=str(owner_id),
            metadata={"source": "checkout_integration_test"},
        )
        return str(inventory["id"])
    finally:
        store.connection.close()


def _context(
    *,
    stock: Decimal = Decimal("5"),
    wallet: Decimal = Decimal("100.00"),
    quantity: int = 2,
) -> dict[str, UUID | str]:
    owner_id = uuid4()
    buyer_id = uuid4()
    company_id = uuid4()
    store_id = uuid4()
    product_id = uuid4()
    sku = f"SKU-{uuid4().hex[:12]}"
    with psycopg.connect(POSTGRES_DSN) as connection:
        _seed_user(connection, owner_id)
        _seed_user(connection, buyer_id)
        _seed_company_store_product(
            connection,
            owner_id=owner_id,
            company_id=company_id,
            store_id=store_id,
            product_id=product_id,
            sku=sku,
        )
    _audit_context(company_id)
    inventory_id = _create_inventory(
        owner_id=owner_id,
        company_id=company_id,
        product_id=product_id,
        sku=sku,
        quantity=stock,
    )
    cart_id = _create_cart(
        buyer_id=buyer_id,
        product_id=product_id,
        quantity=quantity,
    )
    wallet_id = _create_wallet(buyer_id=buyer_id, available=wallet)
    return {
        "owner_id": owner_id,
        "buyer_id": buyer_id,
        "company_id": company_id,
        "store_id": store_id,
        "product_id": product_id,
        "inventory_id": inventory_id,
        "cart_id": cart_id,
        "wallet_id": wallet_id,
    }


def _create_checkout(
    store: MarketplaceCheckoutPostgresStore,
    *,
    context: dict[str, UUID | str],
    key: str,
    expected_total: Decimal = Decimal("20.00"),
) -> dict[str, object]:
    correlation_id = uuid4()
    set_correlation_id(str(correlation_id))
    _audit_context(UUID(str(context["company_id"])))
    return store.create_checkout(
        user_id=str(context["buyer_id"]),
        cart_id=str(context["cart_id"]),
        currency="BRL",
        expected_total_brl=expected_total,
        payment_method="wallet",
        actor=str(context["buyer_id"]),
        idempotency_key=key,
        correlation_id=str(correlation_id),
        causation_id=None,
    )


def test_checkout_idempotency_wallet_confirmation_and_immutable_snapshot() -> None:
    context = _context()
    store = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
    create_key = f"checkout-create-{uuid4()}"

    checkout = _create_checkout(store, context=context, key=create_key)
    repeated = _create_checkout(store, context=context, key=create_key)

    assert checkout["status"] == "pending_payment"
    assert repeated["checkout_id"] == checkout["checkout_id"]
    assert repeated["order_id"] == checkout["order_id"]

    with pytest.raises(MarketplaceCheckoutIdempotencyConflictError):
        _create_checkout(
            store,
            context=context,
            key=create_key,
            expected_total=Decimal("21.00"),
        )

    confirm_key = f"checkout-confirm-{uuid4()}"
    correlation_id = uuid4()
    set_correlation_id(str(correlation_id))
    _audit_context(UUID(str(context["company_id"])))
    confirmed = store.confirm_checkout(
        checkout_id=str(checkout["checkout_id"]),
        user_id=str(context["buyer_id"]),
        payment_method="wallet",
        actor=str(context["buyer_id"]),
        idempotency_key=confirm_key,
        correlation_id=str(correlation_id),
        causation_id=str(checkout["checkout_id"]),
    )
    repeated_confirmation = store.confirm_checkout(
        checkout_id=str(checkout["checkout_id"]),
        user_id=str(context["buyer_id"]),
        payment_method="wallet",
        actor=str(context["buyer_id"]),
        idempotency_key=confirm_key,
        correlation_id=str(correlation_id),
        causation_id=str(checkout["checkout_id"]),
    )

    assert confirmed["status"] == "confirmed"
    assert confirmed["payment_status"] == "authorized"
    assert confirmed["escrow_id"] is not None
    assert repeated_confirmation["escrow_id"] == confirmed["escrow_id"]

    with psycopg.connect(POSTGRES_DSN) as connection:
        inventory = connection.execute(
            """SELECT physical_quantity, reserved_quantity, available_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (context["inventory_id"],),
        ).fetchone()
        wallet = connection.execute(
            """SELECT brl_available, brl_held
               FROM finance.wallets WHERE id = %s""",
            (context["wallet_id"],),
        ).fetchone()
        reservation_count = connection.execute(
            """SELECT COUNT(*) FROM stock.stock_reservations
               WHERE order_id = %s AND status = 'committed'""",
            (checkout["order_id"],),
        ).fetchone()[0]
        escrow_count = connection.execute(
            """SELECT COUNT(*) FROM finance.escrows
               WHERE id = %s AND status = 'held'""",
            (confirmed["escrow_id"],),
        ).fetchone()[0]
        ledger_count = connection.execute(
            """SELECT COUNT(*) FROM finance.ledger_entries
               WHERE idempotency_key = %s AND entry_type = 'escrow_hold'""",
            (confirm_key,),
        ).fetchone()[0]
        settlement_count = connection.execute(
            """SELECT COUNT(*) FROM finance.ledger_entries
               WHERE metadata ->> 'checkout_id' = %s
                 AND entry_type = 'escrow_settlement'""",
            (checkout["checkout_id"],),
        ).fetchone()[0]
        events = {
            row[0]: row[1]
            for row in connection.execute(
                """SELECT routing_key, COUNT(*)
                   FROM audit.domain_events
                   WHERE aggregate_id IN (%s, %s)
                      OR payload -> 'payload' ->> 'checkout_id' = %s
                   GROUP BY routing_key""",
                (
                    checkout["checkout_id"],
                    checkout["order_id"],
                    checkout["checkout_id"],
                ),
            ).fetchall()
        }

        assert inventory == (
            Decimal("3.0000"),
            Decimal("0.0000"),
            Decimal("3.0000"),
        )
        assert wallet == (Decimal("80.00"), Decimal("20.00"))
        assert reservation_count == 1
        assert escrow_count == 1
        assert ledger_count == 1
        assert settlement_count == 0
        assert events.get("marketplace.checkout.started") == 1
        assert events.get("marketplace.order.created") == 1
        assert events.get("stock.reservation.created") == 1
        assert events.get("finance.payment.authorized") == 1
        assert events.get("stock.reservation.committed") == 1
        assert events.get("marketplace.checkout.confirmed") == 1

    with psycopg.connect(POSTGRES_DSN) as connection:
        with pytest.raises(psycopg.Error):
            connection.execute(
                """UPDATE marketplace.checkout_attempts
                   SET snapshot = jsonb_set(snapshot, '{tampered}', 'true'::jsonb)
                   WHERE id = %s""",
                (checkout["checkout_id"],),
            )
    store.close()


def test_price_divergence_and_wallet_failure_release_reservations() -> None:
    context = _context(wallet=Decimal("5.00"))
    store = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)

    with pytest.raises(MarketplaceCheckoutConflictError):
        _create_checkout(
            store,
            context=context,
            key=f"wrong-price-{uuid4()}",
            expected_total=Decimal("19.99"),
        )

    checkout = _create_checkout(
        store,
        context=context,
        key=f"payment-failure-{uuid4()}",
    )
    confirm_key = f"confirm-failure-{uuid4()}"
    correlation_id = uuid4()
    set_correlation_id(str(correlation_id))
    _audit_context(UUID(str(context["company_id"])))

    with pytest.raises(MarketplaceCheckoutPaymentError):
        store.confirm_checkout(
            checkout_id=str(checkout["checkout_id"]),
            user_id=str(context["buyer_id"]),
            payment_method="wallet",
            actor=str(context["buyer_id"]),
            idempotency_key=confirm_key,
            correlation_id=str(correlation_id),
            causation_id=str(checkout["checkout_id"]),
        )
    with pytest.raises(MarketplaceCheckoutPaymentError):
        store.confirm_checkout(
            checkout_id=str(checkout["checkout_id"]),
            user_id=str(context["buyer_id"]),
            payment_method="wallet",
            actor=str(context["buyer_id"]),
            idempotency_key=confirm_key,
            correlation_id=str(correlation_id),
            causation_id=str(checkout["checkout_id"]),
        )

    failed = store.get_checkout(
        checkout_id=str(checkout["checkout_id"]),
        user_id=str(context["buyer_id"]),
    )
    assert failed is not None
    assert failed["status"] == "payment_failed"
    assert failed["payment_status"] == "failed"

    with psycopg.connect(POSTGRES_DSN) as connection:
        inventory = connection.execute(
            """SELECT physical_quantity, reserved_quantity, available_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (context["inventory_id"],),
        ).fetchone()
        reservation = connection.execute(
            """SELECT status, release_reason FROM stock.stock_reservations
               WHERE order_id = %s""",
            (checkout["order_id"],),
        ).fetchone()
        order_status = connection.execute(
            "SELECT status FROM marketplace.orders WHERE id = %s",
            (checkout["order_id"],),
        ).fetchone()[0]
        escrow_count = connection.execute(
            """SELECT COUNT(*) FROM finance.escrows
               WHERE release_condition ->> 'checkout_id' = %s""",
            (checkout["checkout_id"],),
        ).fetchone()[0]
        ledger_count = connection.execute(
            """SELECT COUNT(*) FROM finance.ledger_entries
               WHERE idempotency_key = %s""",
            (confirm_key,),
        ).fetchone()[0]
        failed_events = connection.execute(
            """SELECT COUNT(*) FROM audit.domain_events
               WHERE routing_key = 'finance.payment.failed'
                 AND aggregate_id = %s""",
            (checkout["checkout_id"],),
        ).fetchone()[0]

        assert inventory == (
            Decimal("5.0000"),
            Decimal("0.0000"),
            Decimal("5.0000"),
        )
        assert reservation == ("released", "payment_failed")
        assert order_status == "cancelled"
        assert escrow_count == 0
        assert ledger_count == 0
        assert failed_events == 1
    store.close()


def test_concurrent_checkouts_never_oversell_and_cancel_is_idempotent() -> None:
    owner_id = uuid4()
    company_id = uuid4()
    store_id = uuid4()
    product_id = uuid4()
    sku = f"SKU-{uuid4().hex[:12]}"
    buyers = [uuid4(), uuid4()]

    with psycopg.connect(POSTGRES_DSN) as connection:
        _seed_user(connection, owner_id)
        for buyer_id in buyers:
            _seed_user(connection, buyer_id)
        _seed_company_store_product(
            connection,
            owner_id=owner_id,
            company_id=company_id,
            store_id=store_id,
            product_id=product_id,
            sku=sku,
        )
    _audit_context(company_id)
    inventory_id = _create_inventory(
        owner_id=owner_id,
        company_id=company_id,
        product_id=product_id,
        sku=sku,
        quantity=Decimal("1"),
    )
    contexts: list[dict[str, UUID | str]] = []
    for buyer_id in buyers:
        contexts.append(
            {
                "buyer_id": buyer_id,
                "company_id": company_id,
                "cart_id": _create_cart(
                    buyer_id=buyer_id,
                    product_id=product_id,
                    quantity=1,
                ),
            }
        )
        _create_wallet(buyer_id=buyer_id, available=Decimal("20.00"))

    def attempt(context: dict[str, UUID | str]) -> tuple[str, dict[str, object] | None]:
        worker = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
        try:
            correlation_id = uuid4()
            set_correlation_id(str(correlation_id))
            _audit_context(company_id)
            result = worker.create_checkout(
                user_id=str(context["buyer_id"]),
                cart_id=str(context["cart_id"]),
                currency="BRL",
                expected_total_brl=Decimal("10.00"),
                payment_method="wallet",
                actor=str(context["buyer_id"]),
                idempotency_key=f"concurrent-{uuid4()}",
                correlation_id=str(correlation_id),
                causation_id=None,
            )
            return "reserved", result
        except MarketplaceCheckoutConflictError:
            return "rejected", None
        finally:
            worker.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, contexts))

    assert sorted(status for status, _ in results) == ["rejected", "reserved"]
    winner = next(result for status, result in results if status == "reserved")
    assert winner is not None

    winner_store = MarketplaceCheckoutPostgresStore(POSTGRES_DSN)
    winner_context = next(
        context
        for context in contexts
        if str(context["buyer_id"]) == str(winner["user_id"])
    )
    correlation_id = uuid4()
    set_correlation_id(str(correlation_id))
    _audit_context(company_id)
    cancelled = winner_store.cancel_checkout(
        checkout_id=str(winner["checkout_id"]),
        user_id=str(winner_context["buyer_id"]),
        actor=str(winner_context["buyer_id"]),
        correlation_id=str(correlation_id),
        causation_id=str(winner["checkout_id"]),
    )
    cancelled_again = winner_store.cancel_checkout(
        checkout_id=str(winner["checkout_id"]),
        user_id=str(winner_context["buyer_id"]),
        actor=str(winner_context["buyer_id"]),
        correlation_id=str(correlation_id),
        causation_id=str(winner["checkout_id"]),
    )
    assert cancelled["status"] == "cancelled"
    assert cancelled_again["checkout_id"] == cancelled["checkout_id"]

    with psycopg.connect(POSTGRES_DSN) as connection:
        inventory = connection.execute(
            """SELECT physical_quantity, reserved_quantity, available_quantity
               FROM stock.inventory_items WHERE id = %s""",
            (inventory_id,),
        ).fetchone()
        checkout_count = connection.execute(
            """SELECT COUNT(*) FROM marketplace.checkout_attempts
               WHERE company_id = %s AND store_id = %s""",
            (company_id, store_id),
        ).fetchone()[0]
        cancel_events = connection.execute(
            """SELECT COUNT(*) FROM audit.domain_events
               WHERE routing_key = 'marketplace.checkout.cancelled'
                 AND aggregate_id = %s""",
            (winner["checkout_id"],),
        ).fetchone()[0]
        assert inventory == (
            Decimal("1.0000"),
            Decimal("0.0000"),
            Decimal("1.0000"),
        )
        assert checkout_count == 1
        assert cancel_events == 1
    winner_store.close()
