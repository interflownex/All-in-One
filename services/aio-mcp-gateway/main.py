from __future__ import annotations

import contextlib
import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable

import jwt
from jwt import PyJWKClient
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route

SERVICE_NAME = "aio-mcp-gateway"
SERVICE_VERSION = "0.1.0"
READ_ONLY = {"readOnlyHint": True, "destructiveHint": False}
RATE_LIMIT = int(os.getenv("AIO_MCP_RATE_LIMIT_PER_MINUTE", "60"))
MAX_QUERY_LENGTH = 200
SAFE_ID = re.compile(r"^[a-zA-Z0-9_.:/-]{1,200}$")
SECRET_KEYS = re.compile(r"(?i)(authorization|token|secret|password|api[-_]?key)")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)
_buckets: dict[str, deque[float]] = defaultdict(deque)

SCOPES = {
    "project_status": "project.read",
    "list_pending_tasks": "tasks.read",
    "search_repository": "repository.read",
    "read_project_document": "documents.read",
    "create_technical_report": "reports.generate",
    "valley_consumer_status": "valley.consumer.read",
    "valley_rider_status": "valley.rider.read",
    "aio_admin_status": "aio.admin.read",
    "list_recent_pull_requests": "github.pr.read",
    "inspect_failed_jobs": "ci.jobs.read",
}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SECRET_KEYS.search(key) else _redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _audit(**fields: Any) -> None:
    logger.info(json.dumps(_redact(fields), ensure_ascii=False, default=str))


def _rate_limit(subject: str) -> None:
    now = time.monotonic()
    bucket = _buckets[subject]
    while bucket and bucket[0] <= now - 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT:
        raise PermissionError("rate_limit_exceeded")
    bucket.append(now)


def _validate_identifier(value: str, field: str) -> str:
    normalized = value.strip()
    if not SAFE_ID.fullmatch(normalized):
        raise ValueError(f"{field} inválido")
    if ".." in normalized or normalized.startswith(("/", "\\")):
        raise ValueError(f"{field} bloqueado")
    return normalized


def _status(component: str) -> dict[str, str]:
    return {
        "component": component,
        "status": "available",
        "mode": "read-only",
        "checked_at": datetime.now(UTC).isoformat(),
    }


mcp = FastMCP(
    "All in One + Valley",
    instructions="Gateway MCP centralizado, somente leitura e com autorização por escopo.",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",
)


@mcp.tool(annotations=READ_ONLY)
def project_status(scope: str = "all") -> dict[str, Any]:
    """Retorna o estado seguro e não confidencial do projeto."""
    allowed = {"all", "all_in_one", "valley_consumer", "valley_rider", "aio_admin"}
    if scope not in allowed:
        raise ValueError("scope inválido")
    return {
        "project": "All in One + Valley",
        "scope": scope,
        "gateway": _status(SERVICE_NAME),
        "deployment": os.getenv("DEPLOYMENT_ENV", "development"),
        "mutating_tools_enabled": False,
    }


@mcp.tool(annotations=READ_ONLY)
def list_pending_tasks() -> dict[str, Any]:
    """Lista pendências externas conhecidas sem modificar dados."""
    return {
        "items": [
            {"id": "oauth-provider", "status": "requires_environment_configuration"},
            {"id": "cloud-run", "status": "requires_explicit_deploy_approval"},
            {"id": "custom-domain", "status": "requires_dns_approval"},
            {"id": "gemini-spark", "status": "requires_public_endpoint"},
        ],
        "read_only": True,
    }


@mcp.tool(annotations=READ_ONLY)
def search_repository(query: str, limit: int = 20) -> dict[str, Any]:
    """Prepara uma busca segura no provedor GitHub configurado."""
    normalized = query.strip()
    if not normalized or len(normalized) > MAX_QUERY_LENGTH:
        raise ValueError("query inválida")
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    blocked = (".env", "id_rsa", "id_ed25519", "credentials", "secret", "../", "\\")
    if any(term in normalized.casefold() for term in blocked):
        raise ValueError("consulta bloqueada pela política de segurança")
    return {"query": normalized, "limit": limit, "results": [], "provider": "github", "integration_status": "adapter_required"}


@mcp.tool(annotations=READ_ONLY)
def read_project_document(document_id: str) -> dict[str, Any]:
    """Solicita documento por identificador lógico, nunca por caminho arbitrário."""
    identifier = _validate_identifier(document_id, "document_id")
    return {"document_id": identifier, "content": None, "integration_status": "document_provider_required"}


@mcp.tool(annotations=READ_ONLY)
def create_technical_report(topic: str, sections: list[str] | None = None) -> dict[str, Any]:
    """Gera relatório em memória sem arquivo, commit ou pull request."""
    clean_topic = topic.strip()
    if not clean_topic or len(clean_topic) > 160:
        raise ValueError("topic inválido")
    selected = sections or ["Visão geral", "Evidências", "Riscos", "Próximas ações"]
    if len(selected) > 20 or any(not item.strip() or len(item) > 160 for item in selected):
        raise ValueError("sections inválidas")
    content = "# " + clean_topic + "\n\n" + "\n\n".join(f"## {item.strip()}\n" for item in selected)
    return {"title": clean_topic, "content": content, "persisted": False}


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
    """Prepara consulta somente leitura de pull requests."""
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    return {"items": [], "limit": limit, "integration_status": "github_oauth_required"}


@mcp.tool(annotations=READ_ONLY)
def inspect_failed_jobs(limit: int = 10) -> dict[str, Any]:
    """Prepara consulta somente leitura de jobs com falha."""
    if not 1 <= limit <= 50:
        raise ValueError("limit deve estar entre 1 e 50")
    return {"items": [], "limit": limit, "integration_status": "github_oauth_required"}


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        trace_id = request.headers.get("x-cloud-trace-context", "").split("/", 1)[0] or str(uuid.uuid4())
        started = time.monotonic()
        subject = "anonymous"
        status = 500
        try:
            if request.url.path != "/health":
                subject = self._authenticate(request)
                _rate_limit(subject)
            response = await call_next(request)
            status = response.status_code
        except PermissionError as exc:
            status = 429
            response = JSONResponse({"error": str(exc)}, status_code=status)
        except jwt.PyJWTError:
            status = 401
            response = JSONResponse({"error": "invalid_token"}, status_code=status)
        except (KeyError, ValueError):
            status = 401
            response = JSONResponse({"error": "authentication_configuration_error"}, status_code=status)
        response.headers["x-request-id"] = request_id
        response.headers["x-trace-id"] = trace_id
        _audit(event="request", request_id=request_id, trace_id=trace_id, subject=subject, path=request.url.path, method=request.method, status=status, latency_ms=round((time.monotonic() - started) * 1000, 2))
        return response

    @staticmethod
    def _authenticate(request: Request) -> str:
        if os.getenv("AIO_MCP_AUTH_DISABLED", "false").lower() == "true":
            return "development"
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise jwt.InvalidTokenError("missing bearer")
        token = authorization.removeprefix("Bearer ").strip()
        issuer = os.environ["AIO_MCP_OIDC_ISSUER"].rstrip("/")
        audience = os.environ["AIO_MCP_OIDC_AUDIENCE"]
        jwks_url = os.getenv("AIO_MCP_OIDC_JWKS_URL", issuer + "/.well-known/jwks.json")
        key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=["RS256", "ES256"], audience=audience, issuer=issuer)
        return str(claims["sub"])


async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION})


@contextlib.asynccontextmanager
async def lifespan(_: Starlette):
    async with mcp.session_manager.run():
        yield


app = Starlette(routes=[Route("/health", health, methods=["GET"]), Mount("/mcp", app=mcp.streamable_http_app())], lifespan=lifespan)
app.add_middleware(SecurityMiddleware)
