import sys
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from shared.runtime import bind_correlation_id, create_module_app, get_config
from shared.security import Actor, actor_from_headers, demand_active_business
from shared.stock_postgres_store import (
    StockConflictError,
    StockIdempotencyConflictError,
    StockNotFoundError,
    StockPostgresStore,
)
from shared.store import DuplicateValueError
from shared.units_tax import ConversionRule, convert_quantity

app = create_module_app("stock", version="0.3.0")

STOCK_OPERATOR_ROLES = frozenset(
    {"owner", "administrator", "merchant", "store_manager", "stock_manager", "auditor"}
)


class UnitConversionRequest(BaseModel):
    quantity: str = Field(min_length=1, max_length=80)
    multiplier: str = Field(min_length=1, max_length=80)
    divisor: str = Field(min_length=1, max_length=80)
    precision: int = Field(ge=0, le=12)
    rounding_mode: str
    source_dimension: str = Field(min_length=1, max_length=40)
    target_dimension: str = Field(min_length=1, max_length=40)
    effective_from: datetime
    effective_to: datetime | None = None
    approved: bool
    density: str | None = Field(default=None, max_length=80)


class InventoryItemCreate(BaseModel):
    user_id: UUID
    company_id: UUID
    warehouse_id: UUID | None = None
    product_id: UUID
    sku: str = Field(min_length=1, max_length=120)
    physical_quantity: Decimal = Field(ge=0, max_digits=18, decimal_places=4)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InventoryAdjustment(BaseModel):
    expected_version: int = Field(ge=0)
    physical_quantity: Decimal = Field(ge=0, max_digits=18, decimal_places=4)
    reason: str = Field(min_length=3, max_length=500)


class ReservationCreate(BaseModel):
    user_id: UUID
    company_id: UUID
    inventory_item_id: UUID
    order_id: UUID
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=4)
    expires_in_seconds: int = Field(default=900, ge=60, le=3600)


class ReservationRelease(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


@lru_cache(maxsize=1)
def reservation_store() -> StockPostgresStore:
    dsn = get_config("ALL_IN_ONE_STOCK_POSTGRES_DSN")
    if not dsn:
        raise HTTPException(
            status_code=503,
            detail="Reservas do Stock exigem ALL_IN_ONE_STOCK_POSTGRES_DSN configurado fora do Git.",
        )
    return StockPostgresStore(str(dsn))


def _authorize_subject_or_operator(actor: Actor, user_id: UUID) -> None:
    if actor.user_id == user_id or actor.roles.intersection(STOCK_OPERATOR_ROLES):
        return
    raise HTTPException(status_code=403, detail="Ator não autorizado para esta reserva.")


def _authorize_inventory_company(actor: Actor, company_id: UUID) -> None:
    demand_active_business(actor, "gerenciar inventário")
    if actor.business_id != company_id:
        raise HTTPException(
            status_code=403,
            detail="Inventário deve pertencer à empresa Business autenticada.",
        )


def _translate_stock_error(error: Exception) -> None:
    if isinstance(error, StockNotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from None
    if isinstance(error, (StockConflictError, StockIdempotencyConflictError)):
        raise HTTPException(status_code=409, detail=str(error)) from None
    if isinstance(error, DuplicateValueError):
        raise HTTPException(status_code=409, detail="Item de inventário já cadastrado.") from None
    raise error


@app.post("/calculations/unit-conversion")
def calculate_unit_conversion(
    body: UnitConversionRequest,
    x_actor_user_id: str = Header(..., alias="X-Actor-User-Id"),
) -> dict[str, str]:
    """Converte quantidade no backend sem usar ponto flutuante binário."""
    try:
        result = convert_quantity(
            body.quantity,
            ConversionRule(**body.model_dump(exclude={"quantity"})),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return {
        "quantity": body.quantity,
        "converted_quantity": format(result, "f"),
        "rounding_mode": body.rounding_mode,
        "calculated_by": x_actor_user_id,
    }


@app.post("/inventory/items", status_code=201)
def create_inventory_item(
    body: InventoryItemCreate,
    actor: Actor = Depends(actor_from_headers),
    x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
) -> dict[str, Any]:
    _authorize_inventory_company(actor, body.company_id)
    bind_correlation_id(x_correlation_id)
    try:
        return reservation_store().create_inventory_item(
            user_id=str(body.user_id),
            company_id=str(body.company_id),
            warehouse_id=str(body.warehouse_id) if body.warehouse_id else None,
            product_id=str(body.product_id),
            sku=body.sku.strip(),
            physical_quantity=body.physical_quantity,
            actor=str(actor.user_id),
            metadata=body.metadata,
        )
    except Exception as exc:
        _translate_stock_error(exc)
        raise


@app.patch("/inventory/items/{inventory_item_id}")
def adjust_inventory_item(
    inventory_item_id: UUID,
    body: InventoryAdjustment,
    actor: Actor = Depends(actor_from_headers),
    x_business_id: UUID = Header(..., alias="X-Business-Id"),
    x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
) -> dict[str, Any]:
    _authorize_inventory_company(actor, x_business_id)
    bind_correlation_id(x_correlation_id)
    try:
        return reservation_store().adjust_inventory_item(
            inventory_item_id=str(inventory_item_id),
            company_id=str(x_business_id),
            expected_version=body.expected_version,
            physical_quantity=body.physical_quantity,
            actor=str(actor.user_id),
            reason=body.reason,
        )
    except Exception as exc:
        _translate_stock_error(exc)
        raise


@app.post("/reservations", status_code=201)
def reserve_inventory(
    body: ReservationCreate,
    actor: Actor = Depends(actor_from_headers),
    x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
    x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
    x_causation_id: UUID | None = Header(default=None, alias="X-Causation-Id"),
) -> dict[str, Any]:
    _authorize_subject_or_operator(actor, body.user_id)
    if not 8 <= len(x_idempotency_key) <= 160:
        raise HTTPException(
            status_code=422,
            detail="X-Idempotency-Key deve possuir entre 8 e 160 caracteres.",
        )
    bind_correlation_id(x_correlation_id)
    try:
        result = reservation_store().reserve_inventory(
            user_id=str(body.user_id),
            company_id=str(body.company_id),
            inventory_item_id=str(body.inventory_item_id),
            order_id=str(body.order_id),
            quantity=body.quantity,
            expires_in_seconds=body.expires_in_seconds,
            actor=str(actor.user_id),
            idempotency_key=x_idempotency_key,
            correlation_id=str(x_correlation_id),
            causation_id=str(x_causation_id) if x_causation_id else None,
        )
    except Exception as exc:
        _translate_stock_error(exc)
        raise
    if result["status"] == "rejected":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "insufficient_stock",
                "reservation": result,
            },
        )
    return result


@app.post("/reservations/{reservation_id}/commit")
def commit_reservation(
    reservation_id: UUID,
    actor: Actor = Depends(actor_from_headers),
    x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
) -> dict[str, Any]:
    store = reservation_store()
    current = store.get_reservation(str(reservation_id))
    if current is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")
    _authorize_subject_or_operator(actor, UUID(current["user_id"]))
    bind_correlation_id(x_correlation_id)
    try:
        result = store.commit_reservation(
            reservation_id=str(reservation_id),
            expected_user_id=current["user_id"],
            actor=str(actor.user_id),
        )
    except Exception as exc:
        _translate_stock_error(exc)
        raise
    if result["status"] == "expired":
        raise HTTPException(
            status_code=409,
            detail={"code": "reservation_expired", "reservation": result},
        )
    return result


@app.post("/reservations/{reservation_id}/release")
def release_reservation(
    reservation_id: UUID,
    body: ReservationRelease,
    actor: Actor = Depends(actor_from_headers),
    x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
) -> dict[str, Any]:
    store = reservation_store()
    current = store.get_reservation(str(reservation_id))
    if current is None:
        raise HTTPException(status_code=404, detail="Reserva não encontrada.")
    _authorize_subject_or_operator(actor, UUID(current["user_id"]))
    bind_correlation_id(x_correlation_id)
    try:
        return store.release_reservation(
            reservation_id=str(reservation_id),
            expected_user_id=current["user_id"],
            actor=str(actor.user_id),
            reason=body.reason,
        )
    except Exception as exc:
        _translate_stock_error(exc)
        raise


@app.post("/reservations/expire")
def expire_reservations(
    limit: int = Query(default=100, ge=1, le=500),
    actor: Actor = Depends(actor_from_headers),
    x_correlation_id: UUID = Header(..., alias="X-Correlation-Id"),
) -> dict[str, Any]:
    if (
        "stock:reservations:expire" not in actor.scopes
        and not actor.roles.intersection(STOCK_OPERATOR_ROLES)
    ):
        raise HTTPException(
            status_code=403,
            detail="Escopo stock:reservations:expire ou perfil operador obrigatório.",
        )
    bind_correlation_id(x_correlation_id)
    try:
        expired = reservation_store().expire_due_reservations(
            actor=str(actor.user_id), limit=limit
        )
    except Exception as exc:
        _translate_stock_error(exc)
        raise
    return {"expired_count": len(expired), "reservations": expired}
