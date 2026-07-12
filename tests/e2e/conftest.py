import pytest
import json
import subprocess
import sys
import time
import socket
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import jwt


REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE4_ACTOR_ID = "11111111-1111-4111-8111-111111111111"
PHASE4_JWT_SECRET = "phase4-live-e2e-secret-with-32-bytes-minimum"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def wait_for_http(port: int, timeout: int = 15) -> bool:
    """Wait until the expected Vite server returns a valid HTTP response."""
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            with urlopen(f"http://127.0.0.1:{port}", timeout=2) as response:
                if response.status == 200 and b'<div id="root">' in response.read():
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def wait_for_url(url: str, timeout: int = 15) -> bool:
    start_time = time.time()
    while time.time() - start_time <= timeout:
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
    process = subprocess.Popen(
        f"npm run dev -- --port {port} --strictPort --host 127.0.0.1",
        cwd=app_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
        env=process_env,
    )
    if not wait_for_http(port, timeout=60):
        process.terminate()
        raise RuntimeError(f"Vite nao respondeu corretamente na porta {port}.")
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
    if not wait_for_url(f"{server_url}{health_path}", timeout=60):
        process.terminate()
        raise RuntimeError(f"Servidor FastAPI nao respondeu corretamente em {server_url}.")
    return process, server_url


def stop_process(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


PHASE4_ROUTE_PAYLOADS = {
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
    },
    ("services", "providers"): {"category": "home_services", "name": "Prestador Playwright"},
    ("services", "service_contracts"): {"visit_price_brl": "120.00", "scope": "Visita Playwright"},
    ("finance", "escrows"): {
        "wallet_id": "wallet-phase4",
        "beneficiary_user_id": PHASE4_ACTOR_ID,
        "amount_brl": "120.00",
    },
    ("finance", "wallets"): {"wallet_type": "consumer", "label": "Wallet Playwright"},
    ("document", "documents"): {"storage_key": "phase4/doc.pdf", "filename": "doc.pdf"},
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


def _post_json(url: str, payload: dict[str, object], headers: dict[str, str]) -> None:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            if response.status not in {200, 201}:
                raise RuntimeError(f"POST {url} retornou HTTP {response.status}.")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"POST {url} retornou HTTP {exc.code}: {detail}") from exc


def _seed_phase4_resources(api_hub_url: str, routes: list[str], token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    for index, route in enumerate(routes, start=1):
        module_name, resource_type = _route_to_resource(route)
        payload = PHASE4_ROUTE_PAYLOADS[(module_name, resource_type)]
        _post_json(
            f"{api_hub_url}/{module_name}/resources/{resource_type}",
            {"user_id": PHASE4_ACTOR_ID, "payload": payload},
            {**headers, "X-Idempotency-Key": f"phase4-{module_name}-{resource_type}-{index}"},
        )


def start_phase4_live_stack(
    app_directory: str,
    routes: list[str],
    storage_dir: Path,
) -> tuple[list[subprocess.Popen], str]:
    api_port = free_port()
    api_hub_url = f"http://127.0.0.1:{api_port}"
    token = jwt.encode({"sub": PHASE4_ACTOR_ID}, PHASE4_JWT_SECRET, algorithm="HS256")
    processes: list[subprocess.Popen] = []
    module_urls: dict[str, str] = {}

    try:
        for module_name in sorted({_route_to_resource(route)[0] for route in routes}):
            process, module_url = start_python_http_server(
                REPO_ROOT / "modules" / module_name,
                free_port(),
                {
                    "ALL_IN_ONE_STORAGE_DIR": str(storage_dir / "modules"),
                    "ALL_IN_ONE_ENV": "test",
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
            },
        )
        processes.append(vite_process)

        api_env = {
            "ALL_IN_ONE_STORAGE_DIR": str(storage_dir / "api_hub"),
            "ALL_IN_ONE_ENV": "test",
            "ALL_IN_ONE_JWT_SECRET": PHASE4_JWT_SECRET,
            "ALL_IN_ONE_CORS_ORIGINS": vite_url,
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
        _seed_phase4_resources(api_hub_url, routes, token)
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
