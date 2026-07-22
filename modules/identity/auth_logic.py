from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import struct
import time
from datetime import UTC, datetime, timedelta
from typing import Any

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
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pydantic import BaseModel, Field

pwd_context = (
    CryptContext(
        schemes=["pbkdf2_sha256"], pbkdf2_sha256__rounds=120_000, deprecated="auto"
    )
    if CryptContext
    else None
)

JWT_SECRET = os.getenv("ALL_IN_ONE_JWT_SECRET", "local-secret-key-change-in-production")
INSECURE_LOCAL_JWT_SECRET = "local-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ALL_IN_ONE_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("ALL_IN_ONE_REFRESH_TOKEN_EXPIRE_DAYS", "30"))

MONGO_URL = os.getenv("ALL_IN_ONE_MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_INITDB_DATABASE", "all_in_one")


class LoginRequest(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "usuario@exemplo.com"})
    password: str = Field(..., json_schema_extra={"example": "senha_segura_123"})


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    session_id: str
    expires_at: str
    refresh_expires_at: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)
    device_fingerprint: str | None = Field(default=None, min_length=8, max_length=256)


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
        metadata: dict[str, Any] | None = None,
    ):
        if self.access_logs is None:
            return
        try:
            await self.access_logs.insert_one(
                {
                    "user_id": user_id,
                    "action": action,
                    "status": status,
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "occurred_at": datetime.now(UTC),
                    "metadata": metadata or {},
                }
            )
        except Exception:
            return


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if pwd_context is None:
        return hmac.compare_digest(get_password_hash(plain_password), hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    if pwd_context is None:
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), JWT_SECRET.encode("utf-8"), 120_000
        )
        return "pbkdf2_sha256$" + base64.urlsafe_b64encode(digest).decode("ascii")
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> tuple[str, datetime]:
    validate_auth_configuration()
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    if jwt is None:
        encoded_jwt = _encode_local_jwt(to_encode)
    else:
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt, expire


def validate_auth_configuration() -> None:
    environment = os.getenv("ALL_IN_ONE_ENV", "development").casefold()
    if environment == "production" and JWT_SECRET == INSECURE_LOCAL_JWT_SECRET:
        raise RuntimeError("ALL_IN_ONE_JWT_SECRET forte e obrigatorio em producao.")
    if not 1 <= ACCESS_TOKEN_EXPIRE_MINUTES <= 60:
        raise RuntimeError(
            "ALL_IN_ONE_ACCESS_TOKEN_EXPIRE_MINUTES deve ficar entre 1 e 60."
        )
    if not 1 <= REFRESH_TOKEN_EXPIRE_DAYS <= 90:
        raise RuntimeError(
            "ALL_IN_ONE_REFRESH_TOKEN_EXPIRE_DAYS deve ficar entre 1 e 90."
        )


def create_refresh_token() -> tuple[str, str, datetime]:
    token = secrets.token_urlsafe(48)
    return (
        token,
        hash_refresh_token(token),
        datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _mfa_key() -> bytes:
    configured = os.getenv("ALL_IN_ONE_MFA_ENCRYPTION_KEY")
    if configured:
        try:
            key = base64.urlsafe_b64decode(configured.encode("ascii"))
        except Exception as exc:
            raise RuntimeError(
                "ALL_IN_ONE_MFA_ENCRYPTION_KEY deve usar Base64 URL-safe."
            ) from exc
        if len(key) != 32:
            raise RuntimeError(
                "ALL_IN_ONE_MFA_ENCRYPTION_KEY deve representar exatamente 32 bytes."
            )
        return key
    if os.getenv("ALL_IN_ONE_ENV", "development").casefold() == "production":
        raise RuntimeError("ALL_IN_ONE_MFA_ENCRYPTION_KEY obrigatoria em producao.")
    return hashlib.sha256((JWT_SECRET + ":identity:mfa:v1").encode("utf-8")).digest()


def encrypt_mfa_secret(secret: str, user_id: str) -> str:
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(_mfa_key()).encrypt(
        nonce, secret.encode("ascii"), user_id.encode("utf-8")
    )
    return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def decrypt_mfa_secret(envelope: str, user_id: str) -> str:
    sealed = base64.urlsafe_b64decode(envelope.encode("ascii"))
    if len(sealed) < 29:
        raise ValueError("Envelope MFA invalido.")
    return (
        AESGCM(_mfa_key())
        .decrypt(sealed[:12], sealed[12:], user_id.encode("utf-8"))
        .decode("ascii")
    )


def totp_counter(at_time: int | None = None, step_seconds: int = 30) -> int:
    return (int(time.time()) if at_time is None else at_time) // step_seconds


def totp_code(secret: str, counter: int) -> str:
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded, casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    binary = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{binary % 1_000_000:06d}"


def verify_totp(
    secret: str, code: str, last_counter: int = -1, window: int = 1
) -> int | None:
    if not re_fullmatch_digits(code, 6):
        return None
    current = totp_counter()
    for counter in range(current - window, current + window + 1):
        if counter > last_counter and hmac.compare_digest(
            totp_code(secret, counter), code
        ):
            return counter
    return None


def re_fullmatch_digits(value: str, length: int) -> bool:
    return len(value) == length and value.isascii() and value.isdigit()


def _encode_local_jwt(payload: dict[str, Any]) -> str:
    def encode_part(value: dict[str, Any]) -> str:
        normalized = {
            key: (int(item.timestamp()) if isinstance(item, datetime) else item)
            for key, item in value.items()
        }
        raw = json.dumps(normalized, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    header = encode_part({"alg": JWT_ALGORITHM, "typ": "JWT"})
    body = encode_part(payload)
    signature = hmac.new(
        JWT_SECRET.encode("utf-8"), f"{header}.{body}".encode("ascii"), hashlib.sha256
    ).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return f"{header}.{body}.{encoded_signature}"
