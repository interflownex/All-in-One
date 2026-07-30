from __future__ import annotations

import os
from decimal import Decimal
from functools import lru_cache
from typing import Any, Literal
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from shared.marketplace_checkout_postgres_store import (
    CheckoutConflictError,
    CheckoutIdempotencyConflictError,
    CheckoutNotFoundError,
    MarketplaceCheckoutPostgresStore,
)
from shared.runtime import bind_correlation_id, get_config
from shared.security import Actor, actor_from_headers

CHECKOUT_OPERATOR_ROLES = frozenset(
    {"owner", "administrator", "merchant", "store_manager", "auditor"}
)


class CheckoutConfirmRequest(BaseModel):
    cart_id: UUID
    wallet_id: UUID
    currency: Literal["BRL"] = "BRL"
    expected_total_brl: Decimal = Field(ge=0, max_digits=18, decimal_places=4)
    payment_method: Literal["wallet"] = "wallet"
    reservation_ttl_seconds: int = Field(default=900, ge=60, le=3600)


class CheckoutPaymentResultRequest(BaseModel):
    outcome: Literal["approved", "rejected", "cancelled", "compensated"]
    provider_reference: str | None = Field(default=None, max_length=200)
    reason: str | None = Field(default=None, max_length=500)


def _flag_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().casefold() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def checkout_store() -> MarketplaceCheckoutPostgresStore:
    dsn = get_config("ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN")
    if not dsn:
        raise HTTPException(
            status_code=503,
            detail=(
                "Checkout exige ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN configurado "
                "fora do Git."
            ),
        )
    return MarketplaceCheckoutPostgresStore(str(dsn))


def _require_checkout_enabled() -> None:
    if not _flag_enabled("MARKETPLACE_CHECKOUT_V1_ENABLED"):
        raise HTTPException(
            status_code=503,
            detail="Checkout V1 permanece desligado até homologação.",
        )


def _require_idempotency_key(value: str) -> str:
    normalized = value.strip()
    if not 16 <= len(normalized) <= 120:
        raise HTTPException(
            status_code=422,
            detail="X-Idempotency-Key deve possuir entre 16 e 120 caracteres.",
        )
    return normalized


def _translate_checkout_error(error: Exception) -> None:
    if isinstance(error, CheckoutNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from None
    if isinstance(
        error,
        (CheckoutConflictError, CheckoutIdempotencyConflictError),
    ):
        raise HTTPException(status_code=409, detail=str(error)) from None
    raise error


def _authorize_checkout_read(actor: Actor, checkout: dict[str, Any]) -> None:
    if str(actor.user_id) == checkout["user_id"]:
        return
    if (
        actor.roles.intersection(CHECKOUT_OPERATOR_ROLES)
        and actor.business_id is not None
        and str(actor.business_id) == checkout["company_id"]
    ):
        return
    raise HTTPException(
        status_code=403,
        detail="Checkout não pertence ao usuário ou empresa autenticada.",
    )


def _require_scope(actor: Actor, scope: str) -> None:
    if scope not in actor.scopes:
        raise HTTPException(status_code=403, detail=f"Escopo {scope} obrigatório.")


def register_checkout_routes(app: FastAPI) -> None:
    @app.post("/valley/checkout", status_code=201)
    def confirm_checkout(
        body: CheckoutConfirmRequest,
        actor: Actor = Depends(actor_from_headers),
        x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
        x_causation_id: UUID | None = Header(default=None, alias="X-Causation-Id"),
    ) -> dict[str, Any]:
        _require_checkout_enabled()
        idempotency_key = _require_idempotency_key(x_idempotency_key)
        bind_correlation_id(x_correlation_id)
        try:
            return checkout_store().create_checkout(
                user_id=str(actor.user_id),
                cart_id=str(body.cart_id),
                wallet_id=str(body.wallet_id),
                expected_total_brl=body.expected_total_brl,
                currency=body.currency,
                payment_method=body.payment_method,
                actor=str(actor.user_id),
                idempotency_key=idempotency_key,
                correlation_id=str(x_correlation_id),
                causation_id=str(x_causation_id) if x_causation_id else None,
                expires_in_seconds=body.reservation_ttl_seconds,
            )
        except Exception as exc:
            _translate_checkout_error(exc)
            raise

    @app.get("/valley/checkout/{checkout_id}")
    def get_checkout(
        checkout_id: UUID,
        actor: Actor = Depends(actor_from_headers),
    ) -> dict[str, Any]:
        checkout = checkout_store().get_checkout(str(checkout_id))
        if checkout is None:
            raise HTTPException(status_code=404, detail="Checkout não encontrado.")
        _authorize_checkout_read(actor, checkout)
        return checkout

    @app.post("/valley/checkout/{checkout_id}/payment-result")
    def apply_payment_result(
        checkout_id: UUID,
        body: CheckoutPaymentResultRequest,
        actor: Actor = Depends(actor_from_headers),
        x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
    ) -> dict[str, Any]:
        _require_scope(actor, "marketplace:checkout:payment")
        idempotency_key = _require_idempotency_key(x_idempotency_key)
        bind_correlation_id(x_correlation_id)
        try:
            return checkout_store().apply_payment_result(
                checkout_id=str(checkout_id),
                outcome=body.outcome,
                actor=str(actor.user_id),
                idempotency_key=idempotency_key,
                correlation_id=str(x_correlation_id),
                provider_reference=body.provider_reference,
                reason=body.reason,
            )
        except Exception as exc:
            _translate_checkout_error(exc)
            raise

    @app.post("/valley/checkout/expire")
    def expire_checkouts(
        limit: int = Query(default=100, ge=1, le=500),
        actor: Actor = Depends(actor_from_headers),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
    ) -> dict[str, Any]:
        _require_scope(actor, "marketplace:checkout:expire")
        bind_correlation_id(x_correlation_id)
        try:
            expired = checkout_store().expire_due_checkouts(
                actor=str(actor.user_id),
                correlation_id=str(x_correlation_id),
                limit=limit,
            )
        except Exception as exc:
            _translate_checkout_error(exc)
            raise
        return {"expired_count": len(expired), "checkouts": expired}
