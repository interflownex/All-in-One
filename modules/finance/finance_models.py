from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from decimal import Decimal

class TransferRequest(BaseModel):
    source_wallet_id: UUID
    destination_user_id: UUID | None = None
    destination_wallet_id: UUID | None = None
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(..., pattern="^(BRL|NEX)$")
    description: str = Field(..., min_length=3, max_length=100)
    idempotency_key: str = Field(..., min_length=10)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return v.quantize(Decimal("0.0001"))

class EscrowRequest(BaseModel):
    wallet_id: UUID
    beneficiary_user_id: UUID
    amount: Decimal = Field(..., gt=0)
    release_condition: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(..., min_length=10)

class PixRequest(BaseModel):
    wallet_id: UUID
    pix_key: str = Field(..., min_length=5)
    amount: Decimal = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=10)
