from __future__ import annotations

import os
from decimal import Decimal
from typing import Literal
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .correlation import set_correlation_id
from .marketplace_checkout_postgres_store import (
    MarketplaceCheckoutConflictError,
    MarketplaceCheckoutError,
    MarketplaceCheckoutIdempotencyConflictError,
    MarketplaceCheckoutNotFoundError,
    MarketplaceCheckoutPaymentError,
    MarketplaceCheckoutPostgresStore,
)
from .security import Actor, actor_from_headers


class MarketplaceCheckoutRequest(BaseModel):
    cart_id: UUID
    currency: Literal["BRL"] = "BRL"
    expected_total_brl: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    payment_method: Literal["wallet"] = "wallet"


class MarketplaceCheckoutConfirmationRequest(BaseModel):
    payment_method: Literal["wallet"] = "wallet"


def _checkout_enabled() -> bool:
    value = os.getenv("MARKETPLACE_CHECKOUT_V1_ENABLED", "false")
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _checkout_store() -> MarketplaceCheckoutPostgresStore:
    dsn = os.getenv("ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN")
    if not dsn:
        raise HTTPException(
            status_code=503,
            detail="DSN PostgreSQL do Marketplace ausente para o checkout.",
        )
    return MarketplaceCheckoutPostgresStore(dsn)


def _raise_http_checkout_error(exc: MarketplaceCheckoutError) -> None:
    if isinstance(exc, MarketplaceCheckoutNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from None
    if isinstance(
        exc,
        (
            MarketplaceCheckoutConflictError,
            MarketplaceCheckoutIdempotencyConflictError,
            MarketplaceCheckoutPaymentError,
        ),
    ):
        raise HTTPException(status_code=409, detail=str(exc)) from None
    raise HTTPException(status_code=500, detail="Falha transacional no checkout.") from None


def register_marketplace_checkout_routes(app: FastAPI) -> None:
    """Registra o checkout especializado uma única vez no aplicativo Marketplace."""

    if getattr(app.state, "marketplace_checkout_routes_registered", False):
        return
    app.state.marketplace_checkout_routes_registered = True

    @app.post("/valley/checkout", status_code=201)
    def create_marketplace_checkout(
        body: MarketplaceCheckoutRequest,
        actor: Actor = Depends(actor_from_headers),
        x_idempotency_key: str = Header(
            ...,
            alias="X-Idempotency-Key",
            min_length=16,
            max_length=160,
        ),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
        x_causation_id: UUID | None = Header(default=None, alias="X-Causation-Id"),
    ) -> dict[str, object]:
        if not _checkout_enabled():
            raise HTTPException(
                status_code=503,
                detail="Checkout desativado por feature flag até homologação.",
            )
        set_correlation_id(str(x_correlation_id))
        store = _checkout_store()
        try:
            return store.create_checkout(
                user_id=str(actor.user_id),
                cart_id=str(body.cart_id),
                currency=body.currency,
                expected_total_brl=body.expected_total_brl,
                payment_method=body.payment_method,
                actor=str(actor.user_id),
                idempotency_key=x_idempotency_key,
                correlation_id=str(x_correlation_id),
                causation_id=str(x_causation_id) if x_causation_id else None,
            )
        except MarketplaceCheckoutError as exc:
            _raise_http_checkout_error(exc)
        finally:
            store.close()

    @app.get("/valley/checkout/{checkout_id}")
    def get_marketplace_checkout(
        checkout_id: UUID,
        actor: Actor = Depends(actor_from_headers),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
    ) -> dict[str, object]:
        set_correlation_id(str(x_correlation_id))
        store = _checkout_store()
        try:
            checkout = store.get_checkout(
                checkout_id=str(checkout_id), user_id=str(actor.user_id)
            )
            if checkout is None:
                raise HTTPException(status_code=404, detail="Checkout não encontrado.")
            return checkout
        finally:
            store.close()

    @app.post("/valley/checkout/{checkout_id}/confirm")
    def confirm_marketplace_checkout(
        checkout_id: UUID,
        body: MarketplaceCheckoutConfirmationRequest,
        actor: Actor = Depends(actor_from_headers),
        x_idempotency_key: str = Header(
            ...,
            alias="X-Idempotency-Key",
            min_length=16,
            max_length=160,
        ),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
        x_causation_id: UUID | None = Header(default=None, alias="X-Causation-Id"),
    ) -> dict[str, object]:
        set_correlation_id(str(x_correlation_id))
        store = _checkout_store()
        try:
            return store.confirm_checkout(
                checkout_id=str(checkout_id),
                user_id=str(actor.user_id),
                payment_method=body.payment_method,
                actor=str(actor.user_id),
                idempotency_key=x_idempotency_key,
                correlation_id=str(x_correlation_id),
                causation_id=str(x_causation_id) if x_causation_id else None,
            )
        except MarketplaceCheckoutError as exc:
            _raise_http_checkout_error(exc)
        finally:
            store.close()

    @app.post("/valley/checkout/{checkout_id}/cancel")
    def cancel_marketplace_checkout(
        checkout_id: UUID,
        actor: Actor = Depends(actor_from_headers),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
        x_causation_id: UUID | None = Header(default=None, alias="X-Causation-Id"),
    ) -> dict[str, object]:
        set_correlation_id(str(x_correlation_id))
        store = _checkout_store()
        try:
            return store.cancel_checkout(
                checkout_id=str(checkout_id),
                user_id=str(actor.user_id),
                actor=str(actor.user_id),
                correlation_id=str(x_correlation_id),
                causation_id=str(x_causation_id) if x_causation_id else None,
            )
        except MarketplaceCheckoutError as exc:
            _raise_http_checkout_error(exc)
        finally:
            store.close()
