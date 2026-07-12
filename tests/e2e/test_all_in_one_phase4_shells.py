from collections.abc import Callable

import pytest
from playwright.sync_api import Page, Route, expect


PHASE4_SHELLS = [
    pytest.param(
        "all_in_one_riders_server",
        "All-in-One Riders",
        "Candidatura",
        [
            "/riders/resources/rider_profiles",
            "/riders/resources/vehicles",
            "/delivery/resources/delivery_requests",
            "/mobility/resources/rides",
        ],
        id="riders",
    ),
    pytest.param(
        "all_in_one_services_server",
        "All-in-One Services",
        "Prestador aprovado",
        [
            "/services/resources/providers",
            "/services/resources/service_contracts",
            "/finance/resources/escrows",
            "/document/resources/documents",
        ],
        id="services",
    ),
    pytest.param(
        "all_in_one_health_server",
        "All-in-One Health",
        "Consentimento LGPD",
        [
            "/health/resources/patients",
            "/health/resources/appointments",
            "/identity/resources/consents",
            "/document/resources/documents",
        ],
        id="health",
    ),
    pytest.param(
        "all_in_one_mobility_server",
        "All-in-One Mobility",
        "Corrida",
        [
            "/mobility/resources/rides",
            "/mobility/resources/tickets",
            "/riders/resources/rider_profiles",
            "/finance/resources/wallets",
        ],
        id="mobility",
    ),
]


PHASE4_LIVE_SHELLS = [
    pytest.param(
        "all_in_one_riders_live_server",
        "All-in-One Riders",
        "Candidatura",
        id="riders-live-api-hub",
    ),
    pytest.param(
        "all_in_one_services_live_server",
        "All-in-One Services",
        "Prestador aprovado",
        id="services-live-api-hub",
    ),
    pytest.param(
        "all_in_one_health_live_server",
        "All-in-One Health",
        "Consentimento LGPD",
        id="health-live-api-hub",
    ),
    pytest.param(
        "all_in_one_mobility_live_server",
        "All-in-One Mobility",
        "Corrida",
        id="mobility-live-api-hub",
    ),
]


def _serve_collection(route: Route) -> None:
    route.fulfill(
        status=200,
        content_type="application/json",
        json={
            "data": [
                {
                    "id": "phase4-e2e-1",
                    "name": "Registro Playwright",
                    "status": "active",
                    "created_at": "2026-07-12T00:00:00Z",
                }
            ]
        },
    )


def _wire_routes(page: Page, routes: list[str]) -> None:
    for route in routes:
        page.route(f"**{route}**", _serve_collection)


def _expect_journey_marker(page: Page, journey_marker: str) -> None:
    journey = page.get_by_label("Jornada prioritaria")
    expect(journey.get_by_text(journey_marker, exact=True)).to_be_visible()


@pytest.mark.parametrize("server_fixture,title,journey_marker,routes", PHASE4_SHELLS)
def test_phase4_shells_load_api_hub_data(
    page: Page,
    request: pytest.FixtureRequest,
    server_fixture: str,
    title: str,
    journey_marker: str,
    routes: list[str],
) -> None:
    server_url = request.getfixturevalue(server_fixture)
    _wire_routes(page, routes)

    page.goto(server_url, wait_until="domcontentloaded")

    expect(page.locator("h1")).to_be_visible()
    expect(page.locator(".eyebrow")).to_contain_text(title)
    _expect_journey_marker(page, journey_marker)
    expect(page.locator(".online")).to_have_count(len(routes), timeout=10000)
    expect(page.get_by_text("registro(s) retornado(s) pelo API Hub").first).to_be_visible()


@pytest.mark.parametrize("server_fixture,title,journey_marker,routes", PHASE4_SHELLS)
def test_phase4_shells_keep_mobile_journey_visible(
    page: Page,
    request: pytest.FixtureRequest,
    server_fixture: str,
    title: str,
    journey_marker: str,
    routes: list[str],
) -> None:
    server_url = request.getfixturevalue(server_fixture)
    _wire_routes(page, routes)
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(server_url, wait_until="domcontentloaded")

    expect(page.locator(".eyebrow")).to_contain_text(title)
    _expect_journey_marker(page, journey_marker)
    expect(page.locator(".panel")).to_be_visible()


@pytest.mark.parametrize("server_fixture,title,journey_marker", PHASE4_LIVE_SHELLS)
def test_phase4_shells_load_live_api_hub_fixtures(
    page: Page,
    request: pytest.FixtureRequest,
    server_fixture: str,
    title: str,
    journey_marker: str,
) -> None:
    server_url = request.getfixturevalue(server_fixture)

    page.goto(server_url, wait_until="domcontentloaded")

    expect(page.locator(".eyebrow")).to_contain_text(title)
    _expect_journey_marker(page, journey_marker)
    expect(page.locator(".online")).to_have_count(4, timeout=15000)
    expect(page.get_by_text("1 registro(s) retornado(s) pelo API Hub").first).to_be_visible()
