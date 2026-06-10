import os
import sys
import httpx
import hashlib
import hmac
import asyncio
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote
from uuid import UUID

from fastapi import Request, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

try:
    import redis.asyncio as redis
except ModuleNotFoundError:
    redis = None

try:
    import jwt
except ModuleNotFoundError:
    jwt = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app, get_config
from shared.security import Actor
from shared.valley_catalog import PUBLIC_RESOURCE_TYPES, offer_sort_key, valley_facets

app = create_module_app("api_hub")

cors_origins = [
    origin.strip()
    for origin in get_config(
        "ALL_IN_ONE_CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:5175",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
    allow_headers=["*"],
)

MODULES = [
    "ai_core", "bi", "bpm", "business", "crm", "delivery", "document", "erp",
    "finance", "health", "hr", "identity", "jobs", "legal", "marketplace",
    "mobility", "permissions", "property", "riders", "services", "stock",
    "tms", "vision", "wms"
]

SERVICES = {
    mod: get_config(f"{mod.upper()}_SERVICE_URL", f"http://{mod}:8000")
    for mod in MODULES
}
JWT_SECRET = get_config("ALL_IN_ONE_JWT_SECRET", "local-secret-key-change-in-production")
REDIS_URL = get_config("ALL_IN_ONE_REDIS_URL", "redis://redis:6379/0")
WEBHOOK_SECRET = get_config("ALL_IN_ONE_WEBHOOK_SECRET", "local-webhook-secret-change-in-production")

client = httpx.AsyncClient()
redis_client = redis.from_url(REDIS_URL, decode_responses=True) if redis else None

CATALOG_SOURCE_MODULES = tuple(PUBLIC_RESOURCE_TYPES)
CATALOG_QUERY_FIELDS = (
    "q",
    "category",
    "offer_type",
    "lat",
    "lng",
    "company_type",
    "company_category",
    "business_activity",
    "price_min",
    "price_max",
    "availability",
    "verified_only",
)


class CatalogActionRequest(BaseModel):
    offer_id: str = Field(min_length=3, max_length=240)
    action: Literal["buy", "book", "hire", "request"]
    customer_user_id: UUID
    idempotency_key: str = Field(min_length=8, max_length=120)
    scheduled_at: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=500)
    quantity: int = Field(default=1, ge=1, le=99)


class CatalogPaymentRequest(BaseModel):
    order_id: UUID
    idempotency_key: str = Field(min_length=8, max_length=120)
    method: Literal["pix_sandbox"] = "pix_sandbox"


class SupportCaseRequest(BaseModel):
    kind: Literal["support", "dispute"]
    subject: str | None = Field(default=None, max_length=200)
    message: str = Field(min_length=5, max_length=1000)
    desired_resolution: str | None = Field(default=None, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=120)


class ConsumerReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)
    idempotency_key: str = Field(min_length=8, max_length=120)


def _catalog_offer_key(offer: dict[str, Any]) -> str:
    return str(
        offer.get("offer_id")
        or offer.get("id")
        or ":".join(
            str(offer.get(field) or "")
            for field in ("source_module", "source_resource_type", "source_entity_id")
        )
    )


def merge_catalog_offers(results: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for offers in results:
        for offer in offers:
            key = _catalog_offer_key(offer)
            current = merged.get(key)
            if current is None or (
                current.get("availability_status") == "coming_soon"
                and offer.get("availability_status") != "coming_soon"
            ):
                merged[key] = offer
    return sorted(merged.values(), key=offer_sort_key)


async def _fetch_catalog_offer(offer_id: str) -> dict[str, Any]:
    configured_module = offer_id.split(":", 1)[0].strip().casefold()
    if configured_module not in CATALOG_SOURCE_MODULES:
        raise HTTPException(status_code=422, detail="Origem da oferta invalida.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=5),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def _do_request():
        return await client.get(
            f"{SERVICES[configured_module]}/valley/catalog/offers/{quote(offer_id, safe='')}",
            timeout=3.0,
        )

    try:
        response = await _do_request()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Nao foi possivel validar a oferta agora.") from exc
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Oferta nao encontrada.")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="A fonte da oferta esta temporariamente indisponivel.")
    offer = response.json()
    if not isinstance(offer, dict):
        raise HTTPException(status_code=502, detail="A fonte retornou uma oferta invalida.")
    if offer.get("availability_status") not in {"available", "limited"}:
        raise HTTPException(status_code=409, detail="Esta oferta nao esta disponivel para solicitar agora.")
    return offer


async def _create_catalog_resource(
    module_name: str,
    resource_type: str,
    body: CatalogActionRequest,
    payload: dict[str, Any],
) -> dict[str, Any]:
    headers = {
        "X-Actor-User-Id": str(body.customer_user_id),
        "X-Idempotency-Key": body.idempotency_key,
    }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=5),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def _do_post():
        return await client.post(
            f"{SERVICES[module_name]}/resources/{resource_type}",
            headers=headers,
            json={"user_id": str(body.customer_user_id), "payload": payload},
            timeout=5.0,
        )

    try:
        response = await _do_post()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Nao foi possivel registrar sua solicitacao agora.") from exc
    if response.status_code not in {200, 201}:
        error_payload = response.json()
        detail = error_payload.get("detail") if isinstance(error_payload, dict) else None
        raise HTTPException(status_code=502, detail=detail or "O modulo responsavel recusou a solicitacao.")
    result = response.json()
    if not isinstance(result, dict):
        raise HTTPException(status_code=502, detail="O modulo responsavel retornou uma resposta invalida.")
    return result


async def _service_json(
    method: Literal["GET", "POST"],
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> Any:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=1, max=5),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def _do_call():
        if method == "GET":
            return await client.get(url, headers=headers, timeout=timeout)
        else:
            return await client.post(url, headers=headers, json=payload or {}, timeout=timeout)

    try:
        response = await _do_call()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Um servico necessario esta temporariamente indisponivel.") from exc
    if response.status_code not in {200, 201}:
        error_payload = response.json()
        detail = error_payload.get("detail") if isinstance(error_payload, dict) else None
        raise HTTPException(status_code=502, detail=detail or "Um servico necessario recusou a operacao.")
    return response.json()


def _consumer_item(module_name: str, resource_type: str, item: dict[str, Any]) -> dict[str, Any]:
    payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
    kind = {
        ("marketplace", "orders"): "order",
        ("health", "appointments"): "appointment",
        ("services", "service_contracts"): "service",
    }[(module_name, resource_type)]
    amount = payload.get("total_brl") or payload.get("contracted_price_brl") or payload.get("visit_price_brl")
    return {
        "id": str(item.get("id") or ""),
        "kind": kind,
        "title": str(payload.get("offer_title") or payload.get("scope") or payload.get("care_line") or "Solicitacao Valley"),
        "status": str(item.get("status") or "created"),
        "amount_brl": str(amount) if amount not in (None, "") else None,
        "scheduled_at": payload.get("scheduled_at") or payload.get("requested_at"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }

def _configured_api_keys() -> dict[str, dict[str, object]]:
    """Parse API keys from ALL_IN_ONE_API_KEYS.

    Format: key:client_id:scope_a,scope_b;other:client:*
    """
    raw = os.getenv("ALL_IN_ONE_API_KEYS", "local-api-key:local-client:*")
    configured: dict[str, dict[str, object]] = {}
    for chunk in raw.split(";"):
        if not chunk.strip():
            continue
        parts = chunk.split(":", 2)
        if len(parts) != 3:
            continue
        key, client_id, scopes = (part.strip() for part in parts)
        if not key or not client_id:
            continue
        configured[key] = {
            "client_id": client_id,
            "scopes": {scope.strip() for scope in scopes.split(",") if scope.strip()},
        }
    return configured


def _verify_webhook_signature(body: bytes, signature: str | None) -> bool:
    if not signature or not signature.startswith("sha256="):
        return False
    digest = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, f"sha256={digest}")

async def rate_limiter(request: Request):
    """Rate limiting por IP usando Redis."""
    if redis_client is None:
        return None
    ip = request.client.host
    key = f"rate_limit:{ip}"
    limit = 100
    window = 60

    current = await redis_client.get(key)
    if current and int(current) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Tente novamente em um minuto.")
    
    pipe = redis_client.pipeline()
    await pipe.incr(key).expire(key, window).execute()


async def validate_api_key_edge(request: Request):
    """Valida API key para clientes de integracao e retorna contexto minimo."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key ausente.")

    key_info = _configured_api_keys().get(api_key)
    if key_info is None:
        raise HTTPException(status_code=401, detail="API key invalida.")

    scopes = key_info["scopes"]
    if "*" not in scopes and "gateway:read" not in scopes:
        raise HTTPException(status_code=403, detail="API key sem escopo gateway:read.")
    return key_info

async def validate_jwt_edge(request: Request):
    """Valida o JWT na borda para rotas protegidas."""
    if request.url.path.startswith(("/auth/", "/registrations", "/health", "/gateway")):
        return None
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente ou invalido.")
    
    token = auth_header.split(" ")[1]
    if jwt is None:
        raise HTTPException(status_code=503, detail="Validador JWT indisponivel.")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido.")


async def validate_catalog_action_token(request: Request) -> dict[str, Any]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Entre no Valley para continuar.")
    if jwt is None:
        raise HTTPException(status_code=503, detail="Validador JWT indisponivel.")
    try:
        return jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sua sessao expirou. Entre novamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Sessao invalida.")


async def proxy_request(service_url: str, request: Request, actor_payload: dict | None = None):
    """Proxy otimizado com injeção de contexto e tratamento de erros centralizado."""
    path = request.url.path
    query = request.url.query
    target_url = f"{service_url}{path}" + (f"?{query}" if query else "")

    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    if actor_payload:
        headers["X-Actor-User-Id"] = actor_payload.get("sub", "")

    try:
        req = client.build_request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body()
        )
        resp = await client.send(req, stream=True)
        return StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers=dict(resp.headers),
            background=BackgroundTask(resp.aclose)
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Erro de comunicação: {exc}")

def register_proxies():
    """Registra rotas de proxy dinamicamente."""
    for service_name, url in SERVICES.items():
        @app.api_route(
            f"/{service_name}/{{path:path}}", 
            methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
            dependencies=[Depends(rate_limiter)]
        )
        async def route_proxy(path: str, request: Request, service_url=url, actor=Depends(validate_jwt_edge)):
            return await proxy_request(service_url, request, actor)

register_proxies()

@app.post("/auth/{path:path}", dependencies=[Depends(rate_limiter)])
async def auth_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["identity"], request)

@app.post("/registrations", dependencies=[Depends(rate_limiter)])
async def registrations_proxy(request: Request):
    return await proxy_request(SERVICES["identity"], request)

@app.get("/gateway/catalog/offers", dependencies=[Depends(rate_limiter)])
async def aggregate_catalog_offers(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    q: str | None = None,
    category: str | None = None,
    offer_type: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    company_type: str | None = None,
    company_category: str | None = None,
    business_activity: str | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    availability: str | None = None,
    verified_only: bool = False,
) -> dict[str, Any]:
    """Agrega as vitrines publicas dos modulos no contrato unico do Valley."""
    query_values = locals()
    forwarded_params = {
        field: query_values[field]
        for field in CATALOG_QUERY_FIELDS
        if query_values.get(field) not in (None, "", False)
    }


    if verified_only:
        forwarded_params["verified_only"] = "true"

    async def fetch_module(module_name: str) -> tuple[str, list[dict[str, Any]], str | None]:
        url = f"{SERVICES[module_name]}/valley/catalog/search"

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.5, min=1, max=3),
            retry=retry_if_exception_type(httpx.RequestError),
            reraise=True
        )
        async def _do_fetch():
            return await client.get(url, params=forwarded_params, timeout=3.0)

        try:
            resp = await _do_fetch()
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return module_name, [item for item in data if isinstance(item, dict)], None
                return module_name, [], "resposta_invalida"
            return module_name, [], f"http_{resp.status_code}"
        except (httpx.RequestError, ValueError) as exc:
            return module_name, [], type(exc).__name__

    responses = await asyncio.gather(*(fetch_module(module) for module in CATALOG_SOURCE_MODULES), return_exceptions=True)

    clean_responses = []
    for module, result in zip(CATALOG_SOURCE_MODULES, responses, strict=True):
        if isinstance(result, Exception):
            clean_responses.append((module, [], type(result).__name__))
        else:
            clean_responses.append(result)

    merged = merge_catalog_offers([offers for _, offers, _ in clean_responses])
    failures = [
        {"module": module, "error": error}
        for module, _, error in clean_responses
        if error is not None
    ]
    page = merged[offset : offset + limit]
    return {
        "data": page,
        "total": len(merged),
        "limit": limit,
        "offset": offset,
        "facets": valley_facets(merged),
        "partial": bool(failures),
        "sources": [
            {"module": module, "status": "unavailable" if error else "ok", "offer_count": len(offers)}
            for module, offers, error in clean_responses
        ],
        "failures": failures,
    }


@app.get("/gateway/consumer/orders", dependencies=[Depends(rate_limiter)])
async def get_consumer_orders(
    token_payload: dict[str, Any] = Depends(validate_catalog_action_token)
) -> dict[str, Any]:
    """Retorna historico publico normalizado sem expor payloads internos."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Sessao invalida.")

    headers = {"X-Actor-User-Id": str(user_id)}

    async def fetch_resource(module_name: str, resource_type: str) -> tuple[list[dict[str, Any]], str | None]:
        url = f"{SERVICES[module_name]}/resources/{resource_type}"

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.5, min=1, max=3),
            retry=retry_if_exception_type(httpx.RequestError),
            reraise=True
        )
        async def _do_fetch():
            return await client.get(url, headers=headers, timeout=3.0)

        try:
            resp = await _do_fetch()
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return [
                        _consumer_item(module_name, resource_type, item)
                        for item in data
                        if isinstance(item, dict)
                    ], None
                return [], "resposta_invalida"
            return [], f"http_{resp.status_code}"
        except (httpx.RequestError, ValueError) as exc:
            return [], type(exc).__name__

    results = await asyncio.gather(
        fetch_resource("marketplace", "orders"),
        fetch_resource("health", "appointments"),
        fetch_resource("services", "service_contracts"),
        return_exceptions=True
    )

    all_items: list[dict[str, Any]] = []
    failures = []
    for result, module_name in zip(
        results,
        ("marketplace", "health", "services"),
        strict=True,
    ):
        if isinstance(result, Exception):
            failures.append({"module": module_name, "error": type(result).__name__})
        else:
            items, error = result
            all_items.extend(items)
            if error:
                failures.append({"module": module_name, "error": error})

    all_items.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)

    return {
        "data": all_items,
        "total": len(all_items),
        "partial": bool(failures),
        "failures": failures,
    }


@app.post(
    "/gateway/consumer/orders/{order_id}/support",
    status_code=201,
    dependencies=[Depends(rate_limiter)],
)
async def create_order_support_case(
    order_id: UUID,
    body: SupportCaseRequest,
    token_payload: dict[str, Any] = Depends(validate_catalog_action_token),
) -> dict[str, Any]:
    user_id = str(token_payload.get("sub") or "")
    headers = {"X-Actor-User-Id": user_id}
    order = await _service_json(
        "GET",
        f"{SERVICES['marketplace']}/resources/orders/{order_id}",
        headers=headers,
    )
    if not isinstance(order, dict) or str(order.get("user_id") or "") != user_id:
        raise HTTPException(status_code=403, detail="Pedido nao pertence ao consumidor autenticado.")
    if order.get("status") not in {"paid", "accepted", "in_progress", "delivered", "completed"}:
        raise HTTPException(status_code=409, detail="Suporte fica disponivel apos a confirmacao do pedido.")

    payload = order.get("payload") if isinstance(order.get("payload"), dict) else {}
    support_case = await _service_json(
        "POST",
        f"{SERVICES['marketplace']}/valley/orders/{order_id}/support",
        headers={
            **headers,
            "X-Idempotency-Key": body.idempotency_key,
        },
        payload={
            "kind": body.kind,
            "subject": body.subject,
            "message": body.message,
            "desired_resolution": body.desired_resolution,
            "idempotency_key": body.idempotency_key,
        },
    )
    if not isinstance(support_case, dict):
        raise HTTPException(status_code=502, detail="O Marketplace retornou um caso invalido.")
    return {
        "id": str(support_case.get("id") or ""),
        "order_id": str(order_id),
        "kind": body.kind,
        "status": str(support_case.get("status") or "open"),
        "message": str(support_case.get("message") or "Caso registrado."),
        "support_context": {
            "offer_id": payload.get("offer_id") or payload.get("valley_offer_id"),
            "store_id": payload.get("store_id"),
            "company_id": payload.get("company_id"),
        },
    }


@app.post(
    "/gateway/consumer/orders/{order_id}/reviews",
    status_code=201,
    dependencies=[Depends(rate_limiter)],
)
async def create_consumer_review(
    order_id: UUID,
    body: ConsumerReviewRequest,
    token_payload: dict[str, Any] = Depends(validate_catalog_action_token),
) -> dict[str, Any]:
    """Registra uma avaliacao imutavel somente apos entrega ou conclusao."""
    user_id = str(token_payload.get("sub") or "")
    headers = {"X-Actor-User-Id": user_id}
    order = await _service_json(
        "GET",
        f"{SERVICES['marketplace']}/resources/orders/{order_id}",
        headers=headers,
    )
    if not isinstance(order, dict) or str(order.get("user_id") or "") != user_id:
        raise HTTPException(status_code=403, detail="Pedido nao pertence ao consumidor autenticado.")
    if order.get("status") not in {"delivered", "completed"}:
        raise HTTPException(status_code=409, detail="A avaliacao fica disponivel apos a conclusao do pedido.")

    payload = order.get("payload") if isinstance(order.get("payload"), dict) else {}
    review = await _service_json(
        "POST",
        f"{SERVICES['marketplace']}/resources/reviews",
        headers={
            **headers,
            "X-Idempotency-Key": body.idempotency_key,
        },
        payload={
            "user_id": user_id,
            "entity_id": payload.get("store_id") or payload.get("business_id"),
            "payload": {
                "order_id": str(order_id),
                "store_id": payload.get("store_id"),
                "business_id": payload.get("business_id"),
                "offer_id": payload.get("offer_id") or payload.get("valley_offer_id"),
                "rating": body.rating,
                "comment": body.comment,
                "moderation_status": "published",
            },
        },
    )
    if not isinstance(review, dict):
        raise HTTPException(status_code=502, detail="O Marketplace retornou uma avaliacao invalida.")
    return {
        "id": str(review.get("id") or ""),
        "order_id": str(order_id),
        "rating": body.rating,
        "comment": body.comment,
        "status": str(review.get("status") or "published"),
        "message": "Avaliacao publicada. Obrigado por compartilhar sua experiencia.",
    }


@app.get("/gateway/insights/commercial", dependencies=[Depends(rate_limiter)])
async def commercial_insights() -> dict[str, Any]:
    marketplace = await _service_json(
        "GET",
        f"{SERVICES['marketplace']}/valley/insights/commercial",
        headers={"X-Actor-User-Id": str(UUID(int=0))},
    )
    crm = await _service_json(
        "GET",
        f"{SERVICES['crm']}/status",
        headers={"X-Actor-User-Id": str(UUID(int=1)), "X-Actor-Roles": "auditor"},
    )
    bi = await _service_json(
        "GET",
        f"{SERVICES['bi']}/status",
        headers={"X-Actor-User-Id": str(UUID(int=2)), "X-Actor-Roles": "auditor"},
    )
    if not isinstance(marketplace, dict):
        raise HTTPException(status_code=502, detail="Resumo comercial indisponivel no Marketplace.")
    if not isinstance(crm, dict) or not isinstance(bi, dict):
        raise HTTPException(status_code=502, detail="Resumo comercial indisponivel nos modulos CRM/BI.")
    return {
        **marketplace,
        "crm_records": crm.get("records", 0),
        "crm_audit_events": crm.get("audit_events", 0),
        "crm_outbox_events": crm.get("outbox_events", 0),
        "bi_records": bi.get("records", 0),
        "bi_audit_events": bi.get("audit_events", 0),
        "bi_outbox_events": bi.get("outbox_events", 0),
    }


@app.post("/gateway/catalog/actions", status_code=201, dependencies=[Depends(rate_limiter)])
async def create_catalog_action(
    body: CatalogActionRequest,
    token_payload: dict[str, Any] = Depends(validate_catalog_action_token),
) -> dict[str, Any]:
    """Cria o primeiro registro operacional sem concluir pagamento ou atendimento."""
    if str(token_payload.get("sub") or "") != str(body.customer_user_id):
        raise HTTPException(status_code=403, detail="A sessao nao pertence ao usuario da solicitacao.")
    offer = await _fetch_catalog_offer(body.offer_id)
    expected_action = str(offer.get("consumer_action") or "")
    if expected_action and expected_action != body.action:
        raise HTTPException(status_code=409, detail="A acao solicitada nao corresponde a esta oferta.")

    price = str(offer.get("price_amount") or offer.get("price_brl") or "0.00")
    common = {
        "valley_offer_id": body.offer_id,
        "source_module": offer.get("source_module"),
        "source_resource_type": offer.get("source_resource_type"),
        "source_entity_id": offer.get("source_entity_id"),
        "seller_user_id": offer.get("seller_user_id"),
        "business_id": offer.get("business_id"),
        "consumer_note": body.note,
    }

    if body.action == "buy":
        store_id = offer.get("business_id") or offer.get("seller_user_id") or offer.get("source_entity_id")
        if not store_id:
            raise HTTPException(status_code=409, detail="A oferta ainda nao possui vendedor operacional vinculado.")
        resource = await _create_catalog_resource(
            "marketplace",
            "orders",
            body,
            {
                **common,
                "offer_title": offer.get("title"),
                "offer_id": body.offer_id,
                "company_id": offer.get("business_id"),
                "store_id": str(store_id),
                "escrow_id": f"pending:{body.idempotency_key}",
                "total_brl": price,
                "items": [
                    {
                        "offer_id": body.offer_id,
                        "quantity": body.quantity,
                        "unit_brl": price,
                    }
                ],
            },
        )
        return {
            "status": "created",
            "action": body.action,
            "target_module": "marketplace",
            "resource_type": "orders",
            "resource_id": resource.get("id"),
            "next_step": "payment_required",
            "message": "Pedido criado. O pagamento sera confirmado na proxima etapa.",
            "payment_intent": {
                "amount": price,
                "order_id": resource.get("id"),
            }
        }

    if body.action == "book" and offer.get("source_module") == "health":
        if not body.scheduled_at:
            raise HTTPException(status_code=422, detail="Informe a data e o horario desejados.")
        professional_id = offer.get("seller_user_id") or offer.get("source_entity_id")
        if not professional_id:
            raise HTTPException(status_code=409, detail="A oferta ainda nao possui profissional vinculado.")
        resource = await _create_catalog_resource(
            "health",
            "appointments",
            body,
            {
                **common,
                "offer_title": offer.get("title"),
                "offer_id": body.offer_id,
                "company_id": offer.get("business_id"),
                "patient_id": str(body.customer_user_id),
                "professional_user_id": str(professional_id),
                "scheduled_at": body.scheduled_at,
                "care_line": offer.get("business_activity_id") or "atendimento_valley",
            },
        )
        target_module = "health"
        resource_type = "appointments"
    else:
        provider_id = offer.get("seller_user_id") or offer.get("source_entity_id")
        if not provider_id:
            raise HTTPException(status_code=409, detail="A oferta ainda nao possui prestador vinculado.")
        resource = await _create_catalog_resource(
            "services",
            "service_contracts",
            body,
            {
                **common,
                "offer_title": offer.get("title"),
                "offer_id": body.offer_id,
                "company_id": offer.get("business_id"),
                "provider_user_id": str(provider_id),
                "escrow_id": f"pending:{body.idempotency_key}",
                "visit_price_brl": price,
                "contracted_price_brl": price,
                "scope": body.note or offer.get("title") or "Solicitacao pelo Valley",
                "scheduled_at": body.scheduled_at,
            },
        )
        target_module = "services"
        resource_type = "service_contracts"

    return {
        "status": "created",
        "action": body.action,
        "target_module": target_module,
        "resource_type": resource_type,
        "resource_id": resource.get("id"),
        "next_step": "provider_confirmation",
        "message": "Solicitacao enviada. Voce recebera a confirmacao do prestador.",
    }


@app.post("/gateway/payments/sandbox/authorize", dependencies=[Depends(rate_limiter)])
async def authorize_catalog_payment(
    body: CatalogPaymentRequest,
    token_payload: dict[str, Any] = Depends(validate_catalog_action_token),
) -> dict[str, Any]:
    """Autoriza Pix sandbox e marca o pedido pago somente apos escrow aceito."""
    user_id = str(token_payload.get("sub") or "")
    actor_headers = {"X-Actor-User-Id": user_id}
    order = await _service_json(
        "GET",
        f"{SERVICES['marketplace']}/resources/orders/{body.order_id}",
        headers=actor_headers,
    )
    if not isinstance(order, dict) or str(order.get("user_id") or "") != user_id:
        raise HTTPException(status_code=403, detail="Pedido nao pertence ao consumidor autenticado.")
    if order.get("status") == "paid":
        return {
            "status": "paid",
            "order_id": str(body.order_id),
            "message": "Pagamento ja confirmado anteriormente.",
        }
    if order.get("status") != "created":
        raise HTTPException(status_code=409, detail="Este pedido nao aceita pagamento no estado atual.")

    payload = order.get("payload") if isinstance(order.get("payload"), dict) else {}
    amount = str(payload.get("total_brl") or "")
    beneficiary = str(payload.get("seller_user_id") or payload.get("store_id") or "")
    if not amount or not beneficiary:
        raise HTTPException(status_code=409, detail="Pedido sem dados financeiros completos.")

    internal_headers = {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": "compliance_officer",
        "X-MFA-Verified": "true",
    }
    payment_id = f"order:{body.order_id}"
    pix = await _service_json(
        "POST",
        f"{SERVICES['finance']}/integrations/sandbox/psp/pix/authorize",
        headers=internal_headers,
        payload={
            "payment_id": payment_id,
            "payer_id": user_id,
            "amount_brl": amount,
            "idempotency_key": body.idempotency_key,
        },
    )
    if not isinstance(pix, dict) or pix.get("status") != "authorized":
        raise HTTPException(status_code=409, detail="Pagamento Pix nao foi autorizado.")

    escrow_reference = f"order-{body.order_id}"
    escrow = await _service_json(
        "POST",
        f"{SERVICES['finance']}/integrations/sandbox/psp/escrows",
        headers=internal_headers,
        payload={
            "escrow_id": escrow_reference,
            "payer_id": user_id,
            "beneficiary_id": beneficiary,
            "amount_brl": amount,
        },
    )
    if not isinstance(escrow, dict) or escrow.get("status") != "held":
        raise HTTPException(status_code=409, detail="Nao foi possivel proteger o pagamento em escrow.")

    paid = await _service_json(
        "POST",
        f"{SERVICES['marketplace']}/resources/orders/{body.order_id}/actions/pay",
        headers=actor_headers,
        payload={
            "reason": "Pix sandbox autorizado e valor protegido em escrow.",
            "payload": {
                "payment_provider": "finance_pix_psp",
                "provider_environment": "sandbox",
                "payment_reference": pix.get("reference_id"),
                "escrow_reference": escrow.get("reference_id"),
            },
        },
    )
    return {
        "status": str(paid.get("status") if isinstance(paid, dict) else "paid"),
        "order_id": str(body.order_id),
        "provider_environment": "sandbox",
        "message": "Pagamento sandbox autorizado e protegido ate a conclusao do pedido.",
    }

@app.get("/gateway/telemetry/outbox")
async def outbox_telemetry(limit: int = 100):
    """Monitoramento unificado de Outbox Parada e Eventos em Backoff"""
    from modules.shared.outbox_dispatcher import OutboxDispatcher, OutboxSettings
    
    def fetch_metrics():
        settings = OutboxSettings.from_environment()
        dispatcher = OutboxDispatcher(settings)
        try:
            return dispatcher.collect_metrics()
        finally:
            dispatcher.close()

    try:
        metrics = await asyncio.to_thread(fetch_metrics)
        return {
            "status": "healthy",
            "pending": metrics.pending,
            "due": metrics.due,
            "published": metrics.published,
            "failed_retryable": metrics.failed_retryable,
            "max_retry_count": metrics.max_retry_count,
            "oldest_pending_age_seconds": metrics.oldest_pending_age_seconds,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
            "pending": 0,
            "due": 0,
            "published": 0,
            "failed_retryable": 0,
            "max_retry_count": 0,
            "oldest_pending_age_seconds": 0,
        }


@app.get("/gateway/status")
async def gateway_status():
    return {
        "service": "API Hub Gateway",
        "status": "active",
        "security": "JWT_EDGE_VALIDATION_ENABLED",
        "rate_limit": "REDIS_IP_BASED_ENABLED",
        "routes": list(SERVICES.keys())
    }


@app.get("/gateway/api-key/check", dependencies=[Depends(rate_limiter)])
async def gateway_api_key_check(key_info: dict = Depends(validate_api_key_edge)):
    return {
        "status": "valid",
        "client_id": key_info["client_id"],
        "scopes": sorted(key_info["scopes"]),
    }


@app.post("/gateway/webhooks/verify")
async def gateway_webhook_verify(request: Request):
    body = await request.body()
    signature = request.headers.get("X-All-In-One-Signature")
    if not _verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Assinatura de webhook invalida.")
    return {"status": "valid", "algorithm": "hmac-sha256"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/tracking/{delivery_id}")
async def tracking_websocket(websocket: WebSocket, delivery_id: str):
    await manager.connect(websocket)
    try:
        await websocket.send_json({"delivery_id": delivery_id, "status": "connected", "lat": -23.5505, "lng": -46.6333})
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"delivery_id": delivery_id, "update": data, "type": "ping_ack"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
@app.websocket("/ws/webrtc/{session_id}")
async def webrtc_signaling(websocket: WebSocket, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            for connection in manager.active_connections:
                if connection != websocket:
                    await connection.send_json({"session_id": session_id, "signal": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
