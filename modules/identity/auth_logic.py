from __future__ import annotations

import os
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

try:
    import jwt
except ModuleNotFoundError:
    jwt = None

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ModuleNotFoundError:
    AsyncIOMotorClient = None

try:
    from passlib.context import CryptContext
except ModuleNotFoundError:
    CryptContext = None
from pydantic import BaseModel, Field

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], pbkdf2_sha256__rounds=120_000, deprecated="auto") if CryptContext else None

JWT_SECRET = os.getenv("ALL_IN_ONE_JWT_SECRET", "local-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

MONGO_URL = os.getenv("ALL_IN_ONE_MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_INITDB_DATABASE", "all_in_one")

class LoginRequest(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "usuario@exemplo.com"})
    password: str = Field(..., json_schema_extra={"example": "senha_segura_123"})

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_at: str

class TelemetryClient:
    def __init__(self):
        if AsyncIOMotorClient is None:
            self.client = None
            self.db = None
            self.access_logs = None
            return
        self.client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=1000)
        self.db = self.client[MONGO_DB]
        self.access_logs = self.db["access_logs"]

    async def log_access(
        self, 
        user_id: str, 
        action: str, 
        status: str, 
        ip_address: str | None = None, 
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None
    ):
        if self.access_logs is None:
            return
        try:
            await self.access_logs.insert_one({
                "user_id": user_id,
                "action": action,
                "status": status,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "occurred_at": datetime.now(timezone.utc),
                "metadata": metadata or {}
            })
        except Exception:
            return

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if pwd_context is None:
        return hmac.compare_digest(get_password_hash(plain_password), hashed_password)
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    if pwd_context is None:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), JWT_SECRET.encode("utf-8"), 120_000)
        return "pbkdf2_sha256$" + base64.urlsafe_b64encode(digest).decode("ascii")
    return pwd_context.hash(password)

def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    if jwt is None:
        encoded_jwt = _encode_local_jwt(to_encode)
    else:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt, expire


def _encode_local_jwt(payload: dict[str, Any]) -> str:
    def encode_part(value: dict[str, Any]) -> str:
        normalized = {
            key: (int(item.timestamp()) if isinstance(item, datetime) else item)
            for key, item in value.items()
        }
        raw = json.dumps(normalized, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    header = encode_part({"alg": JWT_ALGORITHM, "typ": "JWT"})
    body = encode_part(payload)
    signature = hmac.new(JWT_SECRET.encode("utf-8"), f"{header}.{body}".encode("ascii"), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{header}.{body}.{encoded_signature}"
