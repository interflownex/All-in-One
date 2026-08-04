from __future__ import annotations

import os
from urllib.parse import urlsplit

from security import SecurityConfigurationError, SecuritySettings

CANONICAL_PRODUCTION_RESOURCE = "https://mcp.brasildesconto.com.br/mcp"
CANONICAL_PRODUCTION_HOST = "mcp.brasildesconto.com.br"
CANONICAL_PRODUCTION_ORIGIN = "https://mcp.brasildesconto.com.br"
SUPPORTED_DEPLOYMENT_ENVS = frozenset(
    {"development", "test", "staging", "preview", "production"}
)
SAFE_ASYMMETRIC_OIDC_ALGORITHMS = frozenset(
    {
        "RS256",
        "RS384",
        "RS512",
        "PS256",
        "PS384",
        "PS512",
        "ES256",
        "ES384",
        "ES512",
        "EdDSA",
    }
)


def enforce_runtime_security_invariants(
    settings: SecuritySettings,
) -> SecuritySettings:
    """Reject unsafe runtime combinations before FastMCP is constructed."""
    errors: list[str] = []

    if settings.deployment_env not in SUPPORTED_DEPLOYMENT_ENVS:
        errors.append("DEPLOYMENT_ENV_UNSUPPORTED")

    _validate_resource_url(settings, errors)

    if settings.auth_required:
        _validate_oidc(settings, errors)

    if settings.is_production:
        _validate_production(settings, errors)

    if errors:
        raise SecurityConfigurationError(
            "invariantes produtivos inválidos: " + ", ".join(sorted(set(errors)))
        )
    return settings


def _validate_resource_url(
    settings: SecuritySettings,
    errors: list[str],
) -> None:
    parsed = urlsplit(settings.protected_resource_url)
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        errors.append("PROTECTED_RESOURCE_URL_INVALID")
    if parsed.path.rstrip("/") != "/mcp":
        errors.append("PROTECTED_RESOURCE_URL_MUST_END_IN_MCP")
    if settings.is_production and parsed.scheme != "https":
        errors.append("PROTECTED_RESOURCE_URL_HTTPS")


def _validate_oidc(
    settings: SecuritySettings,
    errors: list[str],
) -> None:
    algorithms = frozenset(settings.oidc_algorithms)
    if not algorithms or not algorithms.issubset(SAFE_ASYMMETRIC_OIDC_ALGORITHMS):
        errors.append("OIDC_ALGORITHMS_UNSAFE")

    for name, value in (
        ("OIDC_ISSUER", settings.oidc_issuer),
        ("OIDC_JWKS_URL", settings.oidc_jwks_url),
    ):
        if value is None:
            continue
        parsed = urlsplit(value)
        if parsed.scheme == "https":
            continue
        if (
            not settings.is_production
            and parsed.scheme == "http"
            and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        ):
            continue
        errors.append(f"{name}_HTTPS")


def _validate_production(
    settings: SecuritySettings,
    errors: list[str],
) -> None:
    if not settings.auth_required:
        errors.append("AUTH_REQUIRED_MUST_BE_TRUE")
    if not settings.redis_url:
        errors.append("REDIS_URL")

    if not os.getenv("MCP_ALLOWED_HOSTS", "").strip():
        errors.append("MCP_ALLOWED_HOSTS_EXPLICIT")
    if not os.getenv("MCP_ALLOWED_ORIGINS", "").strip():
        errors.append("MCP_ALLOWED_ORIGINS_EXPLICIT")

    if settings.protected_resource_url != CANONICAL_PRODUCTION_RESOURCE:
        errors.append("PROTECTED_RESOURCE_URL_CANONICAL")
    if CANONICAL_PRODUCTION_HOST not in settings.allowed_hosts:
        errors.append("MCP_ALLOWED_HOSTS_CANONICAL")
    if CANONICAL_PRODUCTION_ORIGIN not in settings.allowed_origins:
        errors.append("MCP_ALLOWED_ORIGINS_CANONICAL")

    if any("*" in host for host in settings.allowed_hosts):
        errors.append("MCP_ALLOWED_HOSTS_WILDCARD")
    if any(not origin.startswith("https://") for origin in settings.allowed_origins):
        errors.append("MCP_ALLOWED_ORIGINS_HTTPS")
