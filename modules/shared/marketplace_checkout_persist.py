from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb

from .audit_contract import insert_postgres_audit
from .marketplace_checkout_base import (
    CheckoutConflictError,
    MarketplaceCheckoutBase,
)
from .stock_postgres_store import StockPostgresStore


def persist_checkout(
    store: MarketplaceCheckoutBase,
    connection: Connection,
    *,
    checkout_id: str,
    order_id: str,
    user_id: str,
    cart_id: str,
    wallet_id: str,
    expected_total_brl: Decimal,
    payment_method: str,
    actor: str,
    idempotency_key: str,
    request_hash: str,
    correlation_id: str,
    causation_id: str | None,
    expires_at: datetime,
    expires_in_seconds: int,
    prepared_input: dict[str, Any],
) -> dict[str, Any]:
    company_id = str(prepared_input["company_id"])
    store_id = str(prepared_input["store_id"])
    total = Decimal(str(prepared_input["total"]))
    prepared = list(prepared_input["prepared"])
    snapshot = {
        "version": "1.0.0",
        "cart_id": cart_id,
        "order_id": order_id,
        "user_id": user_id,
        "company_id": company_id,
        "store_id": store_id,
        "wallet_id": wallet_id,
        "currency": "BRL",
        "total_brl": store._decimal_text(total),
        "payment_method": payment_method,
        "items": prepared_input["snapshot_items"],
        "created_at": datetime.now(UTC).isoformat(),
    }

    connection.execute(
        """INSERT INTO marketplace.orders
           (id, user_id, store_id, total_brl, commission_brl, status, metadata,
            created_by, updated_by, idempotency_key, company_id)
           VALUES (%s, %s, %s, %s, 0, 'pending_payment', %s, %s, %s, %s, %s)""",
        (
            order_id,
            user_id,
            store_id,
            total,
            Jsonb({"runtime_payload": snapshot}),
            actor,
            actor,
            f"checkout-order:{request_hash}",
            company_id,
        ),
    )
    checkout_row = connection.execute(
        """INSERT INTO marketplace.checkouts
           (id, user_id, company_id, cart_id, order_id, store_id, wallet_id,
            status, payment_status, currency, expected_total_brl, total_brl,
            idempotency_key, request_hash, correlation_id, causation_id,
            snapshot, reservation_expires_at, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending_stock_reservation',
                   'pending', 'BRL', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
           RETURNING *""",
        (
            checkout_id,
            user_id,
            company_id,
            cart_id,
            order_id,
            store_id,
            wallet_id,
            store._money(expected_total_brl),
            total,
            idempotency_key,
            request_hash,
            correlation_id,
            causation_id,
            Jsonb(snapshot),
            expires_at,
            actor,
            actor,
        ),
    ).fetchone()

    checkout_item_rows: list[dict[str, Any]] = []
    for index, item in enumerate(prepared):
        reservation_id = str(uuid4())
        reservation_key = f"{idempotency_key}:item:{index}"
        reservation_hash = StockPostgresStore.reservation_request_hash(
            inventory_item_id=item["inventory_item_id"],
            order_id=order_id,
            quantity=item["quantity"],
            expires_in_seconds=expires_in_seconds,
        )
        updated_inventory = connection.execute(
            """UPDATE stock.inventory_items
               SET reserved_quantity = reserved_quantity + %s,
                   version = version + 1,
                   status = CASE
                       WHEN physical_quantity = reserved_quantity + %s
                       THEN 'depleted' ELSE 'active' END,
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s AND company_id = %s
                 AND physical_quantity - reserved_quantity >= %s
               RETURNING id""",
            (
                item["quantity"],
                item["quantity"],
                actor,
                item["inventory_item_id"],
                company_id,
                item["quantity"],
            ),
        ).fetchone()
        if updated_inventory is None:
            raise CheckoutConflictError("Estoque alterado concorrentemente.")

        reservation = connection.execute(
            """INSERT INTO stock.stock_reservations
               (id, user_id, company_id, order_id, inventory_item_id, quantity,
                status, idempotency_key, request_hash, correlation_id,
                causation_id, expires_at, metadata, created_by, updated_by)
               VALUES (%s, %s, %s, %s, %s, %s, 'reserved', %s, %s, %s, %s,
                       %s, %s, %s, %s)
               RETURNING *""",
            (
                reservation_id,
                user_id,
                company_id,
                order_id,
                item["inventory_item_id"],
                item["quantity"],
                reservation_key,
                reservation_hash,
                correlation_id,
                causation_id,
                expires_at,
                Jsonb(
                    {
                        "checkout_id": checkout_id,
                        "product_id": item["product_id"],
                    }
                ),
                actor,
                actor,
            ),
        ).fetchone()
        checkout_item = connection.execute(
            """INSERT INTO marketplace.checkout_items
               (checkout_id, product_id, store_id, company_id,
                inventory_item_id, reservation_id, sku, product_name,
                quantity, unit_price_brl, subtotal_brl, currency,
                promotion_snapshot, catalog_version)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       'BRL', %s, %s)
               RETURNING *""",
            (
                checkout_id,
                item["product_id"],
                item["store_id"],
                company_id,
                item["inventory_item_id"],
                reservation_id,
                item["sku"],
                item["name"],
                item["quantity"],
                item["unit_price_brl"],
                item["subtotal_brl"],
                Jsonb(item["promotion"]),
                item["catalog_version"],
            ),
        ).fetchone()
        checkout_item_rows.append(checkout_item)
        insert_postgres_audit(
            connection,
            module="stock",
            actor_user_id=actor,
            action="reserve",
            resource_type="stock_reservations",
            resource_id=reservation_id,
            before=None,
            after=StockPostgresStore._reservation_view(reservation),
            user_id=user_id,
            company_id=company_id,
        )
        store._emit_event(
            connection,
            module="stock",
            routing_key="stock.reservation.created",
            actor=actor,
            aggregate_type="stock_reservations",
            aggregate_id=reservation_id,
            user_id=user_id,
            company_id=company_id,
            status="reserved",
            payload={
                "checkout_id": checkout_id,
                "order_id": order_id,
                "inventory_item_id": item["inventory_item_id"],
                "quantity": store._decimal_text(item["quantity"]),
                "expires_at": expires_at.isoformat(),
            },
            idempotency_key=reservation_key,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )

    checkout_row = connection.execute(
        """UPDATE marketplace.checkouts
           SET status = 'pending_payment', updated_at = NOW(), updated_by = %s
           WHERE id = %s RETURNING *""",
        (actor, checkout_id),
    ).fetchone()
    connection.execute(
        """UPDATE marketplace.carts
           SET status = 'checkout_pending', updated_at = NOW(), updated_by = %s
           WHERE id = %s AND user_id = %s AND status = 'active'""",
        (actor, cart_id, user_id),
    )
    view = store._checkout_view(
        checkout_row, [store._item_view(item) for item in checkout_item_rows]
    )
    insert_postgres_audit(
        connection,
        module="marketplace",
        actor_user_id=actor,
        action="create_checkout",
        resource_type="checkouts",
        resource_id=checkout_id,
        before=None,
        after=view,
        user_id=user_id,
        company_id=company_id,
    )
    for module, routing_key, aggregate_type, aggregate_id, payload in (
        (
            "marketplace",
            "marketplace.checkout.started",
            "checkouts",
            checkout_id,
            {"order_id": order_id, "total_brl": store._decimal_text(total)},
        ),
        (
            "marketplace",
            "marketplace.order.created",
            "orders",
            order_id,
            {"checkout_id": checkout_id, "total_brl": store._decimal_text(total)},
        ),
        (
            "finance",
            "finance.payment.pending",
            "checkouts",
            checkout_id,
            {
                "order_id": order_id,
                "wallet_id": wallet_id,
                "total_brl": store._decimal_text(total),
            },
        ),
    ):
        store._emit_event(
            connection,
            module=module,
            routing_key=routing_key,
            actor=actor,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            user_id=user_id,
            company_id=company_id,
            status="pending_payment" if module == "marketplace" else "pending",
            payload=payload,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            causation_id=causation_id or checkout_id,
        )
    return view
