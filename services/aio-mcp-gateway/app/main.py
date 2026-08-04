from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Callable

import jwt
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from jwt import PyJWKClient
from pydantic import BaseModel, ConfigDict, Field, ValidationError

SERVICE_NAME = "aio-mcp-gateway"
SERVICE_VERSION = "0.1.0"
MCP_PROTOCOL_VERSION = "2025-06-18"
ROOT = Path(os.getenv("AIO_REPOSITORY_ROOT", "/workspace")).resolve()
MAX_FILE_BYTES = int(os.getenv("AIO_MCP_MAX_FILE_BYTES", "524288"))
REQUEST_TIMEOUT_SECONDS = float(os.getenv("AIO_MCP_TOOL_TIMEOUT_SECONDS", "15"))
RATE_LIMIT = int(os.getenv("AIO_MCP_RATE_LIMIT_PER_MINUTE", "60"))
ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".ts", ".tsx", ".js", ".jsx", ".dart"}
SECRET_PATTERN = re.compile(r"(?i)(authorization|token|secret|password|api[-_]?key)\s*[:=]\s*[^\s,;]+")

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)
_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


class RpcRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    jsonrpc: str = Field(pattern=r"^2\.0$")
    id: str | int | None = None
    method: str = Field(min_length=1, max_length=128)
    params: dict[str, Any] = Field(default_factory=dict)


class ToolCallParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=128)
    arguments: dict[str, Any] = Field(default_factory=dict)


class AuthContext(BaseModel):
    subject: str
    scopes: frozenset[str]


class ToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: dict[str, Any]
    annotations: dict[str, bool] = {"readOnlyHint": True, "destructiveHint": False}
    required_scope: str


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if SECRET_PATTERN.search(k) else _redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str):
        return SECRET_PATTERN.sub(lambda m: m.group(1) + "=[REDACTED]", value)
    return value


def _audit(**fields: Any) -> None:
    logger.info(json.dumps(_redact(fields), ensure_ascii=False, default=str))


def _safe_path(relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path:
        raise ValueError("invalid_path")
    candidate = (ROOT / relative_path).resolve(strict=False)
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("path_outside_repository") from exc
    if candidate.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError("extension_not_allowed")
    if candidate.exists() and candidate.is_symlink():
        raise ValueError("symlink_not_allowed")
    return candidate


def _read_text(relative_path: str) -> str:
    path = _safe_path(relative_path)
    if not path.is_file():
        raise ValueError("file_not_found")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("file_too_large")
    return path.read_text(encoding="utf-8", errors="strict")


def _list_pending_tasks(arguments: dict[str, Any]) -> dict[str, Any]:
    candidates = ["tarefas.md", "TASKS.md", "docs/pendencias.md"]
    found = []
    for candidate in candidates:
        path = ROOT / candidate
        if path.is_file():
            found.append({"path": candidate, "content": path.read_text(encoding="utf-8")[:MAX_FILE_BYTES]})
    return {"status": "ok", "documents": found, "count": len(found)}


def _project_status(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "repository_root_available": ROOT.is_dir(),
        "mode": "read-only",
        "mutating_tools_enabled": False,
    }


def _search_repository(arguments: dict[str, Any]) -> dict[str, Any]:
    query = str(arguments.get("query", "")).strip()
    if not query or len(query) > 200:
        raise ValueError("invalid_query")
    limit = min(max(int(arguments.get("limit", 20)), 1), 50)
    needle = query.casefold()
    results: list[dict[str, Any]] = []
    for path in ROOT.rglob("*"):
        if len(results) >= limit:
            break
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        try:
            relative = path.resolve().relative_to(ROOT).as_posix()
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if needle in line.casefold():
                    results.append({"path": relative, "line": number, "preview": line[:500]})
                    if len(results) >= limit:
                        break
        except (OSError, ValueError):
            continue
    return {"status": "ok", "query": query, "results": results, "count": len(results)}


def _read_project_document(arguments: dict[str, Any]) -> dict[str, Any]:
    path = str(arguments.get("path", ""))
    return {"status": "ok", "path": path, "content": _read_text(path)}


def _create_technical_report(arguments: dict[str, Any]) -> dict[str, Any]:
    title = str(arguments.get("title", "Relatório técnico")).strip()[:160]
    sections = arguments.get("sections", [])
    if not isinstance(sections, list) or len(sections) > 50:
        raise ValueError("invalid_sections")
    lines = [f"# {title}", "", "> Gerado em memória. Nenhum arquivo foi persistido.", ""]
    for section in sections:
        if not isinstance(section, dict):
            raise ValueError("invalid_section")
        heading = str(section.get("heading", "Seção")).strip()[:160]
        body = str(section.get("body", ""))[:10000]
        lines.extend([f"## {heading}", "", body, ""])
    return {"status": "ok", "persisted": False, "content": "\n".join(lines)}


def _component_status(component: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        paths = {
            "valley_consumer": ["apps/valley-flutter", "apps/valley"],
            "valley_rider": ["apps/valley_rider", "apps/valley-rider"],
            "aio_admin": ["apps/aio-admin", "apps/aio_admin"],
        }[component]
        available = [path for path in paths if (ROOT / path).exists()]
        return {"status": "ok", "component": component, "available_paths": available}
    return handler


def _list_recent_pull_requests(arguments: dict[str, Any]) -> dict[str, Any]:
    return {"status": "not_configured", "reason": "github_read_adapter_required", "items": []}


def _inspect_failed_jobs(arguments: dict[str, Any]) -> dict[str, Any]:
    return {"status": "not_configured", "reason": "ci_read_adapter_required", "items": []}


TOOLS: dict[str, tuple[ToolDefinition, Callable[[dict[str, Any]], dict[str, Any]]]] = {}


def _register(definition: ToolDefinition, handler: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
    TOOLS[definition.name] = (definition, handler)


def _schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties or {}, "required": required or [], "additionalProperties": False}


_register(ToolDefinition(name="project_status", description="Retorna o estado seguro do projeto e do gateway.", inputSchema=_schema(), required_scope="project.read"), _project_status)
_register(ToolDefinition(name="list_pending_tasks", description="Lista documentos de pendências conhecidos.", inputSchema=_schema(), required_scope="tasks.read"), _list_pending_tasks)
_register(ToolDefinition(name="search_repository", description="Pesquisa texto em arquivos permitidos do repositório.", inputSchema=_schema({"query": {"type": "string", "minLength": 1, "maxLength": 200}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}}, ["query"]), required_scope="repository.read"), _search_repository)
_register(ToolDefinition(name="read_project_document", description="Lê documento textual dentro da raiz autorizada.", inputSchema=_schema({"path": {"type": "string", "minLength": 1, "maxLength": 500}}, ["path"]), required_scope="documents.read"), _read_project_document)
_register(ToolDefinition(name="create_technical_report", description="Gera relatório em memória sem persistir arquivos.", inputSchema=_schema({"title": {"type": "string"}, "sections": {"type": "array", "items": {"type": "object"}}}), required_scope="reports.generate"), _create_technical_report)
_register(ToolDefinition(name="valley_consumer_status", description="Verifica caminhos do Valley Consumidor.", inputSchema=_schema(), required_scope="valley.consumer.read"), _component_status("valley_consumer"))
_register(ToolDefinition(name="valley_rider_status", description="Verifica caminhos do Valley Rider.", inputSchema=_schema(), required_scope="valley.rider.read"), _component_status("valley_rider"))
_register(ToolDefinition(name="aio_admin_status", description="Verifica caminhos do AIO Admin.", inputSchema=_schema(), required_scope="aio.admin.read"), _component_status("aio_admin"))
_register(ToolDefinition(name="list_recent_pull_requests", description="Lista PRs recentes por adaptador GitHub somente leitura.", inputSchema=_schema(), required_scope="github.pr.read"), _list_recent_pull_requests)
_register(ToolDefinition(name="inspect_failed_jobs", description="Inspeciona jobs de CI com falha por adaptador somente leitura.", inputSchema=_schema(), required_scope="ci.jobs.read"), _inspect_failed_jobs)


def _authenticate(authorization: str | None) -> AuthContext:
    if os.getenv("AIO_MCP_AUTH_DISABLED", "false").lower() == "true":
        return AuthContext(subject="development", scopes=frozenset(item[0].required_scope for item in TOOLS.values()))
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    token = authorization.removeprefix("Bearer ").strip()
    issuer = os.environ["AIO_MCP_OIDC_ISSUER"].rstrip("/")
    audience = os.environ["AIO_MCP_OIDC_AUDIENCE"]
    jwks_url = os.getenv("AIO_MCP_OIDC_JWKS_URL", issuer + "/.well-known/jwks.json")
    try:
        key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=["RS256", "ES256"], audience=audience, issuer=issuer)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid_token") from exc
    raw_scopes = claims.get("scope", "")
    scopes = frozenset(raw_scopes.split() if isinstance(raw_scopes, str) else raw_scopes)
    return AuthContext(subject=str(claims.get("sub", "unknown")), scopes=scopes)


def _rate_limit(key: str) -> None:
    now = time.monotonic()
    bucket = _rate_buckets[key]
    while bucket and bucket[0] < now - 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="rate_limit_exceeded")
    bucket.append(now)


def _rpc_result(request_id: Any, result: Any) -> JSONResponse:
    return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": result})


def _rpc_error(request_id: Any, code: int, message: str, data: Any | None = None, status: int = 400) -> JSONResponse:
    payload: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        payload["data"] = data
    return JSONResponse({"jsonrpc": "2.0", "id": request_id, "error": payload}, status_code=status)


app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION, docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def request_context(request: Request, call_next: Callable[..., Any]) -> JSONResponse:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    trace_id = request.headers.get("x-cloud-trace-context", "").split("/", 1)[0] or str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.trace_id = trace_id
    started = time.monotonic()
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    response.headers["x-trace-id"] = trace_id
    _audit(event="http_request", request_id=request_id, trace_id=trace_id, path=request.url.path, method=request.method, status=response.status_code, latency_ms=round((time.monotonic() - started) * 1000, 2))
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.post("/mcp")
async def mcp(request: Request, authorization: str | None = Header(default=None)) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
    try:
        body = await request.json()
        rpc = RpcRequest.model_validate(body)
    except (json.JSONDecodeError, ValidationError):
        return _rpc_error(None, -32600, "Invalid Request")
    try:
        auth = _authenticate(authorization)
        _rate_limit(auth.subject)
    except HTTPException as exc:
        return _rpc_error(rpc.id, -32001, str(exc.detail), status=exc.status_code)

    if rpc.method == "initialize":
        return _rpc_result(rpc.id, {"protocolVersion": MCP_PROTOCOL_VERSION, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": SERVICE_NAME, "version": SERVICE_VERSION}})
    if rpc.method == "notifications/initialized":
        return _rpc_result(rpc.id, {})
    if rpc.method == "tools/list":
        tools = [definition.model_dump(exclude={"required_scope"}) for definition, _ in TOOLS.values() if definition.required_scope in auth.scopes]
        return _rpc_result(rpc.id, {"tools": tools})
    if rpc.method == "tools/call":
        try:
            call = ToolCallParams.model_validate(rpc.params)
        except ValidationError as exc:
            return _rpc_error(rpc.id, -32602, "Invalid params", exc.errors())
        entry = TOOLS.get(call.name)
        if entry is None:
            return _rpc_error(rpc.id, -32601, "Tool not found")
        definition, handler = entry
        if definition.required_scope not in auth.scopes:
            return _rpc_error(rpc.id, -32003, "insufficient_scope", status=403)
        started = time.monotonic()
        try:
            result = handler(call.arguments)
            if time.monotonic() - started > REQUEST_TIMEOUT_SECONDS:
                raise TimeoutError("tool_timeout")
            _audit(event="tool_call", request_id=request_id, trace_id=trace_id, subject=auth.subject, tool=call.name, scope=definition.required_scope, outcome="success")
            return _rpc_result(rpc.id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}], "structuredContent": result, "isError": False})
        except (ValueError, TimeoutError) as exc:
            _audit(event="tool_call", request_id=request_id, trace_id=trace_id, subject=auth.subject, tool=call.name, scope=definition.required_scope, outcome="rejected", reason=str(exc))
            return _rpc_result(rpc.id, {"content": [{"type": "text", "text": str(exc)}], "isError": True})
        except Exception:
            logger.exception("tool_call_failed")
            return _rpc_error(rpc.id, -32603, "Internal error", status=500)
    return _rpc_error(rpc.id, -32601, "Method not found")
