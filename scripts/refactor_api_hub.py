import re
from pathlib import Path

file_path = Path("modules/api_hub/main.py")
content = file_path.read_text(encoding="utf-8")

# Extract the SERVICES definition and replace it
services_pattern = re.compile(r"SERVICES\s*=\s*\{.*?\}", re.DOTALL)

new_services = """MODULES = [
    "ai_core", "bi", "bpm", "business", "crm", "delivery", "document", "erp",
    "finance", "health", "hr", "identity", "jobs", "legal", "marketplace",
    "mobility", "permissions", "property", "riders", "services", "stock",
    "tms", "wms"
]

SERVICES = {
    mod: os.getenv(f"{mod.upper()}_SERVICE_URL", f"http://{mod}:8000")
    for mod in MODULES
}"""

content = services_pattern.sub(new_services, content)

# Remove the hardcoded routes
routes_start = content.find("# Roteamento Protegido")
if routes_start != -1:
    routes_end = content.find('@app.get("/gateway/status")')
    if routes_end != -1:
        new_routes = """# Roteamento Protegido Dinâmico para Módulos
def create_proxy_route(service_name: str):
    @app.api_route(
        f"/{service_name}/{{path:path}}", 
        methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
        dependencies=[Depends(rate_limiter)]
    )
    async def route_proxy(path: str, request: Request, actor=Depends(validate_jwt_edge)):
        return await proxy_request(SERVICES[service_name], request, actor)

for service in SERVICES.keys():
    if service != "identity":
        create_proxy_route(service)

# Roteamento Aberto (Apenas Rate Limit) - Identity
@app.api_route(
    "/identity/{path:path}", 
    methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
    dependencies=[Depends(rate_limiter)]
)
async def identity_proxy(path: str, request: Request, actor=Depends(validate_jwt_edge)):
    return await proxy_request(SERVICES["identity"], request, actor)

@app.post("/auth/{path:path}", dependencies=[Depends(rate_limiter)])
async def auth_proxy(path: str, request: Request):
    return await proxy_request(SERVICES["identity"], request)

@app.post("/registrations", dependencies=[Depends(rate_limiter)])
async def registrations_proxy(request: Request):
    return await proxy_request(SERVICES["identity"], request)

"""
        content = content[:routes_start] + new_routes + content[routes_end:]

file_path.write_text(content, encoding="utf-8")
print("Rotas dinâmicas do API Hub aplicadas com sucesso!")
