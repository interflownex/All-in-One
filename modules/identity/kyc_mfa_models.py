from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from uuid import UUID

class KYCSubmission(BaseModel):
    user_id: UUID
    biometry_hash: str = Field(..., min_length=32, description="Hash da face extraído via SDK de biometria")
    doc_front_base64: str | None = Field(default=None, description="Documento frente em Base64 para OCR")
    doc_back_base64: str | None = Field(default=None, description="Documento verso em Base64 para OCR")
    idempotency_key: str | None = Field(default=None)

class KYCStatus(BaseModel):
    record_id: UUID
    user_id: UUID
    status: str
    risk_score: float | None = None
    reason: str | None = None

class MFASetup(BaseModel):
    user_id: UUID
    method: str = Field(..., pattern="^(totp|sms|email|biometric)$")
    idempotency_key: str | None = Field(default=None)

class MFAVerification(BaseModel):
    user_id: UUID
    method: str
    code: str
