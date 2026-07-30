from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from .marketplace_checkout_base import (
    CheckoutIdempotencyConflictError,
    MarketplaceCheckoutBase,
)
from .marketplace_checkout_persist import persist_checkout
from .marketplace_checkout_prepare import prepare_checkout_input


def create_checkout(
    store: MarketplaceCheckoutBase,
    *,
    user_id: str,
    cart_id: str,
    wallet_id: str,
    expected_total_brl: Decimal,
    currency: str,
    payment_method: str,
    actor: str,
    idempotency_key: str,
    correlation_id: str,
    causation_id: str | None,
    expires_in_seconds: int = 900,
) -> dict[str, Any]:
    request_hash = store.request_hash(
        cart_id=cart_id,
        currency=currency,
        expected_total_brl=expected_total_brl,
        wallet_id=wallet_id,
        payment_method=payment_method,
    )
    conflict: dict[str, str] | None = None
    try:
        with store.transaction() as connection:
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                (f"{user_id}:{idempotency_key}",),
            )
            previous = connection.execute(
                """SELECT * FROM marketplace.checkouts
                   WHERE user_id = %s AND idempotency_key = %s FOR UPDATE""",
                (user_id, idempotency_key),
            ).fetchone()
            if previous is not None:
                if previous["request_hash"] != request_hash:
                    conflict = {
                        "checkout_id": str(previous["id"]),
                        "company_id": str(previous["company_id"]),
                        "previous_hash": str(previous["request_hash"]),
                    }
                    raise CheckoutIdempotencyConflictError(
                        "Chave idempotente já usada pelo checkout "
                        f"{previous['id']} com outro corpo."
                    )
                item_rows = connection.execute(
                    """SELECT * FROM marketplace.checkout_items
                       WHERE checkout_id = %s ORDER BY created_at, id""",
                    (previous["id"],),
                ).fetchall()
                return store._checkout_view(
                    previous, [store._item_view(item) for item in item_rows]
                )

            prepared = prepare_checkout_input(
                store,
                connection,
                user_id=user_id,
                cart_id=cart_id,
                wallet_id=wallet_id,
                expected_total_brl=expected_total_brl,
                currency=currency,
                payment_method=payment_method,
            )
            checkout_id = str(uuid4())
            order_id = str(uuid4())
            expires_at = datetime.now(UTC) + timedelta(
                seconds=expires_in_seconds
            )
            return persist_checkout(
                store,
                connection,
                checkout_id=checkout_id,
                order_id=order_id,
                user_id=user_id,
                cart_id=cart_id,
                wallet_id=wallet_id,
                expected_total_brl=expected_total_brl,
                payment_method=payment_method,
                actor=actor,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                correlation_id=correlation_id,
                causation_id=causation_id,
                expires_at=expires_at,
                expires_in_seconds=expires_in_seconds,
                prepared_input=prepared,
            )
    except CheckoutIdempotencyConflictError:
        if conflict is not None:
            store.audit_external(
                actor,
                "idempotency_conflict",
                "checkouts",
                conflict["checkout_id"],
                {
                    "user_id": user_id,
                    "company_id": conflict["company_id"],
                    "request_hash": request_hash,
                    "previous_hash": conflict["previous_hash"],
                },
            )
        raise
