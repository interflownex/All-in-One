from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import AnyHttpUrl
from security import (
    DEFAULT_TOOL_SCOPES,
    OIDCTokenVerifier,
    SecurityMiddleware,
    SecuritySettings,
    build_limiter,
    build_transport_security,
)
from starlette.requests import Request
from starlette.responses import JSONResponse

SERVICE_NAME = "aio-mcp-gateway"
SERVICE_VERSION = "0.2.0"
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(message)s",
)

security_settings = SecuritySettings.from_env()
token_verifier = (
    OIDCTokenVerifier(security_settings)
    if security_settings.auth_required
    else None
)
auth_settings = (
    AuthSettings(
        issuer_url=AnyHttpUrl(security_settings.oidc_issuer),
        resource_server_url=AnyHttpUrl(
            security_settings.protected_resource_url
        ),
        required_scopes=[security_settings.required_scope],
    )
    if security_settings.auth_required
    and security_settings.oidc_issuer is not None
    else None
)
rate_limiter = build_limiter(security_settings)

mcp = FastMCP(
    "All in One + Valley",
    instructions=(
        "Gateway MCP somente de leitura para status, documentos e operações "
        "de diagnóstico do ecossistema All in One + Valley."
    ),
    website_url="https://brasildesconto.com.br",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp",
    max_request_body_size=security_settings.max_request_body_bytes,
    token_verifier=token_verifier,
    auth=auth_settings,
    transport_security=build_transport_security(security_settings),
)


def _status(component: str) -> dict[str, str]:
    return {
        "component": component,
        "status": "available",
        "mode": "read-only",
        "checked_at": datetime.now(UTC).isoformat(),
    }


def _require_tool_scope(tool_name: str) -> None:
    """Enforce tool-specific scopes after the server-level base scope."""
    if not security_settings.auth_required:
        return

    access_token = get_access_token()
    if access_token is None:
        raise PermissionError("contexto de autenticação ausente")

    required = DEFAULT_TOOL_SCOPES.get(
        tool_name,
        frozenset({security_settings.required_scope}),
    )
    missing = required.difference(access_token.scopes)
    if missing:
        raise PermissionError(
            "escopo insuficiente para a ferramenta: "
            + ", ".join(sorted(missing))
        )


@mcp.tool(annotations=READ_ONLY)
def project_status(scope: str = "all") -> dict[str, Any]:
    """Retorna o estado seguro e não confidencial do projeto."""
    _require_tool_scope("project_status")
    allowed = {"all", "all_in_one", "valley_consumer", "valley_rider", "aio_admin"}
    if scope not in allowed:
        raise ValueError(f"scope inválido; use um de: {', '.join(sorted(allowed))}")
    return {
        "project": "All in One + Valley",
        "scope": scope,
        "gateway": _status(SERVICE_NAME),
        "deployment": security_settings.deployment_env,
        "auth_required": security_settings.auth_required,
        "canonical_endpoint": security_settings.protected_resource_url,
    }


@mcp.tool(annotations=READ_ONLY)
def list_pending_tasks() -> dict[str, Any]:
    """Lista pendências conhecidas do gateway sem modificar dados."""
    _require_tool_scope("list_pending_tasks")
    return {
        "items": [
            {
                "id": "oidc_provider",
                "status": (
                    "configured"
                    if security_settings.auth_required
                    else "pending_external_configuration"
                ),
            },
            {
                "id": "redis_rate_limit",
                "status": (
                    "configured"
                    if security_settings.redis_url
                    else "development_memory_backend"
                ),
            },
            {"id": "cloudflare_dns", "status": "pending_external_configuration"},
            {"id": "tls_certificate", "status": "pending_external_validation"},
            {"id": "gemini_spark", "status": "pending_external_validation"},
        ],
        "read_only": True,
        "canonical_domain": "mcp.brasildesconto.com.br",
    }


@mcp.tool(annotations=READ_ONLY)
def search_repository(query: str, limit: int = 20) -> dict[str, Any]:
    """Valida consulta; a integração GitHub será adicionada com OAuth."""
    _require_tool_scope("search_repository")
    normalized = query.strip()
    if not normalized:
        raise ValueError("query não pode ser vazia")
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    blocked = (".env", "id_rsa", "id_ed25519", "credentials", "secret", "../")
    if any(term in normalized.casefold() for term in blocked):
        raise ValueError("consulta bloqueada pela política de segurança")
    return {
        "query": normalized,
        "limit": limit,
        "results": [],
        "integration_status": "oauth_required",
    }


@mcp.tool(annotations=READ_ONLY)
def read_project_document(document_id: str) -> dict[str, Any]:
    """Retorna metadados seguros de um documento autorizado."""
    _require_tool_scope("read_project_document")
    identifier = document_id.strip()
    if not identifier or ".." in identifier or identifier.startswith(("/", "\\")):
        raise ValueError("document_id inválido")
    return {
        "document_id": identifier,
        "content": None,
        "integration_status": "document_provider_required",
    }


@mcp.tool(annotations=READ_ONLY)
def create_technical_report(topic: str) -> dict[str, Any]:
    """Gera uma estrutura de relatório em memória, sem persistência."""
    _require_tool_scope("create_technical_report")
    clean_topic = topic.strip()
    if not clean_topic:
        raise ValueError("topic não pode ser vazio")
    return {
        "title": clean_topic,
        "sections": ["Visão geral", "Evidências", "Riscos", "Próximas ações"],
        "persisted": False,
    }


@mcp.tool(annotations=READ_ONLY)
def valley_consumer_status() -> dict[str, str]:
    """Retorna o status do domínio Valley Consumidor."""
    _require_tool_scope("valley_consumer_status")
    return _status("valley_consumer")


@mcp.tool(annotations=READ_ONLY)
def valley_rider_status() -> dict[str, str]:
    """Retorna o status do domínio Valley Rider."""
    _require_tool_scope("valley_rider_status")
    return _status("valley_rider")


@mcp.tool(annotations=READ_ONLY)
def aio_admin_status() -> dict[str, str]:
    """Retorna o status do domínio AIO Admin."""
    _require_tool_scope("aio_admin_status")
    return _status("aio_admin")


@mcp.tool(annotations=READ_ONLY)
def list_recent_pull_requests(limit: int = 10) -> dict[str, Any]:
    """Prepara uma consulta segura de pull requests recentes."""
    _require_tool_scope("list_recent_pull_requests")
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    return {"items": [], "limit": limit, "integration_status": "oauth_required"}


@mcp.tool(annotations=READ_ONLY)
def inspect_failed_jobs(limit: int = 10) -> dict[str, Any]:
    """Prepara uma consulta segura de jobs com falha."""
    _require_tool_scope("inspect_failed_jobs")
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    return {"items": [], "limit": limit, "integration_status": "oauth_required"}


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "mode": security_settings.deployment_env,
            "auth_required": security_settings.auth_required,
            "rate_limit_backend": (
                "redis" if security_settings.redis_url else "memory"
            ),
        }
    )


app = SecurityMiddleware(
    mcp.streamable_http_app(),
    settings=security_settings,
    limiter=rate_limiter,
)
