from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from psycopg.types.json import Jsonb

from .audit_contract import insert_postgres_audit
from .marketplace_checkout_approve import approve_checkout_payment
from .marketplace_checkout_base import (
    CHECKOUT_STATUSES_TERMINAL,
    CheckoutConflictError,
    CheckoutIdempotencyConflictError,
    MarketplaceCheckoutBase,
)
from .marketplace_checkout_release import release_checkout_payment


def apply_payment_result(
    store: MarketplaceCheckoutBase,
    *,
    checkout_id: str,
    outcome: Literal["approved", "rejected", "cancelled", "compensated"],
    actor: str,
    idempotency_key: str,
    correlation_id: str,
    provider_reference: str | None,
    reason: str | None,
) -> dict[str, Any]:
    request_payload = {
        "outcome": outcome,
        "provider_reference": provider_reference,
        "reason": reason,
    }
    request_hash = store.operation_hash(request_payload)
    with store.transaction() as connection:
        previous = connection.execute(
            """SELECT * FROM marketplace.checkout_operations
               WHERE checkout_id = %s AND operation_type = 'payment_result'
                 AND idempotency_key = %s FOR UPDATE""",
            (checkout_id, idempotency_key),
        ).fetchone()
        if previous is not None:
            if previous["request_hash"] != request_hash:
                raise CheckoutIdempotencyConflictError(
                    "Chave idempotente do resultado financeiro já foi "
                    "usada com outro corpo."
                )
            return dict(previous["result"])

        checkout, items = store._load_checkout_locked(connection, checkout_id)
        user_id = str(checkout["user_id"])
        company_id = str(checkout["company_id"])
        order_id = str(checkout["order_id"])
        if checkout["status"] in CHECKOUT_STATUSES_TERMINAL:
            current = store._checkout_view(checkout, items)
            connection.execute(
                """INSERT INTO marketplace.checkout_operations
                   (checkout_id, operation_type, idempotency_key, request_hash,
                    result, actor_user_id)
                   VALUES (%s, 'payment_result', %s, %s, %s, %s)""",
                (checkout_id, idempotency_key, request_hash, Jsonb(current), actor),
            )
            return current

        reservations = connection.execute(
            """SELECT * FROM stock.stock_reservations
               WHERE order_id = %s ORDER BY created_at, id FOR UPDATE""",
            (order_id,),
        ).fetchall()
        if not reservations:
            raise CheckoutConflictError("Checkout sem reservas Stock.")

        if outcome == "approved":
            if any(row["status"] != "reserved" for row in reservations):
                raise CheckoutConflictError(
                    "Todas as reservas devem estar ativas para aprovar."
                )
            if any(row["expires_at"] <= datetime.now(UTC) for row in reservations):
                raise CheckoutConflictError(
                    "Reserva expirada não pode ser aprovada."
                )
            updated_checkout = approve_checkout_payment(
                store,
                connection,
                checkout=checkout,
                reservations=list(reservations),
                actor=actor,
                idempotency_key=idempotency_key,
                correlation_id=correlation_id,
                provider_reference=provider_reference,
            )
        else:
            updated_checkout = release_checkout_payment(
                store,
                connection,
                checkout=checkout,
                reservations=list(reservations),
                outcome=outcome,
                actor=actor,
                idempotency_key=idempotency_key,
                correlation_id=correlation_id,
                reason=reason,
            )

        result = store._checkout_view(updated_checkout, items)
        insert_postgres_audit(
            connection,
            module="marketplace",
            actor_user_id=actor,
            action=f"payment_{outcome}",
            resource_type="checkouts",
            resource_id=checkout_id,
            before={"status": "pending_payment", "payment_status": "pending"},
            after=result,
            user_id=user_id,
            company_id=company_id,
        )
        connection.execute(
            """INSERT INTO marketplace.checkout_operations
               (checkout_id, operation_type, idempotency_key, request_hash,
                result, actor_user_id)
               VALUES (%s, 'payment_result', %s, %s, %s, %s)""",
            (checkout_id, idempotency_key, request_hash, Jsonb(result), actor),
        )
        return result
