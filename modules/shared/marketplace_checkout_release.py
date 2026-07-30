from __future__ import annotations

from typing import Any, Literal

from psycopg import Connection

from .audit_contract import insert_postgres_audit
from .marketplace_checkout_base import (
    CheckoutConflictError,
    CheckoutNotFoundError,
    MarketplaceCheckoutBase,
)
from .stock_postgres_store import StockPostgresStore


def release_checkout_payment(
    store: MarketplaceCheckoutBase,
    connection: Connection,
    *,
    checkout: dict[str, Any],
    reservations: list[dict[str, Any]],
    outcome: Literal["rejected", "cancelled", "compensated"],
    actor: str,
    idempotency_key: str,
    correlation_id: str,
    reason: str | None,
) -> dict[str, Any]:
    checkout_id = str(checkout["id"])
    order_id = str(checkout["order_id"])
    user_id = str(checkout["user_id"])
    company_id = str(checkout["company_id"])
    release_reason = reason or f"payment_{outcome}"

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
                "Saldo reservado inconsistente na liberação."
            )
        released = connection.execute(
            """UPDATE stock.stock_reservations
               SET status = 'released', released_at = NOW(),
                   release_reason = %s, updated_at = NOW(), updated_by = %s
               WHERE id = %s AND status = 'reserved' RETURNING *""",
            (release_reason, actor, reservation["id"]),
        ).fetchone()
        if released is None:
            raise CheckoutConflictError(
                "Reserva foi alterada concorrentemente na liberação."
            )
        insert_postgres_audit(
            connection,
            module="stock",
            actor_user_id=actor,
            action="release",
            resource_type="stock_reservations",
            resource_id=str(reservation["id"]),
            before=StockPostgresStore._reservation_view(reservation),
            after=StockPostgresStore._reservation_view(released),
            user_id=user_id,
            company_id=company_id,
        )
        store._emit_event(
            connection,
            module="stock",
            routing_key="stock.reservation.released",
            actor=actor,
            aggregate_type="stock_reservations",
            aggregate_id=str(reservation["id"]),
            user_id=user_id,
            company_id=company_id,
            status="released",
            payload={"checkout_id": checkout_id, "reason": release_reason},
            idempotency_key=reservation["idempotency_key"],
            correlation_id=correlation_id,
            causation_id=checkout_id,
        )

    status_map = {
        "rejected": ("payment_failed", "rejected"),
        "cancelled": ("cancelled", "cancelled"),
        "compensated": ("compensated", "compensated"),
    }
    checkout_status, payment_status = status_map[outcome]
    connection.execute(
        """UPDATE marketplace.orders
           SET status = 'cancelled', updated_at = NOW(), updated_by = %s
           WHERE id = %s""",
        (actor, order_id),
    )
    updated_checkout = connection.execute(
        """UPDATE marketplace.checkouts
           SET status = %s, payment_status = %s, failure_reason = %s,
               updated_at = NOW(), updated_by = %s
           WHERE id = %s RETURNING *""",
        (
            checkout_status,
            payment_status,
            release_reason,
            actor,
            checkout_id,
        ),
    ).fetchone()
    if updated_checkout is None:
        raise CheckoutNotFoundError("Checkout não encontrado durante liberação.")
    connection.execute(
        """UPDATE marketplace.carts
           SET status = 'active', updated_at = NOW(), updated_by = %s
           WHERE id = %s AND user_id = %s""",
        (actor, updated_checkout["cart_id"], user_id),
    )
    finance_routing_key = {
        "rejected": "finance.payment.failed",
        "cancelled": "finance.payment.cancelled",
        "compensated": "finance.payment.compensated",
    }[outcome]
    store._emit_event(
        connection,
        module="finance",
        routing_key=finance_routing_key,
        actor=actor,
        aggregate_type="checkouts",
        aggregate_id=checkout_id,
        user_id=user_id,
        company_id=company_id,
        status=payment_status,
        payload={"order_id": order_id, "reason": release_reason},
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        causation_id=checkout_id,
    )
    store._emit_event(
        connection,
        module="marketplace",
        routing_key="marketplace.checkout.cancelled",
        actor=actor,
        aggregate_type="checkouts",
        aggregate_id=checkout_id,
        user_id=user_id,
        company_id=company_id,
        status=checkout_status,
        payload={"order_id": order_id, "reason": release_reason},
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        causation_id=checkout_id,
    )
    return updated_checkout
