from __future__ import annotations

from typing import Any

from .audit_contract import insert_postgres_audit
from .marketplace_checkout_base import (
    CheckoutConflictError,
    MarketplaceCheckoutBase,
)
from .stock_postgres_store import StockPostgresStore


def expire_due_checkouts(
    self: MarketplaceCheckoutBase, *, actor: str, correlation_id: str, limit: int = 100
) -> list[dict[str, Any]]:
    expired: list[dict[str, Any]] = []
    with self.transaction() as connection:
        checkouts = connection.execute(
            """SELECT * FROM marketplace.checkouts
               WHERE status IN ('stock_reserved', 'pending_payment')
                 AND reservation_expires_at <= NOW()
               ORDER BY reservation_expires_at, id
               FOR UPDATE SKIP LOCKED LIMIT %s""",
            (limit,),
        ).fetchall()
        for checkout in checkouts:
            checkout_id = str(checkout["id"])
            order_id = str(checkout["order_id"])
            user_id = str(checkout["user_id"])
            company_id = str(checkout["company_id"])
            reservations = connection.execute(
                """SELECT * FROM stock.stock_reservations
                   WHERE order_id = %s ORDER BY created_at, id FOR UPDATE""",
                (order_id,),
            ).fetchall()
            for reservation in reservations:
                if reservation["status"] != "reserved":
                    continue
                quantity = reservation["quantity"]
                updated_inventory = connection.execute(
                    """UPDATE stock.inventory_items
                       SET reserved_quantity = reserved_quantity - %s,
                           version = version + 1, status = 'active',
                           updated_at = NOW(), updated_by = %s
                       WHERE id = %s AND reserved_quantity >= %s
                       RETURNING id""",
                    (quantity, actor, reservation["inventory_item_id"], quantity),
                ).fetchone()
                if updated_inventory is None:
                    raise CheckoutConflictError(
                        "Saldo reservado inconsistente durante expiração."
                    )
                released = connection.execute(
                    """UPDATE stock.stock_reservations
                       SET status = 'expired', released_at = NOW(),
                           release_reason = 'reservation_expired',
                           updated_at = NOW(), updated_by = %s
                       WHERE id = %s AND status = 'reserved' RETURNING *""",
                    (actor, reservation["id"]),
                ).fetchone()
                self._emit_event(
                    connection,
                    module="stock",
                    routing_key="stock.reservation.expired",
                    actor=actor,
                    aggregate_type="stock_reservations",
                    aggregate_id=str(reservation["id"]),
                    user_id=user_id,
                    company_id=company_id,
                    status="expired",
                    payload={"checkout_id": checkout_id, "order_id": order_id},
                    idempotency_key=reservation["idempotency_key"],
                    correlation_id=correlation_id,
                    causation_id=checkout_id,
                )
                insert_postgres_audit(
                    connection,
                    module="stock",
                    actor_user_id=actor,
                    action="expire",
                    resource_type="stock_reservations",
                    resource_id=str(reservation["id"]),
                    before=StockPostgresStore._reservation_view(reservation),
                    after=StockPostgresStore._reservation_view(released),
                    user_id=user_id,
                    company_id=company_id,
                )
            connection.execute(
                """UPDATE marketplace.orders
                   SET status = 'cancelled', updated_at = NOW(),
                       updated_by = %s
                   WHERE id = %s""",
                (actor, order_id),
            )
            updated = connection.execute(
                """UPDATE marketplace.checkouts
                   SET status = 'expired', payment_status = 'cancelled',
                       failure_reason = 'reservation_expired',
                       updated_at = NOW(), updated_by = %s
                   WHERE id = %s RETURNING *""",
                (actor, checkout_id),
            ).fetchone()
            connection.execute(
                """UPDATE marketplace.carts
                   SET status = 'active', updated_at = NOW(), updated_by = %s
                   WHERE id = %s AND user_id = %s""",
                (actor, checkout["cart_id"], user_id),
            )
            item_rows = connection.execute(
                """SELECT * FROM marketplace.checkout_items
                   WHERE checkout_id = %s ORDER BY created_at, id""",
                (checkout_id,),
            ).fetchall()
            view = self._checkout_view(
                updated, [self._item_view(item) for item in item_rows]
            )
            self._emit_event(
                connection,
                module="marketplace",
                routing_key="marketplace.checkout.expired",
                actor=actor,
                aggregate_type="checkouts",
                aggregate_id=checkout_id,
                user_id=user_id,
                company_id=company_id,
                status="expired",
                payload={"order_id": order_id},
                idempotency_key=f"expire:{checkout_id}",
                correlation_id=correlation_id,
                causation_id=checkout_id,
            )
            expired.append(view)
    return expired
