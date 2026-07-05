from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import Page, Route, expect


ROOT = Path(__file__).resolve().parents[2]


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        return int(server.getsockname()[1])


def wait_for_http(port: int, timeout: int = 60) -> bool:
    start_time = time.time()
    while time.time() - start_time <= timeout:
        try:
            with urlopen(f"http://127.0.0.1:{port}", timeout=2) as response:
                if response.status == 200 and b'<div id="root">' in response.read():
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def start_vite_server(app_directory: Path) -> tuple[subprocess.Popen, str]:
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


def _assert_actor_header(route: Route) -> None:
    headers = route.request.headers
    actor_id = headers.get("x-actor-user-id") or headers.get("X-Actor-User-Id")
    assert actor_id, "O shell de Mobility precisa enviar X-Actor-User-Id."


def _stub_mobility_shell_feed(page: Page) -> None:
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
                "orders_total": 22,
                "orders_paid": 18,
                "orders_completed": 17,
                "reviews_total": 4,
                "average_rating": 4.7,
                "support_cases_total": 2,
                "support_cases_open": 1,
                "support_cases_resolved": 1,
                "conversion_rate_percent": 28,
                "source": "api_hub",
            },
        )

    def serve_health(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "module": "mobility",
                "service": "mobility",
                "status": "healthy",
                "storage": "postgres",
                "version": "baseline",
            },
        )

    def serve_rides(route: Route) -> None:
        _assert_actor_header(route)
        if route.request.method == "POST":
            payload = route.request.post_data_json
            assert payload["user_id"]
            assert payload["payload"]["origin"]
            assert payload["payload"]["destination"]
            route.fulfill(
                status=201,
                content_type="application/json",
                json={"id": "ride-new", "status": "requested", "message": "Corrida solicitada."},
            )
            return
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "ride-1",
                        "status": "accepted",
                        "created_at": "2026-07-04T09:00:00Z",
                        "payload": {
                            "origin": "Centro, Sao Paulo",
                            "destination": "Aeroporto de Congonhas",
                            "vehicle_type": "comfort",
                            "rider_name": "Marina Costa",
                            "fare_brl": "48.90",
                            "eta": "12 min",
                            "qr_mode": "nfc",
                        },
                    }
                ],
            },
        )

    def serve_tickets(route: Route) -> None:
        _assert_actor_header(route)
        if route.request.method == "POST":
            payload = route.request.post_data_json
            assert payload["user_id"]
            assert payload["payload"]["route_code"]
            assert payload["payload"]["amount_brl"]
            route.fulfill(
                status=201,
                content_type="application/json",
                json={"id": "ticket-new", "status": "active", "message": "Bilhete emitido."},
            )
            return
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "ticket-1",
                        "status": "active",
                        "created_at": "2026-07-04T13:00:00Z",
                        "payload": {
                            "route_code": "MTR-101",
                            "amount_brl": "9.80",
                            "qr_token_hash": "hash-mtr-101",
                            "mode": "metro",
                            "channel": "qr",
                            "validity": "90 minutos",
                        },
                    }
                ],
            },
        )

    def serve_routes(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "route-1",
                        "status": "available",
                        "created_at": "2026-07-04T08:00:00Z",
                        "payload": {
                            "route_code": "MTR-101",
                            "origin": "Centro",
                            "destination": "Zona Sul",
                            "transport_mode": "metro",
                            "line_name": "Linha Azul",
                            "duration_minutes": "24",
                        },
                    }
                ],
            },
        )

    def serve_fares(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "fare-1",
                        "status": "active",
                        "created_at": "2026-07-04T08:40:00Z",
                        "payload": {
                            "route_code": "MTR-101",
                            "base_fare_brl": "9.80",
                            "peak_multiplier": "1.2",
                            "discount_rule": "off_peak_10",
                            "payment_method": "qr+nfc",
                        },
                    }
                ],
            },
        )

    page.route("**/gateway/status**", serve_gateway_status)
    page.route("**/gateway/insights/commercial**", serve_commercial_insights)
    page.route("**/health**", serve_health)
    page.route("**/resources/rides**", serve_rides)
    page.route("**/resources/tickets**", serve_tickets)
    page.route("**/resources/routes**", serve_routes)
    page.route("**/resources/fare_rules**", serve_fares)


def test_all_in_one_mobility_dashboard_and_actions(page: Page) -> None:
    process, server_url = start_vite_server(ROOT / "apps" / "all-in-one-mobility")
    try:
        _stub_mobility_shell_feed(page)

        page.goto(server_url, timeout=60000, wait_until="domcontentloaded")

        expect(page.locator("h1")).to_contain_text("Corridas, tickets e tarifas")
        expect(page.locator(".metric-card")).to_have_count(5)
        expect(page.get_by_text("gateway-signed")).to_be_visible()

        page.locator(".nav-pill", has_text="Corridas").click()
        expect(page.get_by_role("heading", name="Solicitar viagem urbana")).to_be_visible()
        page.get_by_placeholder("Centro, Sao Paulo").fill("Centro, Sao Paulo")
        page.get_by_placeholder("Aeroporto de Congonhas").fill("Aeroporto de Congonhas")
        page.get_by_placeholder("comfort").fill("comfort")
        page.get_by_placeholder("Pessoa Demo").fill("Pessoa Demo")
        page.get_by_role("button", name="Solicitar corrida").click()
        expect(page.get_by_text("Corrida solicitada com sucesso: ride-new.")).to_be_visible()

        page.locator(".nav-pill", has_text="Bilhetes").click()
        expect(page.get_by_role("heading", name="Emitir QR ou NFC")).to_be_visible()
        page.locator('input[placeholder="MTR-101"]').fill("MTR-101")
        page.locator('input[placeholder="9.80"]').fill("9.80")
        page.locator('input[placeholder="demo-qr-hash"]').fill("demo-qr-hash")
        page.locator('input[placeholder="qr"]').fill("qr")
        page.get_by_role("button", name="Emitir bilhete").click()
        expect(page.get_by_text("Bilhete emitido com sucesso: ticket-new.")).to_be_visible()

        page.locator(".nav-pill", has_text="Rotas").click()
        expect(page.get_by_role("heading", name="Rotas e trajetos disponiveis")).to_be_visible()
        expect(page.get_by_text("MTR-101")).to_be_visible()
        expect(page.get_by_text("Linha Azul")).to_be_visible()

        page.locator(".nav-pill", has_text="Tarifas").click()
        expect(page.get_by_role("heading", name="Tarifas e regras ativas")).to_be_visible()
    finally:
        stop_process(process)
