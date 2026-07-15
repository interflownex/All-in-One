import pytest
import json
import subprocess
import sys
import time
import socket
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import jwt


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE4_ACTOR_ID = "11111111-1111-4111-8111-111111111111"
PHASE4_BUSINESS_ID = "22222222-2222-4222-8222-222222222222"
PHASE4_JWT_SECRET = "phase4-live-e2e-secret-with-32-bytes-minimum"
PHASE4_HTTP_TIMEOUT_SECONDS = 60
PLAYWRIGHT_LAUNCH_TIMEOUT_MS = 300_000


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    launch_options = {"timeout": PLAYWRIGHT_LAUNCH_TIMEOUT_MS}
    if pytestconfig.getoption("--headed"):
        launch_options["headless"] = False
    browser_channel = pytestconfig.getoption("--browser-channel")
    if browser_channel:
        launch_options["channel"] = browser_channel
    slowmo = pytestconfig.getoption("--slowmo")
    if slowmo:
        launch_options["slow_mo"] = slowmo
    return launch_options


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def wait_for_http(port: int, timeout: int = 15, process: subprocess.Popen | None = None) -> bool:
    """Wait until the expected Vite server returns a valid HTTP response."""
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if process is not None and process.poll() is not None:
            return False
        try:
            with urlopen(f"http://127.0.0.1:{port}", timeout=2) as response:
                if response.status == 200 and b'<div id="root">' in response.read():
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def wait_for_url(url: str, timeout: int = 15, process: subprocess.Popen | None = None) -> bool:
    start_time = time.time()
    while time.time() - start_time <= timeout:
        if process is not None and process.poll() is not None:
            return False
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def start_vite_server(app_directory: str, env: dict[str, str] | None = None) -> tuple[subprocess.Popen, str]:
    port = free_port()
    server_url = f"http://127.0.0.1:{port}"
    process_env = os.environ.copy()
    if env:
        process_env.update({key: value.format(server_url=server_url) for key, value in env.items()})
    startup_timeout = int(process_env.get("VITE_START_TIMEOUT_SECONDS", "120"))
    process = subprocess.Popen(
        f"npm run dev -- --port {port} --strictPort --host 127.0.0.1",
        cwd=app_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
        env=process_env,
    )
    if not wait_for_http(port, timeout=startup_timeout, process=process):
        process.terminate()
        raise RuntimeError(f"Vite nao respondeu corretamente na porta {port} em {startup_timeout}s.")
    return process, server_url


def start_python_http_server(
    app_directory: Path,
    port: int,
    env: dict[str, str],
    health_path: str = "/health",
) -> tuple[subprocess.Popen, str]:
    server_url = f"http://127.0.0.1:{port}"
    process_env = os.environ.copy()
    process_env.update(env)
    startup_timeout = int(process_env.get("FASTAPI_START_TIMEOUT_SECONDS", "120"))
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=app_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=process_env,
    )
    if not wait_for_url(f"{server_url}{health_path}", timeout=startup_timeout, process=process):
        process.terminate()
        raise RuntimeError(f"Servidor FastAPI nao respondeu corretamente em {server_url} em {startup_timeout}s.")
    return process, server_url


def stop_process(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


PHASE4_ROUTE_PAYLOADS = {
    ("identity", "users"): {
        "full_name": "Perfil Playwright",
        "email": "phase4-user@example.test",
        "password_hash": "phase4-live-password-hash",
        "document_cpf": "CPF-PHASE4",
    },
    ("riders", "rider_profiles"): {
        "cnh_number_hash": "phase4-cnh-hash",
        "cnh_category": "AB",
        "wallet_id": "wallet-phase4-rider",
        "name": "Registro Playwright",
    },
    ("riders", "vehicles"): {
        "rider_profile_id": "phase4-rider-profile",
        "type": "moto",
        "license_plate": "E2E4A12",
    },
    ("delivery", "delivery_requests"): {
        "service_type": "last_mile",
        "origin": {"lat": -23.55, "lng": -46.63},
        "destination": {"lat": -23.56, "lng": -46.64},
    },
    ("mobility", "rides"): {
        "origin": {"lat": -23.55, "lng": -46.63},
        "destination": {"lat": -23.57, "lng": -46.65},
        "vehicle_type": "car",
    },
    ("mobility", "tickets"): {
        "route_code": "MOB-E2E",
        "amount_brl": "4.40",
        "qr_token_hash": "phase4-ticket-token",
        "nfc_token_hash": "phase4-nfc-token",
    },
    ("services", "providers"): {"category": "home_services", "name": "Prestador Playwright"},
    ("services", "service_contracts"): {"visit_price_brl": "120.00", "scope": "Visita Playwright"},
    ("finance", "escrows"): {
        "wallet_id": "wallet-phase4",
        "beneficiary_user_id": PHASE4_ACTOR_ID,
        "amount_brl": "120.00",
    },
    ("finance", "wallets"): {"wallet_type": "consumer", "label": "Wallet Playwright"},
    ("marketplace", "orders"): {
        "store_id": "store-phase4-user",
        "total_brl": "99.90",
        "items": [{"sku": "SKU-PHASE4", "quantity": 1, "unit_brl": "99.90"}],
    },
    ("business", "companies"): {
        "cnpj": "12345678000195",
        "root_cnpj": "12345678",
        "legal_name": "Empresa Business Playwright",
        "legal_representative_user_id": PHASE4_ACTOR_ID,
    },
    ("business", "catalog_offers"): {
        "title": "Oferta Business Playwright",
        "offer_type": "subscription",
        "consumer_category": "professional",
        "company_type": "recruiter",
        "company_category": "jobs",
        "business_activity_id": "activity-phase4-jobs",
        "source_module": "jobs",
        "source_resource_type": "job_postings",
        "price_brl": "199.90",
    },
    ("api_hub", "api_clients"): {
        "client_name": "Cliente API Hub Playwright",
        "scopes": ["gateway:read", "jobs:manage"],
        "client_id_hash": "phase4-api-client-id-hash",
        "secret_reference": "secret://phase4/api-client",
    },
    ("api_hub", "api_keys"): {
        "key_name": "Chave API Hub Playwright",
        "key_hash": "phase4-api-key-hash",
        "key_hint": "play...wright",
        "scopes": ["gateway:read"],
        "expires_at": "2027-07-13T00:00:00Z",
    },
    ("api_hub", "webhooks"): {
        "target_url": "https://webhook.playwright.example/events",
        "event_patterns": ["business.company.approved", "jobs.job_posting.published"],
        "signing_secret_reference": "secret://phase4/webhook",
    },
    ("api_hub", "integration_runs"): {
        "integration_type": "apigee_api_hub_sync",
        "provider_name": "Apigee API Hub Playwright",
        "log_summary": "Execucao administrativa viva sem credencial externa bruta.",
    },
    ("jobs", "job_postings"): {
        "company_id": PHASE4_BUSINESS_ID,
        "company_status": "active",
        "title": "Vaga Playwright",
        "description": "Jornada viva compartilhada dos shells User e Business",
    },
    ("jobs", "resumes"): {
        "headline": "Curriculo Business Playwright",
        "recruiter_visibility": "business_recruiters",
    },
    ("jobs", "applications"): {
        "resume_id": "33333333-3333-4333-8333-333333333333",
        "job_posting_id": "44444444-4444-4444-8444-444444444444",
    },
    ("erp", "fiscal_documents"): {
        "document_type": "Relatorio de Giro Fiscal Playwright",
        "amount_brl": "3490.75",
        "description": "Documento ERP vivo para conciliacao Business",
    },
    ("bi", "dashboards"): {
        "name": "Dashboard Giro de Estoque Playwright",
        "definition": {"metric": "inventory_turnover", "period": "monthly"},
    },
    ("wms", "warehouses"): {
        "name": "CD Regional Playwright",
        "description": "Estoque local vivo para operacao Business",
    },
    ("tms", "freights"): {
        "freight_brl": "89.90",
        "title": "Frete Regional Playwright",
        "description": "Transporte vivo para pedido Business",
    },
    ("crm", "opportunities"): {
        "title": "Oportunidade B2B Playwright",
        "expected_value_brl": "1299.00",
        "description": "Pipeline vivo para lojista Business",
    },
    ("bpm", "processes"): {
        "process_key": "onboarding-business-playwright",
        "title": "Fluxo BPM Playwright",
    },
    ("document", "documents"): {
        "storage_provider": "private_vault",
        "storage_bucket": "all-in-one-private-documents",
        "storage_key": "vault/document/phase4/doc.pdf",
        "file_sha256": "6f1ed002ab5595859014ebf0951522d9f59b7a3df43f1f4f13ff2f90a61f1f8c",
        "kms_key_version": "kms://document/v1",
        "filename": "doc.pdf",
        "content_type": "application/pdf",
    },
    ("hr", "employees"): {
        "company_id": PHASE4_BUSINESS_ID,
        "employment_type": "clt",
        "name": "Colaborador HR Playwright",
    },
    ("legal", "cases"): {
        "case_number": "LEGAL-PLAYWRIGHT-001",
        "title": "Caso Legal Playwright",
        "risk_brl": "700.00",
    },
    ("property", "properties"): {
        "address": "Rua Playwright, 100",
        "property_type": "commercial",
        "name": "Imovel Property Playwright",
    },
    ("vision", "devices"): {
        "device_fingerprint": "vision-device-playwright",
        "name": "Camera Vision Playwright",
    },
    ("ai_core", "moderation_decisions"): {
        "module": "business",
        "risk_score": "0.21",
        "title": "Decisao AI Core Playwright",
    },
    ("health", "patients"): {"health_identifier": "patient-phase4", "name": "Paciente Playwright"},
    ("health", "appointments"): {"scheduled_at": "2026-07-12T12:00:00Z", "care_line": "Consulta"},
    ("identity", "consents"): {
        "user_id": PHASE4_ACTOR_ID,
        "document_version": "2026-07-12",
        "consent_type": "lgpd",
        "purpose": "playwright_phase4",
        "accepted_at": "2026-07-12T12:00:00Z",
    },
}


def _route_to_resource(route: str) -> tuple[str, str]:
    module_name, resources_segment, resource_type, *_ = route.strip("/").split("/")
    if resources_segment != "resources":
        raise RuntimeError(f"Rota API Hub inesperada para fixture viva: {route}")
    return module_name, resource_type


def _post_json(url: str, payload: dict[str, object], headers: dict[str, str]) -> dict[str, object]:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", **headers},
            method="POST",
        )
        try:
            with urlopen(request, timeout=PHASE4_HTTP_TIMEOUT_SECONDS) as response:
                if response.status not in {200, 201}:
                    raise RuntimeError(f"POST {url} retornou HTTP {response.status}.")
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code < 500 or attempt == 3:
                raise RuntimeError(f"POST {url} retornou HTTP {exc.code}: {detail}") from exc
            last_error = RuntimeError(f"POST {url} retornou HTTP {exc.code}: {detail}")
        except URLError as exc:
            if attempt == 3:
                raise RuntimeError(f"POST {url} falhou: {exc}") from exc
            last_error = exc
        except TimeoutError as exc:
            if attempt == 3:
                raise RuntimeError(f"POST {url} excedeu {PHASE4_HTTP_TIMEOUT_SECONDS}s.") from exc
            last_error = exc
        time.sleep(0.5 * attempt)
    if last_error:
        raise RuntimeError(f"POST {url} falhou: {last_error}") from last_error
    raise RuntimeError(f"POST {url} falhou sem detalhe.")


def _seed_phase4_resources(api_hub_url: str, routes: list[str], token: str) -> dict[tuple[str, str], dict[str, object]]:
    headers = {"Authorization": f"Bearer {token}"}
    created: dict[tuple[str, str], dict[str, object]] = {}
    for index, route in enumerate(routes, start=1):
        module_name, resource_type = _route_to_resource(route)
        payload = PHASE4_ROUTE_PAYLOADS[(module_name, resource_type)]
        target_path = f"/resources/{resource_type}" if module_name == "api_hub" else f"/{module_name}/resources/{resource_type}"
        request_headers = {**headers, "X-Idempotency-Key": f"phase4-{module_name}-{resource_type}-{index}"}
        created[(module_name, resource_type)] = _post_json(
            f"{api_hub_url}{target_path}",
            {"user_id": PHASE4_ACTOR_ID, "payload": payload},
            request_headers,
        )
    return created


def start_phase4_live_stack(
    app_directory: str,
    routes: list[str],
    storage_dir: Path,
    publish_job_postings: bool = False,
) -> tuple[list[subprocess.Popen], str]:
    api_port = free_port()
    api_hub_url = f"http://127.0.0.1:{api_port}"
    token = jwt.encode(
        {
            "sub": PHASE4_ACTOR_ID,
            "roles": ["compliance_officer", "auditor", "owner", "recruiter"],
            "scopes": ["riders:approve", "health:approve", "jobs:manage", "jobs:resumes:read"],
            "mfa_verified": True,
            "business_id": PHASE4_BUSINESS_ID,
            "business_status": "active",
        },
        PHASE4_JWT_SECRET,
        algorithm="HS256",
    )
    processes: list[subprocess.Popen] = []
    module_urls: dict[str, str] = {}

    try:
        for module_name in sorted({_route_to_resource(route)[0] for route in routes}):
            if module_name == "api_hub":
                continue
            process, module_url = start_python_http_server(
                REPO_ROOT / "modules" / module_name,
                free_port(),
                {
                    "ALL_IN_ONE_STORAGE_DIR": str(storage_dir / "modules"),
                    "ALL_IN_ONE_ENV": "test",
                    "FASTAPI_START_TIMEOUT_SECONDS": "240",
                    "GOOGLE_INTEGRATIONS_ENABLED": "false",
                    "GOOGLE_CLOUD_ENABLED": "false",
                },
            )
            processes.append(process)
            module_urls[module_name] = module_url

        vite_process, vite_url = start_vite_server(
            app_directory,
            {
                "VITE_API_HUB_URL": api_hub_url,
                "VITE_API_HUB_TOKEN": token,
                "VITE_START_TIMEOUT_SECONDS": "240",
            },
        )
        processes.append(vite_process)

        api_env = {
            "ALL_IN_ONE_STORAGE_DIR": str(storage_dir / "api_hub"),
            "ALL_IN_ONE_ENV": "test",
            "ALL_IN_ONE_JWT_SECRET": PHASE4_JWT_SECRET,
            "ALL_IN_ONE_CORS_ORIGINS": vite_url,
            "FASTAPI_START_TIMEOUT_SECONDS": "240",
            "GOOGLE_INTEGRATIONS_ENABLED": "false",
            "GOOGLE_CLOUD_ENABLED": "false",
        }
        api_env.update({f"{module_name.upper()}_SERVICE_URL": url for module_name, url in module_urls.items()})
        api_process, _ = start_python_http_server(
            REPO_ROOT / "modules" / "api_hub",
            api_port,
            api_env,
        )
        processes.append(api_process)
        created = _seed_phase4_resources(api_hub_url, routes, token)
        if publish_job_postings and ("jobs", "job_postings") in created:
            headers = {"Authorization": f"Bearer {token}"}
            job = created[("jobs", "job_postings")]
            _post_json(
                f"{api_hub_url}/jobs/resources/job_postings/{job['id']}/actions/publish",
                {"reason": "vaga publicada para candidatura viva do shell User"},
                {**headers, "X-Idempotency-Key": f"phase4-jobs-job-postings-publish-{job['id']}"},
            )
        return processes, vite_url
    except Exception:
        for process in reversed(processes):
            stop_process(process)
        raise

@pytest.fixture(scope="session")
def rider_server():
    try:
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/valley_rider"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def business_server():
    try:
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/valley_business"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def superapp_server():
    try:
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/valley"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_user_server():
    try:
        process, url = start_vite_server(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one"),
            {"VITE_API_HUB_URL": "{server_url}"},
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_business_shell_server():
    try:
        process, url = start_vite_server(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-business"),
            {"VITE_API_HUB_URL": "{server_url}"},
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_business_live_server(tmp_path_factory):
    routes = [
        "/business/resources/companies",
        "/business/resources/catalog_offers",
        "/jobs/resources/job_postings",
        "/jobs/resources/resumes",
        "/erp/resources/fiscal_documents",
        "/bi/resources/dashboards",
        "/wms/resources/warehouses",
        "/tms/resources/freights",
        "/crm/resources/opportunities",
        "/bpm/resources/processes",
        "/document/resources/documents",
        "/hr/resources/employees",
        "/api_hub/resources/api_clients",
        "/api_hub/resources/api_keys",
        "/api_hub/resources/webhooks",
        "/api_hub/resources/integration_runs",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-business"),
            routes,
            tmp_path_factory.mktemp("phase4-business-live"),
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_business_governance_live_server(tmp_path_factory):
    routes = [
        "/legal/resources/cases",
        "/property/resources/properties",
        "/vision/resources/devices",
        "/ai_core/resources/moderation_decisions",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-business"),
            routes,
            tmp_path_factory.mktemp("phase4-business-governance-live"),
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_user_live_server(tmp_path_factory):
    routes = [
        "/identity/resources/users",
        "/finance/resources/wallets",
        "/marketplace/resources/orders",
        "/delivery/resources/delivery_requests",
        "/jobs/resources/job_postings",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one"),
            routes,
            tmp_path_factory.mktemp("phase4-user-live"),
            publish_job_postings=True,
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_user_jobs_live_server(tmp_path_factory):
    routes = ["/jobs/resources/job_postings"]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one"),
            routes,
            tmp_path_factory.mktemp("phase4-user-jobs-live"),
            publish_job_postings=True,
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_riders_server():
    try:
        process, url = start_vite_server(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-riders"),
            {"VITE_API_HUB_URL": "{server_url}"},
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def all_in_one_services_server():
    try:
        process, url = start_vite_server(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-services"),
            {"VITE_API_HUB_URL": "{server_url}"},
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def all_in_one_health_server():
    try:
        process, url = start_vite_server(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-health"),
            {"VITE_API_HUB_URL": "{server_url}"},
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def all_in_one_mobility_server():
    try:
        process, url = start_vite_server(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-mobility"),
            {"VITE_API_HUB_URL": "{server_url}"},
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_riders_live_server(tmp_path_factory):
    routes = [
        "/riders/resources/rider_profiles",
        "/riders/resources/vehicles",
        "/delivery/resources/delivery_requests",
        "/mobility/resources/rides",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-riders"),
            routes,
            tmp_path_factory.mktemp("phase4-riders-live"),
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_services_live_server(tmp_path_factory):
    routes = [
        "/services/resources/providers",
        "/services/resources/service_contracts",
        "/finance/resources/escrows",
        "/document/resources/documents",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-services"),
            routes,
            tmp_path_factory.mktemp("phase4-services-live"),
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_health_live_server(tmp_path_factory):
    routes = [
        "/health/resources/patients",
        "/health/resources/appointments",
        "/identity/resources/consents",
        "/document/resources/documents",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-health"),
            routes,
            tmp_path_factory.mktemp("phase4-health-live"),
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)


@pytest.fixture(scope="session")
def all_in_one_mobility_live_server(tmp_path_factory):
    routes = [
        "/mobility/resources/rides",
        "/mobility/resources/tickets",
        "/riders/resources/rider_profiles",
        "/finance/resources/wallets",
    ]
    try:
        processes, url = start_phase4_live_stack(
            os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-mobility"),
            routes,
            tmp_path_factory.mktemp("phase4-mobility-live"),
        )
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    for process in reversed(processes):
        stop_process(process)
