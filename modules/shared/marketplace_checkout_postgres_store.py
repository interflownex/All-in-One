from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from .marketplace_checkout_base import (
    CheckoutConflictError,
    CheckoutIdempotencyConflictError,
    CheckoutNotFoundError,
    MarketplaceCheckoutBase,
)
from .marketplace_checkout_create import create_checkout
from .marketplace_checkout_expiration import expire_due_checkouts
from .marketplace_checkout_payment import apply_payment_result

__all__ = [
    "CheckoutConflictError",
    "CheckoutIdempotencyConflictError",
    "CheckoutNotFoundError",
    "MarketplaceCheckoutPostgresStore",
]


class MarketplaceCheckoutPostgresStore(MarketplaceCheckoutBase):
    """Orquestrador transacional Marketplace -> Stock -> Finance sem Delivery."""

    def create_checkout(
        self,
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
        return create_checkout(
            self,
            user_id=user_id,
            cart_id=cart_id,
            wallet_id=wallet_id,
            expected_total_brl=expected_total_brl,
            currency=currency,
            payment_method=payment_method,
            actor=actor,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            causation_id=causation_id,
            expires_in_seconds=expires_in_seconds,
        )

    def apply_payment_result(
        self,
        *,
        checkout_id: str,
        outcome: Literal["approved", "rejected", "cancelled", "compensated"],
        actor: str,
        idempotency_key: str,
        correlation_id: str,
        provider_reference: str | None,
        reason: str | None,
    ) -> dict[str, Any]:
        return apply_payment_result(
            self,
            checkout_id=checkout_id,
            outcome=outcome,
            actor=actor,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            provider_reference=provider_reference,
            reason=reason,
        )

    def expire_due_checkouts(
        self, *, actor: str, correlation_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        return expire_due_checkouts(
            self, actor=actor, correlation_id=correlation_id, limit=limit
        )
