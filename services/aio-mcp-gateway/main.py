from __future__ import annotations

import contextlib
import os
from datetime import UTC, datetime
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

SERVICE_NAME = "aio-mcp-gateway"
SERVICE_VERSION = "0.1.0"
READ_ONLY = {"readOnlyHint": True, "destructiveHint": False}

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
        "deployment": os.getenv("DEPLOYMENT_ENV", "development"),
    }


@mcp.tool(annotations=READ_ONLY)
def list_pending_tasks() -> dict[str, Any]:
    """Lista pendências conhecidas do gateway sem modificar dados."""
    return {
        "items": [
            {"id": "oauth", "status": "pending_external_configuration"},
            {"id": "cloud_run", "status": "pending_external_configuration"},
            {"id": "custom_domain", "status": "pending_external_configuration"},
            {"id": "gemini_spark", "status": "pending_external_validation"},
        ],
        "read_only": True,
    }


@mcp.tool(annotations=READ_ONLY)
def search_repository(query: str, limit: int = 20) -> dict[str, Any]:
    """Valida uma consulta de repositório; integração GitHub será adicionada com OAuth."""
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
        }
    )


@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    async with mcp.session_manager.run():
        yield


app = Starlette(
    routes=[
        Route("/health", endpoint=health, methods=["GET"]),
        Mount("/mcp", app=mcp.streamable_http_app()),
    ],
    lifespan=lifespan,
)
