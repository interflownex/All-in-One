import re
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import Page, Route, expect

LIVE_ACTION_TIMEOUT = 60000
APP_SOURCE = (
    Path(__file__).resolve().parents[2] / "apps" / "all-in-one" / "src" / "App.tsx"
)


USER_JOURNEY_ROUTES = [
    ("/identity", "Identity", "Perfil Playwright"),
    ("/finance/wallets", "Wallets", "Wallet Playwright"),
    ("/marketplace/orders", "Orders", "Pedido Playwright"),
    ("/delivery/deliveryrequests", "Delivery Requests", "Entrega Playwright"),
    ("/jobs/jobpostings", "Job Postings", "Vaga Playwright"),
]

USER_LIVE_JOURNEY_ROUTES = [
    ("/identity", "Identity", "Perfil Playwright"),
    ("/finance/wallets", "Wallets", "Wallet Playwright"),
    ("/marketplace/orders", "Orders", "store-phase4-user"),
    ("/delivery/deliveryrequests", "Delivery Requests", "last_mile"),
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


def test_all_in_one_user_shell_runs_consumer_journey(
    page: Page, all_in_one_user_server: str
) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)

    page.goto(all_in_one_user_server, wait_until="domcontentloaded")

    expect(page.locator("h1")).to_contain_text("Todos os sistemas.")
    expect(page.locator(".aio-module-card")).to_have_count(25)
    expect(page.get_by_role("link", name="Abrir dashboard")).to_have_count(25)

    for path, title, fixture_name in USER_JOURNEY_ROUTES:
        page.goto(f"{all_in_one_user_server}{path}", wait_until="domcontentloaded")

        expect(page.locator("h1")).to_contain_text(title)
        expect(page.get_by_placeholder(f"Buscar em {title}...")).to_be_visible()
        expect(page.get_by_text(fixture_name)).to_be_visible(timeout=10000)


def test_all_in_one_user_shell_keeps_mobile_journey_reachable(
    page: Page, all_in_one_user_server: str
) -> None:
    page.route("**/gateway/**", _serve_gateway_collection)
    page.set_viewport_size({"width": 390, "height": 844})

    page.goto(
        f"{all_in_one_user_server}/marketplace/orders", wait_until="domcontentloaded"
    )

    expect(page.locator("h1")).to_contain_text("Orders")
    expect(page.get_by_text("Pedido Playwright")).to_be_visible(timeout=10000)
    expect(page.get_by_placeholder("Buscar em Orders...")).to_be_visible()


def test_all_in_one_user_shell_completes_live_order_and_delivery_actions(
    page: Page, all_in_one_user_live_server: str
) -> None:
    page.goto(all_in_one_user_live_server, wait_until="domcontentloaded")

    expect(page.locator("h1")).to_contain_text("Todos os sistemas.")

    for path, title, fixture_name in USER_LIVE_JOURNEY_ROUTES:
        page.goto(f"{all_in_one_user_live_server}{path}", wait_until="domcontentloaded")

        expect(page.locator("h1")).to_contain_text(title)
        expect(page.get_by_text(fixture_name)).to_be_visible(timeout=15000)
        expect(page.get_by_text("ID:")).to_be_visible(timeout=15000)

    page.goto(
        f"{all_in_one_user_live_server}/marketplace/orders",
        wait_until="domcontentloaded",
    )
    order_panel = page.get_by_label("Acao de jornada User")
    expect(
        order_panel.get_by_role("button", name="Concluir jornada User")
    ).to_be_enabled(timeout=LIVE_ACTION_TIMEOUT)
    order_panel.get_by_role("button", name="Concluir jornada User").click()
    expect(order_panel.locator(".journey-feedback.completed")).to_contain_text(
        "pedido paid", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(page.locator(".badge", has_text="paid")).to_be_visible(
        timeout=LIVE_ACTION_TIMEOUT
    )

    page.goto(
        f"{all_in_one_user_live_server}/delivery/deliveryrequests",
        wait_until="domcontentloaded",
    )
    delivery_panel = page.get_by_label("Acao de jornada User")
    expect(
        delivery_panel.get_by_role("button", name="Concluir jornada User")
    ).to_be_enabled(timeout=LIVE_ACTION_TIMEOUT)
    delivery_panel.get_by_role("button", name="Concluir jornada User").click()
    expect(delivery_panel.locator(".journey-feedback.completed")).to_contain_text(
        "entrega completed", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(page.locator(".badge", has_text="completed")).to_be_visible(
        timeout=LIVE_ACTION_TIMEOUT
    )


def test_all_in_one_user_shell_submits_live_job_application(
    page: Page, all_in_one_user_jobs_live_server: str
) -> None:
    page.goto(
        f"{all_in_one_user_jobs_live_server}/jobs/jobpostings",
        wait_until="domcontentloaded",
    )
    expect(page.locator("h1")).to_contain_text(
        "Job Postings", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(page.get_by_text("Vaga Playwright")).to_be_visible(timeout=15000)
    jobs_status = page.get_by_label("Busca notificacoes e pos-candidatura Jobs")
    expect(jobs_status).to_contain_text(
        "vaga publicada encontrada", timeout=LIVE_ACTION_TIMEOUT
    )

    page.get_by_placeholder("Buscar em Job Postings...").fill("Jornada")
    page.get_by_role("button", name="Pesquisar").click()
    expect(jobs_status).to_contain_text(
        "Busca aplicada: Jornada", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(page.get_by_text("Vaga Playwright")).to_be_visible(
        timeout=LIVE_ACTION_TIMEOUT
    )

    jobs_panel = page.get_by_label("Acao de jornada User")
    expect(
        jobs_panel.get_by_role("button", name="Concluir jornada User")
    ).to_be_enabled(timeout=LIVE_ACTION_TIMEOUT)
    jobs_panel.get_by_role("button", name="Concluir jornada User").click()
    expect(jobs_panel.locator(".journey-feedback.completed")).to_contain_text(
        "candidatura submitted", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(jobs_status).to_contain_text(
        "Notificacao Jobs: candidatura enviada com sucesso.",
        timeout=LIVE_ACTION_TIMEOUT,
    )
    expect(jobs_status).to_contain_text(
        "Pos-candidatura Jobs", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(jobs_status).to_contain_text(
        "Status: submitted", timeout=LIVE_ACTION_TIMEOUT
    )
    expect(page.locator(".badge", has_text="submitted")).to_be_visible(
        timeout=LIVE_ACTION_TIMEOUT
    )


def test_all_in_one_user_shell_crud_has_no_dead_actions(
    page: Page, all_in_one_user_server: str
) -> None:
    page.goto(
        f"{all_in_one_user_server}/identity/users-form", wait_until="domcontentloaded"
    )
    page.get_by_label("Nome / Identificador").fill("Pessoa Funcional")
    page.get_by_label("Descrição Detalhada").fill("Registro criado pelo teste E2E")
    page.get_by_label("Categoria / Tipo").select_option("Estrategico")
    page.get_by_role("button", name="Salvar Registro").click()

    expect(page).to_have_url(re.compile(r"/identity/users$"), timeout=10000)
    expect(page.get_by_text("Pessoa Funcional")).to_be_visible(timeout=10000)

    page.get_by_role("button", name="Editar").click()
    expect(
        page.get_by_role("heading", name=re.compile("Editar Registro"))
    ).to_be_visible()
    name_field = page.get_by_label("Nome / Identificador")
    name_field.fill("Pessoa Atualizada")
    page.get_by_role("button", name="Salvar Registro").click()

    expect(page.get_by_text("Pessoa Atualizada")).to_be_visible(timeout=10000)
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Excluir").click()
    expect(page.get_by_text("Pessoa Atualizada")).to_have_count(0)


def test_all_in_one_user_shell_renders_every_registered_route_without_runtime_errors(
    page: Page, all_in_one_user_preview_server: str
) -> None:
    routes = re.findall(
        r'<Route path="([^"]+)"', APP_SOURCE.read_text(encoding="utf-8")
    )
    assert len(routes) == len(set(routes)) >= 335

    runtime_errors: list[str] = []
    page.on("pageerror", lambda error: runtime_errors.append(str(error)))

    for path in routes:
        page.goto(
            f"{all_in_one_user_preview_server}{path}", wait_until="domcontentloaded"
        )
        if path == "/":
            expect(page.locator("h1")).to_contain_text("Todos os sistemas.")
        expect(page.locator("h1, form h2").first).to_be_visible(timeout=15000)
        if page.locator("form h2").count():
            expect(page.locator("form h2")).to_contain_text("Novo Registro")
            expect(page.get_by_role("button", name="Salvar Registro")).to_be_enabled()
            expect(page.get_by_role("button", name="Cancelar")).to_be_enabled()
        elif path != "/":
            expect(page.locator("h1")).to_be_visible()
            expect(page.get_by_role("button", name="Pesquisar")).to_be_enabled()
            expect(page.get_by_role("button", name="Novo registro")).to_be_enabled()

        assert "Carregando..." not in page.locator("body").inner_text()

    assert not runtime_errors, (
        "Erros JavaScript durante auditoria integral: " + " | ".join(runtime_errors)
    )


def test_all_in_one_user_shell_exercises_every_shared_control_type(
    page: Page, all_in_one_user_server: str
) -> None:
    page.goto(
        f"{all_in_one_user_server}/finance/wallets", wait_until="domcontentloaded"
    )

    search = page.get_by_placeholder("Buscar em Wallets...")
    search.fill("Carteira principal")
    page.get_by_role("button", name="Pesquisar").click()
    expect(page.get_by_text("Carteira principal").first).to_be_visible()

    page.get_by_role("button", name="Ver detalhes").first.click()
    expect(page.get_by_role("dialog")).to_be_visible()
    page.get_by_role("button", name="Fechar detalhes").click()
    expect(page.get_by_role("dialog")).to_have_count(0)

    page.get_by_role("button", name="Novo registro").click()
    expect(page).to_have_url(re.compile(r"/finance/wallets-form$"))
    page.get_by_role("button", name="Cancelar").click()
    expect(page).to_have_url(re.compile(r"/finance/wallets$"))

    page.get_by_role("button", name="Editar").first.click()
    expect(
        page.get_by_role("heading", name=re.compile("Editar Registro"))
    ).to_be_visible()
    page.get_by_role("button", name="Cancelar").click()
    expect(page).to_have_url(re.compile(r"/finance/wallets$"))
