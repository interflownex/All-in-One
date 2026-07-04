import pytest
from playwright.sync_api import Page, Route, expect


def _assert_actor_header(route: Route) -> None:
    headers = route.request.headers
    actor_id = headers.get("x-actor-user-id") or headers.get("X-Actor-User-Id")
    assert actor_id, "O SmartCRUD precisa enviar X-Actor-User-Id para o API Hub."


@pytest.mark.parametrize("server_fixture", ["all_in_one_server", "all_in_one_business_server"])
def test_all_in_one_business_overview_uses_live_companies(
    page: Page,
    request: pytest.FixtureRequest,
    server_fixture: str,
) -> None:
    all_in_one_server = request.getfixturevalue(server_fixture)

    def serve_companies(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "company-1",
                        "name": "Clínica Solar",
                        "status": "approved",
                        "created_at": "2026-07-04T00:00:00Z",
                    }
                ]
            },
    )

    page.route("**/business/resources/companies**", serve_companies)

    page.goto(all_in_one_server, timeout=60000, wait_until="domcontentloaded")
    page.locator('nav .module-link').filter(has_text="Business").click()
    page.locator('nav .sub-menu a[href="/business/business"]').click()

    expect(page.locator("h1")).to_contain_text("Business")
    expect(page.get_by_placeholder("Buscar em Business...")).to_be_visible()
    expect(page.get_by_text("Clínica Solar")).to_be_visible()


@pytest.mark.parametrize("server_fixture", ["all_in_one_server", "all_in_one_business_server"])
def test_all_in_one_business_finance_overview_uses_live_wallets(
    page: Page,
    request: pytest.FixtureRequest,
    server_fixture: str,
) -> None:
    all_in_one_server = request.getfixturevalue(server_fixture)

    def serve_wallets(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "wallet-1",
                        "name": "Carteira Operacional",
                        "status": "active",
                        "created_at": "2026-07-04T00:00:00Z",
                    }
                ]
            },
    )

    page.route("**/finance/resources/wallets**", serve_wallets)

    page.goto(all_in_one_server, timeout=60000, wait_until="domcontentloaded")
    page.locator('nav .module-link').filter(has_text="Finance").click()
    page.locator('nav .sub-menu a[href="/finance/finance"]').click()

    expect(page.locator("h1")).to_contain_text("Finance")
    expect(page.get_by_placeholder("Buscar em Finance...")).to_be_visible()
    expect(page.get_by_text("Carteira Operacional")).to_be_visible()
