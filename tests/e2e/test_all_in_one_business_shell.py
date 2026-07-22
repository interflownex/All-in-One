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
LIVE_API_EXPECT_TIMEOUT = 60000


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
        page.goto(
            f"{all_in_one_business_shell_server}{path}", wait_until="domcontentloaded"
        )

        expect(page.locator("h1")).to_contain_text(title)
        expect(page.get_by_placeholder(f"Buscar em {title}...")).to_be_visible()
        expect(page.get_by_text(fixture_name)).to_be_visible(timeout=10000)


def test_all_in_one_business_shell_keeps_mobile_jobs_access_reachable(
    page: Page, all_in_one_business_shell_server: str
) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(
        f"{all_in_one_business_shell_server}/jobs/resumeaccesslogs",
        wait_until="domcontentloaded",
    )

    expect(page.locator("h1")).to_contain_text("Resume Access Logs")
    expect(page.get_by_text("Acesso Curriculo Playwright")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Buscar em Resume Access Logs...")).to_be_visible()


def test_all_in_one_business_shell_runs_live_api_hub_actions(
    page: Page, all_in_one_business_live_server: str
) -> None:
    page.goto(
        f"{all_in_one_business_live_server}/business/companies",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Empresa Business Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Filtros operacionais Business")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Auditoria operacional Business")).to_contain_text(
        "Nenhuma acao auditavel executada nesta tela."
    )
    page.get_by_role("button", name="Aprovar empresa").click()
    expect(page.get_by_text("Empresa aprovada no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Auditoria operacional Business")).to_contain_text(
        "Ultima acao auditavel: approve em business/companies/"
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_label("Status operacional").select_option("approved")
    expect(page.get_by_label("Resumo filtrado Business")).to_contain_text("1")
    expect(page.get_by_text("Empresa Business Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/jobs/jobpostings",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Vaga Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Publicar vaga").click()
    expect(page.get_by_text("Vaga publicada no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="published")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/jobs/resumeaccesslogs",
        wait_until="domcontentloaded",
    )
    page.get_by_role("button", name="Registrar acesso a currículo").click()
    expect(
        page.get_by_text("Acesso a curriculo registrado no API Hub vivo.")
    ).to_be_visible(timeout=LIVE_API_EXPECT_TIMEOUT)
    expect(
        page.get_by_text("triagem para vaga publicada via Business shell")
    ).to_be_visible(timeout=LIVE_API_EXPECT_TIMEOUT)

    page.goto(
        f"{all_in_one_business_live_server}/erp/fiscaldocuments",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Relatorio de Giro Fiscal Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar registro ERP").click()
    expect(page.get_by_text("Registro ERP aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/bi/dashboards",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Dashboard Giro de Estoque Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar relatório BI").click()
    expect(page.get_by_text("Relatorio BI aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/wms/warehouses",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("CD Regional Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar operação WMS").click()
    expect(page.get_by_text("Operacao WMS aprovada no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/tms/freights", wait_until="domcontentloaded"
    )
    expect(page.get_by_text("Frete Regional Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar operação TMS").click()
    expect(page.get_by_text("Operacao TMS aprovada no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/crm/opportunities",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Oportunidade B2B Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar oportunidade CRM").click()
    expect(
        page.get_by_text("Oportunidade CRM aprovada no API Hub vivo.")
    ).to_be_visible(timeout=LIVE_API_EXPECT_TIMEOUT)
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/bpm/processes",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Fluxo BPM Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar fluxo BPM").click()
    expect(page.get_by_text("Fluxo BPM aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/document/documents",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("doc.pdf")).to_be_visible(timeout=LIVE_API_EXPECT_TIMEOUT)
    page.get_by_role("button", name="Aprovar documento").click()
    expect(
        page.get_by_text("Documento operacional aprovado no API Hub vivo.")
    ).to_be_visible(timeout=LIVE_API_EXPECT_TIMEOUT)
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/hr/employees", wait_until="domcontentloaded"
    )
    expect(page.get_by_text("Colaborador HR Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar registro HR").click()
    expect(page.get_by_text("Registro HR aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/api_hub/apiclients",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Cliente API Hub Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar cliente API Hub").click()
    expect(page.get_by_text("Cliente API Hub aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Auditoria operacional Business")).to_contain_text(
        "Ultima acao auditavel: approve em api_hub/api_clients/"
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/api_hub/apikeys",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Chave API Hub Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar cliente API Hub").click()
    expect(page.get_by_text("Cliente API Hub aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Auditoria operacional Business")).to_contain_text(
        "Ultima acao auditavel: approve em api_hub/api_keys/"
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/api_hub/webhooks",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("https://webhook.playwright.example/events")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar cliente API Hub").click()
    expect(page.get_by_text("Cliente API Hub aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Auditoria operacional Business")).to_contain_text(
        "Ultima acao auditavel: approve em api_hub/webhooks/"
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )

    page.goto(
        f"{all_in_one_business_live_server}/api_hub/integrationruns",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Apigee API Hub Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar cliente API Hub").click()
    expect(page.get_by_text("Cliente API Hub aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.get_by_label("Auditoria operacional Business")).to_contain_text(
        "Ultima acao auditavel: approve em api_hub/integration_runs/"
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )


def test_all_in_one_business_shell_runs_governance_live_api_hub_actions(
    page: Page, all_in_one_business_governance_live_server: str
) -> None:
    page.goto(
        f"{all_in_one_business_governance_live_server}/legal/cases",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Caso Legal Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar caso Legal").click()
    expect(page.get_by_text("Caso Legal aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible()

    page.goto(
        f"{all_in_one_business_governance_live_server}/property/properties",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Imovel Property Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar ativo Property").click()
    expect(page.get_by_text("Ativo Property aprovado no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible()

    page.goto(
        f"{all_in_one_business_governance_live_server}/vision/devices",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Camera Vision Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar dispositivo Vision").click()
    expect(
        page.get_by_text("Dispositivo Vision aprovado no API Hub vivo.")
    ).to_be_visible(timeout=LIVE_API_EXPECT_TIMEOUT)
    expect(page.locator(".badge", has_text="approved")).to_be_visible()

    page.goto(
        f"{all_in_one_business_governance_live_server}/ai_core/moderationdecisions",
        wait_until="domcontentloaded",
    )
    expect(page.get_by_text("Decisao AI Core Playwright")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    page.get_by_role("button", name="Aprovar decisão AI Core").click()
    expect(page.get_by_text("Decisao AI Core aprovada no API Hub vivo.")).to_be_visible(
        timeout=LIVE_API_EXPECT_TIMEOUT
    )
    expect(page.locator(".badge", has_text="approved")).to_be_visible()
