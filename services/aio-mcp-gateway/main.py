from __future__ import annotations

import contextlib
import logging
import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from security import (
    OIDCValidator,
    SecurityMiddleware,
    SecuritySettings,
    build_limiter,
    protected_resource_metadata,
)
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

SERVICE_NAME = "aio-mcp-gateway"
SERVICE_VERSION = "0.2.0"
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(message)s",
)

security_settings = SecuritySettings.from_env()
token_validator = (
    OIDCValidator(security_settings) if security_settings.auth_required else None
)
rate_limiter = build_limiter(security_settings)

mcp = FastMCP(
    "All in One + Valley",
    instructions=(
        "Gateway MCP somente de leitura para status, documentos e operações "
        "de diagnóstico do ecossistema All in One + Valley."
    ),
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",
)


def _status(component: str) -> dict[str, str]:
    return {
        "component": component,
        "status": "available",
        "mode": "read-only",
        "checked_at": datetime.now(UTC).isoformat(),
    }


@mcp.tool(annotations=READ_ONLY)
def project_status(scope: str = "all") -> dict[str, Any]:
    """Retorna o estado seguro e não confidencial do projeto."""
    allowed = {"all", "all_in_one", "valley_consumer", "valley_rider", "aio_admin"}
    if scope not in allowed:
        raise ValueError(f"scope inválido; use um de: {', '.join(sorted(allowed))}")
    return {
        "project": "All in One + Valley",
        "scope": scope,
        "gateway": _status(SERVICE_NAME),
        "deployment": security_settings.deployment_env,
        "auth_required": security_settings.auth_required,
        "canonical_endpoint": f"{security_settings.protected_resource_url}/mcp",
    }


@mcp.tool(annotations=READ_ONLY)
def list_pending_tasks() -> dict[str, Any]:
    """Lista pendências conhecidas do gateway sem modificar dados."""
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
            {"id": "cloud_run", "status": "pending_external_configuration"},
            {"id": "custom_domain", "status": "pending_external_configuration"},
            {"id": "gemini_spark", "status": "pending_external_validation"},
        ],
        "read_only": True,
        "canonical_domain": "mcp.brasildesconto.com.br",
    }


@mcp.tool(annotations=READ_ONLY)
def search_repository(query: str, limit: int = 20) -> dict[str, Any]:
    """Valida consulta; a integração GitHub será adicionada com OAuth."""
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
    return _status("valley_consumer")


@mcp.tool(annotations=READ_ONLY)
def valley_rider_status() -> dict[str, str]:
    """Retorna o status do domínio Valley Rider."""
    return _status("valley_rider")


@mcp.tool(annotations=READ_ONLY)
def aio_admin_status() -> dict[str, str]:
    """Retorna o status do domínio AIO Admin."""
    return _status("aio_admin")


@mcp.tool(annotations=READ_ONLY)
def list_recent_pull_requests(limit: int = 10) -> dict[str, Any]:
    """Prepara uma consulta segura de pull requests recentes."""
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    return {"items": [], "limit": limit, "integration_status": "oauth_required"}


@mcp.tool(annotations=READ_ONLY)
def inspect_failed_jobs(limit: int = 10) -> dict[str, Any]:
    """Prepara uma consulta segura de jobs com falha."""
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    return {"items": [], "limit": limit, "integration_status": "oauth_required"}


async def health(_: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "mode": security_settings.deployment_env,
        }
    )


async def oauth_protected_resource(_: Request) -> JSONResponse:
    return JSONResponse(protected_resource_metadata(security_settings))


@contextlib.asynccontextmanager
async def lifespan(_: Starlette) -> AsyncIterator[None]:
    try:
        async with mcp.session_manager.run():
            yield
    finally:
        await rate_limiter.close()


app = Starlette(
    routes=[
        Route("/health", endpoint=health, methods=["GET"]),
        Route(
            "/.well-known/oauth-protected-resource",
            endpoint=oauth_protected_resource,
            methods=["GET"],
        ),
        Mount("/mcp", app=mcp.streamable_http_app()),
    ],
    middleware=[
        Middleware(
            SecurityMiddleware,
            settings=security_settings,
            validator=token_validator,
            limiter=rate_limiter,
        )
    ],
    lifespan=lifespan,
)
