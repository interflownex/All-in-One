from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import ProxyHandler, build_opener

from playwright.sync_api import Page, Route, expect


ROOT = Path(__file__).resolve().parents[2]
LOOPBACK_OPENER = build_opener(ProxyHandler({}))


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def wait_for_http(port: int, timeout: int = 60) -> bool:
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            with LOOPBACK_OPENER.open(
                f"http://127.0.0.1:{port}", timeout=2
            ) as response:
                if response.status == 200 and b'<div id="root">' in response.read():
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def start_vite_server(app_directory: Path) -> tuple[subprocess.Popen, str]:
    port = free_port()
    process = subprocess.Popen(
        [
            "npm",
            "run",
            "dev",
            "--",
            "--port",
            str(port),
            "--strictPort",
            "--host",
            "127.0.0.1",
        ],
        cwd=app_directory,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
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


def _assert_actor_header(route: Route) -> None:
    headers = route.request.headers
    actor_id = headers.get("x-actor-user-id") or headers.get("X-Actor-User-Id")
    assert actor_id, "O shell de Health precisa enviar X-Actor-User-Id."


def _stub_health_shell_feed(page: Page) -> None:
    def serve_gateway_status(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "service": "api_hub",
                "status": "operational",
                "security": "gateway-signed",
                "rate_limit": "60rpm",
                "routes": ["/gateway/status", "/gateway/insights/commercial"],
            },
        )

    def serve_commercial_insights(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "orders_total": 20,
                "orders_paid": 17,
                "orders_completed": 16,
                "reviews_total": 5,
                "average_rating": 4.9,
                "support_cases_total": 1,
                "support_cases_open": 0,
                "support_cases_resolved": 1,
                "conversion_rate_percent": 23,
                "source": "api_hub",
            },
        )

    def serve_health(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "module": "health",
                "service": "health",
                "status": "healthy",
                "storage": "postgres",
                "version": "baseline",
            },
        )

    def serve_patients(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "patient-1",
                        "status": "active",
                        "created_at": "2026-07-04T09:00:00Z",
                        "payload": {
                            "full_name": "Ana Souza",
                            "health_identifier": "SUS-998877",
                            "city": "Sao Paulo",
                            "primary_care": "Clinica geral",
                            "insurance_plan": "All-in-One Care",
                            "next_visit": "2026-07-08T14:00:00Z",
                        },
                    },
                    {
                        "id": "patient-2",
                        "status": "monitoring",
                        "created_at": "2026-07-04T11:00:00Z",
                        "payload": {
                            "full_name": "Carlos Lima",
                            "health_identifier": "SUS-554433",
                            "city": "Campinas",
                            "primary_care": "Cardiologia",
                            "insurance_plan": "Premium Care",
                            "next_visit": "2026-07-09T10:30:00Z",
                        },
                    },
                ],
            },
        )

    def serve_appointments(route: Route) -> None:
        _assert_actor_header(route)
        if route.request.method == "POST":
            payload = route.request.post_data_json
            assert payload["user_id"]
            assert payload["payload"]["scheduled_at"]
            route.fulfill(
                status=201,
                content_type="application/json",
                json={"id": "appointment-new", "status": "scheduled", "message": "Consulta agendada."},
            )
            return
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "appointment-1",
                        "status": "confirmed",
                        "created_at": "2026-07-04T12:00:00Z",
                        "payload": {
                            "patient_id": "patient-1",
                            "patient_name": "Ana Souza",
                            "specialty": "telemedicina",
                            "scheduled_at": "2026-07-08T14:00:00Z",
                            "mode": "video",
                            "channel": "portal",
                            "telemedicine": True,
                        },
                    }
                ],
            },
        )

    def serve_records(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "record-1",
                        "status": "available",
                        "created_at": "2026-07-04T14:00:00Z",
                        "payload": {
                            "patient_id": "patient-1",
                            "patient_name": "Ana Souza",
                            "record_type": "consulta",
                            "provider": "Dra. Marina",
                            "summary": "Evolucao favoravel e acompanhamento remoto.",
                            "confidentiality": "restricted",
                        },
                    }
                ],
            },
        )

    def serve_prescriptions(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "prescription-1",
                        "status": "issued",
                        "created_at": "2026-07-04T15:00:00Z",
                        "payload": {
                            "patient_id": "patient-1",
                            "patient_name": "Ana Souza",
                            "medication": "Vitamina D",
                            "dosage": "1 comp. ao dia",
                            "issued_by": "Dra. Marina",
                            "refills": "2",
                        },
                    }
                ],
            },
        )

    page.route("**/gateway/status**", serve_gateway_status)
    page.route("**/gateway/insights/commercial**", serve_commercial_insights)
    page.route("**/health**", serve_health)
    page.route("**/resources/patients**", serve_patients)
    page.route("**/resources/appointments**", serve_appointments)
    page.route("**/resources/medical_records**", serve_records)
    page.route("**/resources/prescriptions**", serve_prescriptions)


def test_all_in_one_health_dashboard_and_scheduling(page: Page) -> None:
    process, server_url = start_vite_server(ROOT / "apps" / "all-in-one-health")
    try:
        _stub_health_shell_feed(page)

        page.goto(server_url, timeout=60000, wait_until="domcontentloaded")

        expect(page.locator("h1")).to_contain_text(
            "Saude operacional com consentimento, agenda e prontuario protegido."
        )
        expect(page.locator(".api-card")).to_have_count(4)
        expect(page.locator(".api-card span.online, .api-card span.fallback")).to_have_count(
            4
        )
        journey = page.get_by_label("Jornada prioritaria")
        expect(journey.get_by_text("Consentimento LGPD", exact=True)).to_be_visible()
        expect(page.get_by_label("Acao de jornada Health")).to_be_visible()
        expect(page.get_by_label("Governanca clinica Health")).to_be_visible()
    finally:
        stop_process(process)
