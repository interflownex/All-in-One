from __future__ import annotations

import os
from decimal import Decimal
from typing import Literal
from uuid import UUID

import psycopg
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
from .mercado_pago_checkout import (
    MercadoPagoAPIError,
    MercadoPagoClient,
    MercadoPagoConfigurationError,
    MercadoPagoSettings,
)
from .security import Actor, actor_from_headers


class MarketplaceCheckoutRequest(BaseModel):
    cart_id: UUID
    currency: Literal["BRL"] = "BRL"
    expected_total_brl: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    payment_method: Literal["wallet", "mercado_pago"] = "wallet"


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


def _recover_concurrent_checkout_creation(
    *,
    store: MarketplaceCheckoutPostgresStore,
    body: MarketplaceCheckoutRequest,
    user_id: str,
    idempotency_key: str,
) -> dict[str, object]:
    """Converte a disputa da restrição única em replay idempotente ou conflito."""

    previous = store.connection.execute(
        """SELECT * FROM marketplace.checkout_attempts
           WHERE user_id = %s AND idempotency_key = %s""",
        (user_id, idempotency_key),
    ).fetchone()
    if previous is None:
        raise HTTPException(
            status_code=409,
            detail="Disputa idempotente detectada sem operação recuperável.",
        )
    expected_hash = MarketplaceCheckoutPostgresStore.checkout_request_hash(
        cart_id=str(body.cart_id),
        currency=body.currency,
        expected_total_brl=body.expected_total_brl,
        payment_method=body.payment_method,
    )
    if previous["request_hash"] != expected_hash:
        raise HTTPException(
            status_code=409,
            detail="Chave idempotente já utilizada com outro corpo.",
        )
    return MarketplaceCheckoutPostgresStore._checkout_view(previous)


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
        except psycopg.errors.UniqueViolation:
            return _recover_concurrent_checkout_creation(
                store=store,
                body=body,
                user_id=str(actor.user_id),
                idempotency_key=x_idempotency_key,
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

    @app.post("/valley/checkout/{checkout_id}/mercadopago/preference")
    def create_mercado_pago_preference(
        checkout_id: UUID,
        actor: Actor = Depends(actor_from_headers),
        x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
    ) -> dict[str, object]:
        """Cria a preferência Checkout Pro sem expor o access token ao cliente."""
        set_correlation_id(str(x_correlation_id))
        try:
            settings = MercadoPagoSettings.from_environment()
        except MercadoPagoConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from None
        store = _checkout_store()
        try:
            checkout = store.get_checkout(checkout_id=str(checkout_id), user_id=str(actor.user_id))
            if checkout is None:
                raise HTTPException(status_code=404, detail="Checkout não encontrado.")
            if checkout["payment_method"] != "mercado_pago":
                raise HTTPException(status_code=409, detail="Checkout não configurado para Mercado Pago.")
            snapshot = checkout.get("snapshot") if isinstance(checkout.get("snapshot"), dict) else {}
            items = snapshot.get("items") if isinstance(snapshot.get("items"), list) else []
            title = str(items[0].get("name") if items and isinstance(items[0], dict) else "Compra Valley")
            preference = MercadoPagoClient(settings).create_preference(
                checkout_id=checkout["checkout_id"], order_id=checkout["order_id"],
                total_brl=Decimal(checkout["total_brl"]), title=title,
            )
            return {
                "checkout_id": checkout["checkout_id"],
                "provider": "mercado_pago",
                "preference_id": preference.get("id"),
                "init_point": preference.get("init_point"),
                "sandbox_init_point": preference.get("sandbox_init_point"),
            }
        except MercadoPagoAPIError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from None
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
        except psycopg.errors.UniqueViolation:
            raise HTTPException(
                status_code=409,
                detail="Chave idempotente de confirmação já utilizada em outro checkout.",
            ) from None
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
