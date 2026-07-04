from playwright.sync_api import Page, Route, expect


def _assert_actor_header(route: Route) -> None:
    headers = route.request.headers
    actor_id = headers.get("x-actor-user-id") or headers.get("X-Actor-User-Id")
    assert actor_id, "O shell do usuario precisa enviar X-Actor-User-Id."


def _stub_user_shell_feed(page: Page) -> None:
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
                "orders_total": 48,
                "orders_paid": 41,
                "orders_completed": 39,
                "reviews_total": 12,
                "average_rating": 4.8,
                "support_cases_total": 6,
                "support_cases_open": 1,
                "support_cases_resolved": 5,
                "conversion_rate_percent": 17,
                "crm_records": 120,
                "bi_records": 64,
                "source": "api_hub",
            },
        )

    def serve_offers(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "offer_id": "offer-1",
                        "title": "Hamburguer Gourmet Valley",
                        "consumer_category": "Alimentacao",
                        "offer_type_label": "Alimento",
                        "primary_action_label": "Comprar Agora",
                        "region_label": "Centro",
                        "price_amount": "45.90",
                        "verified_seller": True,
                        "source_module": "marketplace",
                    },
                    {
                        "offer_id": "offer-2",
                        "title": "Consultoria de IA Estrategica",
                        "consumer_category": "Tecnologia",
                        "offer_type_label": "Servico",
                        "primary_action_label": "Solicitar Orcamento",
                        "region_label": "Online",
                        "price_amount": None,
                        "verified_seller": True,
                        "source_module": "marketplace",
                    },
                ],
            },
        )

    def serve_wallets(route: Route) -> None:
        _assert_actor_header(route)
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "wallet-1",
                        "status": "active",
                        "created_at": "2026-07-04T12:00:00Z",
                        "payload": {
                            "wallet_type": "consumer",
                            "currency": "BRL",
                            "balance_brl": "1280.55",
                        },
                    },
                    {
                        "id": "wallet-2",
                        "status": "active",
                        "created_at": "2026-07-04T12:05:00Z",
                        "payload": {
                            "wallet_type": "business",
                            "currency": "BRL",
                            "balance_brl": "802.10",
                        },
                    },
                ],
            },
        )

    def serve_vacancies(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": "vac-1",
                        "title": "Analista de Operacoes",
                        "company_name": "Valley Tech",
                        "description": "Operacao e suporte a jornadas logadas.",
                        "amount_brl": "5200.00",
                        "region_label": "Hibrido",
                        "status": "published",
                    },
                    {
                        "id": "vac-2",
                        "title": "Designer de Produto",
                        "company_name": "Valley Studio",
                        "description": "Experiencia do usuario e prototipacao.",
                        "amount_brl": "6100.00",
                        "region_label": "Remoto",
                        "status": "published",
                    },
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
        elif "8104" in url:
            payload = {
                "module": "delivery",
                "service": "delivery",
                "status": "healthy",
                "storage": "postgres",
                "version": "baseline",
            }
        elif "8106" in url:
            payload = {
                "module": "mobility",
                "service": "mobility",
                "status": "healthy",
                "storage": "postgres",
                "version": "baseline",
            }
        else:
            payload = {"status": "healthy"}
        route.fulfill(status=200, content_type="application/json", json=payload)

    page.route("**/gateway/status**", serve_gateway_status)
    page.route("**/gateway/insights/commercial**", serve_commercial_insights)
    page.route("**/gateway/catalog/offers**", serve_offers)
    page.route("**/wallets/**", serve_wallets)
    page.route("**/vacancies**", serve_vacancies)
    page.route("**/health**", serve_health)


def test_all_in_one_user_dashboard_reflete_feeds_reais(page: Page, all_in_one_user_server: str) -> None:
    _stub_user_shell_feed(page)

    page.goto(all_in_one_user_server, timeout=60000, wait_until="domcontentloaded")

    expect(page.get_by_role("heading", name="Experiencia do usuario em tempo real")).to_be_visible()
    expect(page.locator(".summary-card")).to_have_count(6)
    expect(page.get_by_text("gateway-signed")).to_be_visible()
    expect(page.locator(".metric-strip strong", has_text="4.8")).to_be_visible()
    expect(page.get_by_text("R$ 1.280,55")).to_be_visible()
    expect(page.get_by_text("R$ 802,10")).to_be_visible()
    expect(page.get_by_text("Hamburguer Gourmet Valley")).to_be_visible()
    expect(page.locator(".alert-box")).to_have_count(0)

    page.locator(".nav-pill", has_text="Conta").click()
    expect(page.get_by_role("heading", name="Identidade, login e consentimento")).to_be_visible()
    account_metrics = page.locator(".content-grid .metric-strip > div")
    expect(account_metrics.nth(0)).to_contain_text("identity")
    expect(account_metrics.nth(2)).to_contain_text("postgres")

    page.locator(".nav-pill", has_text="Carteira").click()
    expect(page.get_by_role("heading", name="Wallets do usuario")).to_be_visible()
    wallet_rows = page.locator(".content-grid .data-row")
    expect(wallet_rows).to_have_count(2)
    expect(wallet_rows.nth(0)).to_contain_text("consumer")
    expect(wallet_rows.nth(0)).to_contain_text("R$ 1.280,55")
    expect(wallet_rows.nth(1)).to_contain_text("business")
    expect(wallet_rows.nth(1)).to_contain_text("R$ 802,10")

    page.locator(".nav-pill", has_text="Operacao").click()
    expect(page.get_by_role("heading", name="Entrega e mobilidade")).to_be_visible()
    operation_metrics = page.locator(".content-grid .metric-strip > div")
    expect(operation_metrics.nth(0)).to_contain_text("healthy")
    expect(operation_metrics.nth(2)).to_contain_text("postgres")

    page.locator(".nav-pill", has_text="Vagas").click()
    expect(page.get_by_role("heading", name="Vagas e historico de candidatura")).to_be_visible()
    expect(page.get_by_text("Analista de Operacoes")).to_be_visible()


def test_all_in_one_user_search_filters_market_and_jobs(page: Page, all_in_one_user_server: str) -> None:
    _stub_user_shell_feed(page)

    page.goto(all_in_one_user_server, timeout=60000, wait_until="domcontentloaded")
    page.locator("input[type='search']").fill("Analista")

    page.locator(".nav-pill", has_text="Mercado").click()
    expect(page.get_by_role("heading", name="Ofertas e acoes disponiveis")).to_be_visible()
    expect(page.get_by_text("Nenhuma oferta encontrada para a busca atual.")).to_be_visible()

    page.locator(".nav-pill", has_text="Vagas").click()
    expect(page.get_by_role("heading", name="Vagas e historico de candidatura")).to_be_visible()
    expect(page.get_by_text("Analista de Operacoes")).to_be_visible()
    expect(page.get_by_text("Design")).to_have_count(0)
