import json

from playwright.sync_api import Page, Route, expect


def _assert_actor_header(route: Route) -> None:
    headers = route.request.headers
    actor_id = headers.get("x-actor-user-id") or headers.get("X-Actor-User-Id")
    assert actor_id, "O shell de Services precisa enviar X-Actor-User-Id."


def _stub_services_shell_feed(page: Page) -> None:
    def serve_gateway_status(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "service": "api_hub",
                "status": "operational",
                "security": "gateway-signed",
                "rate_limit": "60rpm",
                "routes": [
                    "/gateway/catalog/offers",
                    "/gateway/insights/commercial",
                    "/gateway/status",
                ],
            },
        )

    def serve_commercial_insights(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "orders_total": 18,
                "orders_paid": 15,
                "orders_completed": 14,
                "reviews_total": 4,
                "average_rating": 4.9,
                "support_cases_total": 2,
                "support_cases_open": 1,
                "support_cases_resolved": 1,
                "conversion_rate_percent": 22,
                "crm_records": 38,
                "bi_records": 24,
                "source": "api_hub",
            },
        )

    def serve_providers(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "provider-1",
                        "status": "approved",
                        "created_at": "2026-07-04T08:00:00Z",
                        "payload": {
                            "category": "instalacao",
                            "name": "Solar Care",
                            "service_area": "Energia solar",
                            "city": "Campinas",
                            "rating": "4.9",
                            "verified": True,
                        },
                    },
                    {
                        "id": "provider-2",
                        "status": "pending_review",
                        "created_at": "2026-07-04T08:10:00Z",
                        "payload": {
                            "category": "assistencia tecnica",
                            "name": "Prime Services",
                            "service_area": "Hibrido",
                            "city": "Sao Paulo",
                            "rating": "4.7",
                            "verified": False,
                        },
                    },
                ],
            },
        )

    def serve_visits(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "visit-1",
                        "status": "confirmed",
                        "created_at": "2026-07-04T09:00:00Z",
                        "payload": {
                            "provider_id": "provider-1",
                            "scheduled_at": "2026-07-05T14:00:00Z",
                            "visit_price_brl": "180.00",
                            "customer_name": "Cliente Energia",
                            "service_type": "visita tecnica",
                        },
                    }
                ],
            },
        )

    def serve_quotes(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "quote-1",
                        "status": "created",
                        "created_at": "2026-07-04T09:30:00Z",
                        "payload": {
                            "provider_id": "provider-1",
                            "service_type": "orcamento rapido",
                            "quoted_brl": "320.00",
                            "visit_price_brl": "180.00",
                        },
                    }
                ],
            },
        )

    def serve_contracts(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "contract-1",
                        "status": "held",
                        "created_at": "2026-07-04T10:00:00Z",
                        "payload": {
                            "provider_id": "provider-1",
                            "contracted_price_brl": "320.00",
                            "visit_price_brl": "180.00",
                            "stage": "avaliacao",
                        },
                    }
                ],
            },
        )

    def serve_evidence(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "evidence-1",
                        "status": "accepted",
                        "created_at": "2026-07-04T10:30:00Z",
                        "payload": {
                            "kind": "photo",
                            "note": "Foto anexada ao contrato",
                            "hash": "sha256:demo",
                        },
                    }
                ],
            },
        )

    def serve_health(route: Route) -> None:
        url = route.request.url
        if "8101" in url:
            payload = {
                "module": "identity",
                "service": "identity",
                "status": "healthy",
                "storage": "postgres",
                "version": "baseline",
            }
        else:
            payload = {
                "module": "services",
                "service": "services",
                "status": "healthy",
                "storage": "postgres",
                "version": "baseline",
            }
        route.fulfill(status=200, content_type="application/json", json=payload)

    def serve_time_slots(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "provider_id": "provider-1",
                "date": "2026-07-04",
                "available_slots": ["09:00", "13:00", "17:00"],
            },
        )

    def serve_reserve_slot(route: Route) -> None:
        body = json.loads(route.request.post_data or "{}")
        assert body.get("customer_id"), "A reserva precisa enviar o customer_id persistente."
        assert body.get("slot"), "A reserva precisa enviar o slot selecionado."
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "status": "reserved",
                "provider_id": "provider-1",
                "slot": body["slot"],
                "customer_id": body["customer_id"],
                "reservation_id": "reservation-1",
            },
        )

    page.route("**/gateway/status**", serve_gateway_status)
    page.route("**/gateway/insights/commercial**", serve_commercial_insights)
    page.route("**/resources/providers**", serve_providers)
    page.route("**/resources/visits**", serve_visits)
    page.route("**/resources/quotes**", serve_quotes)
    page.route("**/resources/service_contracts**", serve_contracts)
    page.route("**/resources/evidence**", serve_evidence)
    page.route("**/health**", serve_health)
    page.route("**/time-slots**", serve_time_slots)
    page.route("**/reserve-slot**", serve_reserve_slot)


def test_all_in_one_services_dashboard_and_reservation(page: Page, all_in_one_services_server: str) -> None:
    _stub_services_shell_feed(page)

    page.goto(all_in_one_services_server, timeout=60000, wait_until="domcontentloaded")

    expect(page.get_by_role("heading", name="Operacao de servicos em tempo real")).to_be_visible()
    expect(page.locator(".summary-card")).to_have_count(6)
    expect(page.get_by_text("gateway-signed")).to_be_visible()
    expect(page.get_by_text("Solar Care")).to_be_visible()
    expect(page.get_by_text("Cliente Energia")).to_be_visible()
    expect(page.get_by_text("Foto anexada ao contrato")).to_be_visible()
    expect(page.get_by_text("R$ 180,00")).to_be_visible()
    expect(page.locator(".alert-box")).to_have_count(0)

    page.locator(".nav-pill", has_text="Prestadores").click()
    expect(page.get_by_role("heading", name="Base operacional")).to_be_visible()
    expect(page.get_by_text("Solar Care")).to_be_visible()
    expect(page.get_by_text("Prime Services")).to_be_visible()

    page.get_by_placeholder("Buscar prestadores, visitas e contratos").fill("Prime")
    expect(page.locator(".provider-card")).to_have_count(1)
    expect(page.get_by_text("Prime Services")).to_be_visible()

    page.get_by_placeholder("Buscar prestadores, visitas e contratos").fill("")
    page.get_by_role("button", name="13:00").click()
    page.get_by_role("button", name="Reservar slot").click()
    expect(page.get_by_text("Reserva confirmada: reservation-1 em 13:00")).to_be_visible()

    page.locator(".nav-pill", has_text="Visitas").click()
    expect(page.get_by_role("heading", name="Atendimentos programados")).to_be_visible()
    expect(page.get_by_text("Cliente Energia")).to_be_visible()

    page.locator(".nav-pill", has_text="Orcamentos").click()
    expect(page.get_by_role("heading", name="Propostas em aberto")).to_be_visible()
    expect(page.get_by_text("orcamento rapido")).to_be_visible()

    page.locator(".nav-pill", has_text="Contratos").click()
    expect(page.get_by_role("heading", name="Escopo e evolucao")).to_be_visible()
    expect(page.get_by_text("avaliacao")).to_be_visible()

    page.locator(".nav-pill", has_text="Evidencias").click()
    expect(page.get_by_role("heading", name="Auditoria e anexos")).to_be_visible()
    expect(page.get_by_text("Foto anexada ao contrato")).to_be_visible()
