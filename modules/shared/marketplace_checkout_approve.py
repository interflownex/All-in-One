from __future__ import annotations

from typing import Any
from uuid import uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb

from .audit_contract import insert_postgres_audit
from .marketplace_checkout_base import (
    CheckoutConflictError,
    CheckoutNotFoundError,
    MarketplaceCheckoutBase,
)
from .stock_postgres_store import StockPostgresStore


def approve_checkout_payment(
    store: MarketplaceCheckoutBase,
    connection: Connection,
    *,
    checkout: dict[str, Any],
    reservations: list[dict[str, Any]],
    actor: str,
    idempotency_key: str,
    correlation_id: str,
    provider_reference: str | None,
) -> dict[str, Any]:
    checkout_id = str(checkout["id"])
    order_id = str(checkout["order_id"])
    user_id = str(checkout["user_id"])
    company_id = str(checkout["company_id"])
    ledger_id = str(uuid4())

    connection.execute(
        """INSERT INTO finance.ledger_entries
           (id, user_id, wallet_id, currency, amount_brl, entry_type,
            reference_type, reference_id, idempotency_key, status,
            metadata, created_by)
           VALUES (%s, %s, %s, 'BRL', %s, 'marketplace_purchase_authorized',
                   'marketplace.checkout', %s, %s, 'posted', %s, %s)""",
        (
            ledger_id,
            user_id,
            checkout["wallet_id"],
            -checkout["total_brl"],
            checkout_id,
            f"checkout-payment:{checkout_id}:{idempotency_key}",
            Jsonb(
                {
                    "order_id": order_id,
                    "company_id": company_id,
                    "provider_reference": provider_reference,
                    "correlation_id": correlation_id,
                }
            ),
            actor,
        ),
    )

    for reservation in reservations:
        inventory = connection.execute(
            "SELECT * FROM stock.inventory_items WHERE id = %s FOR UPDATE",
            (reservation["inventory_item_id"],),
        ).fetchone()
        if inventory is None:
            raise CheckoutNotFoundError("Inventário da reserva não encontrado.")
        quantity = reservation["quantity"]
        updated_inventory = connection.execute(
            """UPDATE stock.inventory_items
               SET physical_quantity = physical_quantity - %s,
                   reserved_quantity = reserved_quantity - %s,
                   version = version + 1,
                   status = CASE WHEN physical_quantity - %s = 0
                                 THEN 'depleted' ELSE 'active' END,
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s AND physical_quantity >= %s
                 AND reserved_quantity >= %s
               RETURNING id""",
            (
                quantity,
                quantity,
                quantity,
                actor,
                inventory["id"],
                quantity,
                quantity,
            ),
        ).fetchone()
        if updated_inventory is None:
            raise CheckoutConflictError("Saldo reservado inconsistente.")
        committed = connection.execute(
            """UPDATE stock.stock_reservations
               SET status = 'committed', committed_at = NOW(),
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s AND status = 'reserved' RETURNING *""",
            (actor, reservation["id"]),
        ).fetchone()
        if committed is None:
            raise CheckoutConflictError(
                "Reserva foi alterada concorrentemente antes da confirmação."
            )
        insert_postgres_audit(
            connection,
            module="stock",
            actor_user_id=actor,
            action="commit",
            resource_type="stock_reservations",
            resource_id=str(reservation["id"]),
            before=StockPostgresStore._reservation_view(reservation),
            after=StockPostgresStore._reservation_view(committed),
            user_id=user_id,
            company_id=company_id,
        )
        store._emit_event(
            connection,
            module="stock",
            routing_key="stock.reservation.committed",
            actor=actor,
            aggregate_type="stock_reservations",
            aggregate_id=str(reservation["id"]),
            user_id=user_id,
            company_id=company_id,
            status="committed",
            payload={"checkout_id": checkout_id, "order_id": order_id},
            idempotency_key=reservation["idempotency_key"],
            correlation_id=correlation_id,
            causation_id=checkout_id,
        )

    insert_postgres_audit(
        connection,
        module="finance",
        actor_user_id=actor,
        action="ledger_post",
        resource_type="ledger_entries",
        resource_id=ledger_id,
        before=None,
        after={
            "checkout_id": checkout_id,
            "order_id": order_id,
            "currency": "BRL",
            "amount_brl": store._decimal_text(-checkout["total_brl"]),
            "entry_type": "marketplace_purchase_authorized",
        },
        user_id=user_id,
        company_id=company_id,
    )
    connection.execute(
        """UPDATE marketplace.orders
           SET status = 'paid',
               metadata = jsonb_set(
                   metadata, '{runtime_payload,payment_status}',
                   '"authorized"'::jsonb, true),
               updated_at = NOW(), updated_by = %s
           WHERE id = %s""",
        (actor, order_id),
    )
    updated_checkout = connection.execute(
        """UPDATE marketplace.checkouts
           SET status = 'confirmed', payment_status = 'authorized',
               failure_reason = NULL, updated_at = NOW(), updated_by = %s
           WHERE id = %s RETURNING *""",
        (actor, checkout_id),
    ).fetchone()
    if updated_checkout is None:
        raise CheckoutNotFoundError("Checkout não encontrado durante confirmação.")
    connection.execute(
        """UPDATE marketplace.carts
           SET status = 'converted', updated_at = NOW(), updated_by = %s
           WHERE id = %s AND user_id = %s""",
        (actor, updated_checkout["cart_id"], user_id),
    )
    store._emit_event(
        connection,
        module="finance",
        routing_key="finance.payment.authorized",
        actor=actor,
        aggregate_type="ledger_entries",
        aggregate_id=ledger_id,
        user_id=user_id,
        company_id=company_id,
        status="posted",
        payload={
            "checkout_id": checkout_id,
            "order_id": order_id,
            "total_brl": store._decimal_text(updated_checkout["total_brl"]),
        },
        idempotency_key=f"checkout-payment:{checkout_id}:{idempotency_key}",
        correlation_id=correlation_id,
        causation_id=checkout_id,
    )
    store._emit_event(
        connection,
        module="marketplace",
        routing_key="marketplace.checkout.confirmed",
        actor=actor,
        aggregate_type="checkouts",
        aggregate_id=checkout_id,
        user_id=user_id,
        company_id=company_id,
        status="confirmed",
        payload={"order_id": order_id, "ledger_entry_id": ledger_id},
        idempotency_key=idempotency_key,
        correlation_id=correlation_id,
        causation_id=ledger_id,
    )
    return updated_checkout
