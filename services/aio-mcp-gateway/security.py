from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import secrets
import time
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol, Self

import jwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.transport_security import TransportSecuritySettings
from redis.asyncio import Redis
from starlette.types import ASGIApp, Message, Receive, Scope, Send

LOGGER = logging.getLogger("aio_mcp_gateway.security")
TRACEPARENT_VERSION = "00"
REQUEST_ID_MAX_LENGTH = 128
SENSITIVE_KEY_PARTS = (
    "authorization",
    "token",
    "secret",
    "password",
    "api_key",
    "apikey",
    "credential",
)

DEFAULT_TOOL_SCOPES: dict[str, frozenset[str]] = {
    "project_status": frozenset({"aio:mcp:read"}),
    "list_pending_tasks": frozenset({"aio:mcp:read"}),
    "search_repository": frozenset({"aio:mcp:read"}),
    "read_project_document": frozenset({"aio:mcp:read"}),
    "create_technical_report": frozenset({"aio:mcp:read"}),
    "valley_consumer_status": frozenset({"aio:mcp:read"}),
    "valley_rider_status": frozenset({"aio:mcp:read"}),
    "aio_admin_status": frozenset({"aio:mcp:read"}),
    "list_recent_pull_requests": frozenset({"aio:mcp:read"}),
    "inspect_failed_jobs": frozenset({"aio:mcp:read"}),
}


class SecurityConfigurationError(RuntimeError):
    """Raised when mandatory production controls are not configured."""


class RateLimitBackendError(RuntimeError):
    """Raised when the production rate-limit backend is unavailable."""


@dataclass(frozen=True)
class SecuritySettings:
    deployment_env: str
    auth_required: bool
    oidc_issuer: str | None
    oidc_audience: str | None
    oidc_jwks_url: str | None
    oidc_algorithms: tuple[str, ...]
    required_scope: str
    allowed_origins: frozenset[str]
    allowed_hosts: frozenset[str]
    protected_resource_url: str
    redis_url: str | None
    rate_limit_requests: int
    rate_limit_window_seconds: int
    max_request_body_bytes: int

    @property
    def is_production(self) -> bool:
        return self.deployment_env == "production"

    @classmethod
    def from_env(cls) -> Self:
        deployment_env = os.getenv("DEPLOYMENT_ENV", "development").strip().casefold()
        auth_required = _env_bool(
            "AUTH_REQUIRED",
            default=deployment_env == "production",
        )
        issuer = _clean_optional(os.getenv("OIDC_ISSUER"))
        audience = _clean_optional(os.getenv("OIDC_AUDIENCE"))
        jwks_url = _clean_optional(os.getenv("OIDC_JWKS_URL"))
        algorithms = tuple(
            item.strip()
            for item in os.getenv("OIDC_ALGORITHMS", "RS256").split(",")
            if item.strip()
        )
        required_scope = os.getenv("MCP_REQUIRED_SCOPE", "aio:mcp:read").strip()
        allowed_origins = frozenset(
            _normalize_origin(item)
            for item in os.getenv(
                "MCP_ALLOWED_ORIGINS",
                ",".join(
                    [
                        "https://brasildesconto.com.br",
                        "https://mcp.brasildesconto.com.br",
                        "https://mcp-staging.brasildesconto.com.br",
                        "https://mcp-preview.brasildesconto.com.br",
                        "http://localhost:8080",
                        "http://127.0.0.1:8080",
                    ]
                ),
            ).split(",")
            if item.strip()
        )
        allowed_hosts = frozenset(
            item.strip().casefold()
            for item in os.getenv(
                "MCP_ALLOWED_HOSTS",
                ",".join(
                    [
                        "mcp.brasildesconto.com.br",
                        "mcp-staging.brasildesconto.com.br",
                        "mcp-preview.brasildesconto.com.br",
                        "testserver",
                        "localhost:*",
                        "127.0.0.1:*",
                    ]
                ),
            ).split(",")
            if item.strip()
        )
        protected_resource_url = (
            os.getenv(
                "PROTECTED_RESOURCE_URL",
                "https://mcp.brasildesconto.com.br/mcp",
            )
            .strip()
            .rstrip("/")
        )
        redis_url = _clean_optional(os.getenv("REDIS_URL"))
        rate_limit_requests = _env_positive_int("RATE_LIMIT_REQUESTS", 120)
        rate_limit_window_seconds = _env_positive_int(
            "RATE_LIMIT_WINDOW_SECONDS",
            60,
        )
        max_request_body_bytes = _env_positive_int(
            "MAX_REQUEST_BODY_BYTES",
            1_048_576,
        )

        settings = cls(
            deployment_env=deployment_env,
            auth_required=auth_required,
            oidc_issuer=issuer,
            oidc_audience=audience,
            oidc_jwks_url=jwks_url,
            oidc_algorithms=algorithms,
            required_scope=required_scope,
            allowed_origins=allowed_origins,
            allowed_hosts=allowed_hosts,
            protected_resource_url=protected_resource_url,
            redis_url=redis_url,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window_seconds=rate_limit_window_seconds,
            max_request_body_bytes=max_request_body_bytes,
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        missing: list[str] = []
        if self.auth_required:
            if not self.oidc_issuer:
                missing.append("OIDC_ISSUER")
            if not self.oidc_audience:
                missing.append("OIDC_AUDIENCE")
            if not self.oidc_jwks_url:
                missing.append("OIDC_JWKS_URL")
            if not self.oidc_algorithms:
                missing.append("OIDC_ALGORITHMS")
            if not self.required_scope:
                missing.append("MCP_REQUIRED_SCOPE")
        if self.is_production and not self.redis_url:
            missing.append("REDIS_URL")
        if not self.allowed_origins:
            missing.append("MCP_ALLOWED_ORIGINS")
        if not self.allowed_hosts:
            missing.append("MCP_ALLOWED_HOSTS")
        if (
            not self.protected_resource_url.startswith("https://")
            and self.is_production
        ):
            missing.append("PROTECTED_RESOURCE_URL_HTTPS")
        if missing:
            joined = ", ".join(sorted(set(missing)))
            raise SecurityConfigurationError(
                f"configuração de segurança incompleta: {joined}"
            )


class OIDCTokenVerifier(TokenVerifier):
    """Validate JWT access tokens against an external OIDC provider."""

    def __init__(self, settings: SecuritySettings) -> None:
        if not (
            settings.oidc_issuer and settings.oidc_audience and settings.oidc_jwks_url
        ):
            raise SecurityConfigurationError(
                "OIDCTokenVerifier exige issuer, audience e JWKS URL"
            )
        self._issuer = settings.oidc_issuer
        self._audience = settings.oidc_audience
        self._resource = settings.protected_resource_url
        self._algorithms = list(settings.oidc_algorithms)
        self._jwks = PyJWKClient(
            settings.oidc_jwks_url,
            cache_keys=True,
            lifespan=300,
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = await asyncio.to_thread(self._decode, token)
        except jwt.PyJWTError:
            return None

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            return None

        client_id = claims.get("azp") or claims.get("client_id") or subject
        if not isinstance(client_id, str) or not client_id.strip():
            return None

        expires_at = claims.get("exp")
        if not isinstance(expires_at, int):
            return None

        return AccessToken(
            token=token,
            client_id=client_id,
            scopes=sorted(_extract_scopes(claims)),
            expires_at=expires_at,
            resource=self._resource,
            subject=subject,
            claims=claims,
        )

    def _decode(self, token: str) -> dict[str, Any]:
        signing_key = self._jwks.get_signing_key_from_jwt(token)
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=self._algorithms,
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iss", "aud", "sub"]},
        )
        return decoded


class RateLimiter(Protocol):
    async def allow(self, identity: str) -> bool:
        """Return whether a request is allowed for the current window."""

    async def close(self) -> None:
        """Release resources held by the limiter."""


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        self._limit = limit
        self._window_seconds = window_seconds
        self._entries: dict[str, tuple[float, int]] = {}
        self._lock = asyncio.Lock()

    async def allow(self, identity: str) -> bool:
        now = time.monotonic()
        async with self._lock:
            started_at, count = self._entries.get(identity, (now, 0))
            if now - started_at >= self._window_seconds:
                started_at, count = now, 0
            count += 1
            self._entries[identity] = (started_at, count)
            if len(self._entries) > 10_000:
                self._prune(now)
            return count <= self._limit

    def _prune(self, now: float) -> None:
        expired = [
            key
            for key, (started_at, _) in self._entries.items()
            if now - started_at >= self._window_seconds
        ]
        for key in expired:
            self._entries.pop(key, None)

    async def close(self) -> None:
        return None


class RedisRateLimiter:
    def __init__(self, redis_url: str, limit: int, window_seconds: int) -> None:
        self._redis = Redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
        )
        self._limit = limit
        self._window_seconds = window_seconds

    async def allow(self, identity: str) -> bool:
        bucket = int(time.time()) // self._window_seconds
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        key = f"aio:mcp:rate:{bucket}:{digest}"
        try:
            count = int(await self._redis.incr(key))
            if count == 1:
                await self._redis.expire(key, self._window_seconds + 5)
            return count <= self._limit
        except Exception as exc:
            raise RateLimitBackendError("backend de rate limit indisponível") from exc

    async def close(self) -> None:
        await self._redis.aclose()


def build_limiter(settings: SecuritySettings) -> RateLimiter:
    if settings.redis_url:
        return RedisRateLimiter(
            settings.redis_url,
            settings.rate_limit_requests,
            settings.rate_limit_window_seconds,
        )
    return InMemoryRateLimiter(
        settings.rate_limit_requests,
        settings.rate_limit_window_seconds,
    )


def build_transport_security(
    settings: SecuritySettings,
) -> TransportSecuritySettings:
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=sorted(settings.allowed_hosts),
        allowed_origins=sorted(settings.allowed_origins),
    )


class SecurityMiddleware:
    """Add rate limiting, response hardening and structured request logs."""

    def __init__(
        self,
        app: ASGIApp,
        settings: SecuritySettings,
        limiter: RateLimiter,
    ) -> None:
        self.app = app
        self.settings = settings
        self.limiter = limiter

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] == "lifespan":
            await self._lifespan(scope, receive, send)
            return
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started_at = time.monotonic()
        path = str(scope.get("path", ""))
        method = str(scope.get("method", "GET")).upper()
        headers = _headers(scope)
        request_id = _request_id(headers.get("x-request-id"))
        traceparent = _traceparent(headers.get("traceparent"))
        status_code = 500

        async def send_with_observability(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                response_headers = list(message.get("headers", []))
                response_headers.extend(
                    [
                        (b"x-request-id", request_id.encode("ascii")),
                        (b"traceparent", traceparent.encode("ascii")),
                        (b"x-content-type-options", b"nosniff"),
                        (b"cache-control", b"no-store"),
                        (b"referrer-policy", b"no-referrer"),
                        (
                            b"permissions-policy",
                            b"camera=(), microphone=(), geolocation=()",
                        ),
                    ]
                )
                message["headers"] = response_headers
            await send(message)

        try:
            if path == "/mcp" or path.startswith("/mcp/"):
                identity = _client_identity(scope, headers)
                if not await self.limiter.allow(identity):
                    await _json_response(
                        send_with_observability,
                        429,
                        {
                            "error": "rate_limit_exceeded",
                            "request_id": request_id,
                        },
                        headers=[
                            (
                                b"retry-after",
                                str(self.settings.rate_limit_window_seconds).encode(
                                    "ascii"
                                ),
                            )
                        ],
                    )
                    return
            await self.app(scope, receive, send_with_observability)
        except RateLimitBackendError:
            await _json_response(
                send_with_observability,
                503,
                {
                    "error": "rate_limit_backend_unavailable",
                    "request_id": request_id,
                },
            )
        finally:
            _log_request(
                method=method,
                path=path,
                status=status_code,
                request_id=request_id,
                traceparent=traceparent,
                duration_ms=round((time.monotonic() - started_at) * 1000, 2),
            )

    async def _lifespan(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        async def send_with_shutdown(message: Message) -> None:
            if message["type"] in {
                "lifespan.shutdown.complete",
                "lifespan.shutdown.failed",
            }:
                await self.limiter.close()
            await send(message)

        await self.app(scope, receive, send_with_shutdown)


async def _json_response(
    send: Send,
    status: int,
    payload: Mapping[str, Any],
    headers: list[tuple[bytes, bytes]] | None = None,
) -> None:
    body = json.dumps(
        redact(payload),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    response_headers = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"content-length", str(len(body)).encode("ascii")),
        *(headers or []),
    ]
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": response_headers,
        }
    )
    await send({"type": "http.response.body", "body": body})


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if any(part in key_text.casefold() for part in SENSITIVE_KEY_PARTS):
                redacted[key_text] = "[REDACTED]"
            else:
                redacted[key_text] = redact(item)
        return redacted
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    return value


def _extract_scopes(claims: Mapping[str, Any]) -> set[str]:
    raw = claims.get("scope", claims.get("scp", []))
    if isinstance(raw, str):
        return {item for item in raw.split() if item}
    if isinstance(raw, list):
        return {str(item) for item in raw if str(item)}
    return set()


def _headers(scope: Scope) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in scope.get("headers", []):
        result[key.decode("latin-1").casefold()] = value.decode(
            "latin-1",
            errors="replace",
        )
    return result


def _client_identity(scope: Scope, headers: Mapping[str, str]) -> str:
    authorization = headers.get("authorization")
    if authorization and authorization.casefold().startswith("bearer "):
        digest = hashlib.sha256(authorization.encode("utf-8")).hexdigest()
        return f"token:{digest}"

    forwarded = headers.get("cf-connecting-ip") or headers.get("x-forwarded-for")
    if forwarded:
        return f"ip:{forwarded.split(',', maxsplit=1)[0].strip()}"
    client = scope.get("client")
    if isinstance(client, tuple) and client:
        return f"ip:{client[0]}"
    return "anonymous"


def _request_id(value: str | None) -> str:
    if value:
        cleaned = value.strip()
        if 0 < len(cleaned) <= REQUEST_ID_MAX_LENGTH and all(
            character.isalnum() or character in "._:-" for character in cleaned
        ):
            return cleaned
    return str(uuid.uuid4())


def _traceparent(value: str | None) -> str:
    if value:
        normalized = value.strip().casefold()
        parts = normalized.split("-")
        if (
            len(parts) == 4
            and parts[0] == TRACEPARENT_VERSION
            and len(parts[1]) == 32
            and len(parts[2]) == 16
            and len(parts[3]) == 2
            and all(_is_hex(part) for part in parts)
            and parts[1] != "0" * 32
            and parts[2] != "0" * 16
        ):
            return normalized
    return f"00-{secrets.token_hex(16)}-{secrets.token_hex(8)}-01"


def _is_hex(value: str) -> bool:
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _normalize_origin(value: str) -> str:
    return value.strip().casefold().rstrip("/")


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise SecurityConfigurationError(f"{name} deve ser booleano")


def _env_positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise SecurityConfigurationError(f"{name} deve ser inteiro") from exc
    if value <= 0:
        raise SecurityConfigurationError(f"{name} deve ser maior que zero")
    return value


def _log_request(
    *,
    method: str,
    path: str,
    status: int,
    request_id: str,
    traceparent: str,
    duration_ms: float,
) -> None:
    LOGGER.info(
        json.dumps(
            {
                "event": "http_request",
                "method": method,
                "path": path,
                "status": status,
                "request_id": request_id,
                "traceparent": traceparent,
                "duration_ms": duration_ms,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )
