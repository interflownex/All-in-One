from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# Configuração de Criptografia de Senha
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Configurações JWT
JWT_SECRET = os.getenv("ALL_IN_ONE_JWT_SECRET", "local-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 dia

# Configuração MongoDB para Telemetria
MONGO_URL = os.getenv("ALL_IN_ONE_MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_INITDB_DATABASE", "all_in_one")

class LoginRequest(BaseModel):
    email: str = Field(..., example="usuario@exemplo.com")
    password: str = Field(..., example="senha_segura_123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_at: str

class TelemetryClient:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
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
        await self.access_logs.insert_one({
            "user_id": user_id,
            "action": action,
            "status": status,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "occurred_at": datetime.now(timezone.utc),
            "metadata": metadata or {}
        })

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt, expire
