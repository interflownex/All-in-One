from urllib.parse import urlparse

from playwright.sync_api import Page, Route, expect


USER_JOURNEY_ROUTES = [
    ("/identity", "Identity", "Perfil Playwright"),
    ("/finance/wallets", "Wallets", "Wallet Playwright"),
    ("/marketplace/orders", "Orders", "Pedido Playwright"),
    ("/delivery/deliveryrequests", "Delivery Requests", "Entrega Playwright"),
    ("/jobs/jobpostings", "Job Postings", "Vaga Playwright"),
]

API_HUB_FIXTURES = {
    ("identity", "identity"): "Perfil Playwright",
    ("finance", "wallets"): "Wallet Playwright",
    ("marketplace", "orders"): "Pedido Playwright",
    ("delivery", "deliveryrequests"): "Entrega Playwright",
    ("jobs", "jobpostings"): "Vaga Playwright",
}


def _serve_gateway_collection(route: Route) -> None:
    path_parts = urlparse(route.request.url).path.strip("/").split("/")
    module_name = path_parts[1] if len(path_parts) > 1 else "unknown"
    entity = path_parts[2] if len(path_parts) > 2 else "unknown"
    title = API_HUB_FIXTURES.get((module_name, entity), f"{module_name} {entity}")
    route.fulfill(
        status=200,
        content_type="application/json",
        json={
            "data": [
                {
                    "id": f"phase4-{module_name}-{entity}",
                    "name": title,
                    "status": "Ativo",
                    "created_at": "2026-07-12T00:00:00Z",
                }
            ]
        },
    )


def test_all_in_one_user_shell_runs_consumer_journey(page: Page, all_in_one_user_server: str) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)

    page.goto(all_in_one_user_server, wait_until="domcontentloaded")

    expect(page.locator("h1")).to_contain_text("Bem-vindo ao All-in-One")
    expect(page.get_by_text("Hambúrguer Gourmet Valley")).to_be_visible()

    for path, title, fixture_name in USER_JOURNEY_ROUTES:
        page.goto(f"{all_in_one_user_server}{path}", wait_until="domcontentloaded")

        expect(page.locator("h1")).to_contain_text(title)
        expect(page.get_by_placeholder(f"Buscar em {title}...")).to_be_visible()
        expect(page.get_by_text(fixture_name)).to_be_visible(timeout=10000)


def test_all_in_one_user_shell_keeps_mobile_journey_reachable(page: Page, all_in_one_user_server: str) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(f"{all_in_one_user_server}/marketplace/orders", wait_until="domcontentloaded")

    expect(page.locator("h1")).to_contain_text("Orders")
    expect(page.get_by_text("Pedido Playwright")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Buscar em Orders...")).to_be_visible()
