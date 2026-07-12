import pytest
import subprocess
import time
import socket
import os
from urllib.request import urlopen


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


def start_vite_server(app_directory: str) -> tuple[subprocess.Popen, str]:
    port = free_port()
    process = subprocess.Popen(
        f"npm run dev -- --port {port} --strictPort --host 127.0.0.1",
        cwd=app_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
    )
    if not wait_for_http(port, timeout=60):
        process.terminate()
        raise RuntimeError(f"Vite nao respondeu corretamente na porta {port}.")
    return process, f"http://127.0.0.1:{port}"


def stop_process(process: subprocess.Popen) -> None:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()

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
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-riders"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def all_in_one_services_server():
    try:
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-services"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def all_in_one_health_server():
    try:
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-health"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)

@pytest.fixture(scope="session")
def all_in_one_mobility_server():
    try:
        process, url = start_vite_server(os.path.join(os.path.dirname(__file__), "../../apps/all-in-one-mobility"))
    except RuntimeError as exc:
        pytest.fail(str(exc))
    yield url
    stop_process(process)
