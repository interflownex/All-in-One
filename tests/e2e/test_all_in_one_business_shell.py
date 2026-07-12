from urllib.parse import urlparse

from playwright.sync_api import Page, Route, expect


BUSINESS_JOURNEY_ROUTES = [
    ("/business/companies", "Companies", "Empresa Playwright"),
    ("/business/catalogoffers", "Catalog Offers", "Oferta Playwright"),
    ("/jobs/jobpostings", "Job Postings", "Vaga Business Playwright"),
    ("/jobs/applications", "Applications", "Candidatura Playwright"),
    ("/jobs/resumeaccesslogs", "Resume Access Logs", "Acesso Curriculo Playwright"),
]

API_HUB_FIXTURES = {
    ("business", "companies"): "Empresa Playwright",
    ("business", "catalogoffers"): "Oferta Playwright",
    ("jobs", "jobpostings"): "Vaga Business Playwright",
    ("jobs", "applications"): "Candidatura Playwright",
    ("jobs", "resumeaccesslogs"): "Acesso Curriculo Playwright",
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


def test_all_in_one_business_shell_runs_jobs_access_journey(
    page: Page, all_in_one_business_shell_server: str
) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)

    page.goto(all_in_one_business_shell_server, wait_until="domcontentloaded")

    expect(page.locator("h1")).to_contain_text("Bem-vindo ao Valley Business")
    expect(page.get_by_text("Dashboard ERP Integrado")).to_be_visible()

    for path, title, fixture_name in BUSINESS_JOURNEY_ROUTES:
        page.goto(f"{all_in_one_business_shell_server}{path}", wait_until="domcontentloaded")

        expect(page.locator("h1")).to_contain_text(title)
        expect(page.get_by_placeholder(f"Buscar em {title}...")).to_be_visible()
        expect(page.get_by_text(fixture_name)).to_be_visible(timeout=10000)


def test_all_in_one_business_shell_keeps_mobile_jobs_access_reachable(
    page: Page, all_in_one_business_shell_server: str
) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(f"{all_in_one_business_shell_server}/jobs/resumeaccesslogs", wait_until="domcontentloaded")

    expect(page.locator("h1")).to_contain_text("Resume Access Logs")
    expect(page.get_by_text("Acesso Curriculo Playwright")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Buscar em Resume Access Logs...")).to_be_visible()


def test_all_in_one_business_shell_runs_live_api_hub_actions(
    page: Page, all_in_one_business_live_server: str
) -> None:
    page.goto(f"{all_in_one_business_live_server}/business/companies", wait_until="domcontentloaded")
    expect(page.get_by_text("Empresa Business Playwright")).to_be_visible(timeout=10000)
    page.get_by_role("button", name="Aprovar empresa").click()
    expect(page.get_by_text("Empresa aprovada no API Hub vivo.")).to_be_visible(timeout=10000)
    expect(page.get_by_text("approved")).to_be_visible()

    page.goto(f"{all_in_one_business_live_server}/jobs/jobpostings", wait_until="domcontentloaded")
    expect(page.get_by_text("Vaga Playwright")).to_be_visible(timeout=10000)
    page.get_by_role("button", name="Publicar vaga").click()
    expect(page.get_by_text("Vaga publicada no API Hub vivo.")).to_be_visible(timeout=10000)
    expect(page.get_by_text("published")).to_be_visible()

    page.goto(f"{all_in_one_business_live_server}/jobs/resumeaccesslogs", wait_until="domcontentloaded")
    page.get_by_role("button", name="Registrar acesso a currículo").click()
    expect(page.get_by_text("Acesso a curriculo registrado no API Hub vivo.")).to_be_visible(timeout=10000)
    expect(page.get_by_text("triagem para vaga publicada via Business shell")).to_be_visible(timeout=10000)
