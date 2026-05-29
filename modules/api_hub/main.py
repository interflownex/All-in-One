import redis.asyncio as redis
import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.background import BackgroundTask
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from shared.security import Actor

app = create_module_app("api_hub")

# Configurações
SERVICES = {
    "identity": os.getenv("IDENTITY_SERVICE_URL", "http://identity:8000"),
    "finance": os.getenv("FINANCE_SERVICE_URL", "http://finance:8000"),
}
JWT_SECRET = os.getenv("ALL_IN_ONE_JWT_SECRET", "local-secret-key-change-in-production")
REDIS_URL = os.getenv("ALL_IN_ONE_REDIS_URL", "redis://redis:6379/0")

# Clientes
client = httpx.AsyncClient()
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def rate_limiter(request: Request):
    """Rate limiting por IP usando Redis."""
    ip = request.client.host
    key = f"rate_limit:{ip}"
    limit = 100 # requisições
    window = 60 # segundos
    
    current = await redis_client.get(key)
    if current and int(current) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Tente novamente em um minuto.")
    
    pipe = redis_client.pipeline()
    await pipe.incr(key).expire(key, window).execute()

async def validate_jwt_edge(request: Request):
    """Valida o JWT na borda para rotas protegidas."""
    if request.url.path.startswith(("/auth/", "/registrations", "/health", "/gateway")):
        return None
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente ou invalido.")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido.")

async def proxy_request(service_url: str, request: Request, actor_payload: dict | None = None):
    """Proxy com injeção de contexto de ator."""
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    target_url = f"{service_url}{url.path}"
    if url.query:
        target_url += f"?{url.query}"

    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Injeta o X-Actor-User-Id se o JWT foi validado na borda
    if actor_payload:
        headers["X-Actor-User-Id"] = actor_payload.get("sub")

    req = client.build_request(
        method=request.method,
        url=target_url,
        headers=headers,
        content=await request.body()
    )
    
    try:
        resp = await client.send(req, stream=True)
        return StreamingResponse(
            resp.aiter_raw(),
            status_code=resp.status_code,
            headers=dict(resp.headers),
            background=BackgroundTask(resp.aclose)
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Erro de comunicacao com microservico: {exc}")

# Roteamento Protegido com Rate Limit e Validação JWT
@app.api_route(
    "/identity/{path:path}", 
    methods=["GET", "POST", "PATCH", "DELETE"],
    dependencies=[Depends(rate_limiter)]
)
async def identity_proxy(path: str, request: Request, actor=Depends(validate_jwt_edge)):
    return await proxy_request(SERVICES["identity"], request, actor)

# Roteamento Aberto (Apenas Rate Limit)
@app.post("/auth/{path:path}", dependencies=[Depends(rate_limiter)])
async def auth_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["identity"], request)

@app.post("/registrations", dependencies=[Depends(rate_limiter)])
async def registrations_proxy(request: Request):
    return await proxy_request(SERVICES["identity"], request)

# Roteamento para Finanças
@app.api_route(
    "/finance/{path:path}", 
    methods=["GET", "POST", "PATCH", "DELETE"],
    dependencies=[Depends(rate_limiter)]
)
async def finance_proxy(path: str, request: Request, actor=Depends(validate_jwt_edge)):
    return await proxy_request(SERVICES["finance"], request, actor)

@app.get("/gateway/status")
async def gateway_status():
    return {
        "service": "API Hub Gateway",
        "status": "active",
        "security": "JWT_EDGE_VALIDATION_ENABLED",
        "rate_limit": "REDIS_IP_BASED_ENABLED",
        "routes": list(SERVICES.keys())
    }


