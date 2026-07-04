from playwright.sync_api import Page, expect, Route


def test_valley_superapp_filters(page: Page, superapp_server: str):
    """
    Testa a vitrine regional e os filtros de categorias amigaveis do Valley SuperApp.
    """

    def serve_offers(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "offer_id": "offer-food-1",
                        "title": "Hamburguer Gourmet Valley",
                        "short_description": "Blend de 180g, queijo canastra e cebola caramelizada.",
                        "price_amount": "45.90",
                        "price_type": "fixed",
                        "consumer_category": "Alimentacao",
                        "offer_type": "food",
                        "offer_type_label": "Alimento",
                        "source_module": "marketplace",
                        "provider_label": "Valley Store",
                        "region_label": "Sao Paulo, SP",
                        "distance_km": 1.2,
                        "consumer_action": "buy",
                        "primary_action_label": "Comprar Agora",
                        "verified_seller": True,
                        "metadata": {
                            "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
                        },
                    },
                    {
                        "offer_id": "offer-service-1",
                        "title": "Consultoria de IA Estrategica",
                        "short_description": "Implementacao de agentes inteligentes e automacao de processos.",
                        "price_amount": None,
                        "price_type": "quote",
                        "consumer_category": "Tecnologia",
                        "offer_type": "service",
                        "offer_type_label": "Servico",
                        "source_module": "marketplace",
                        "provider_label": "Valley Tech",
                        "region_label": "Online",
                        "distance_km": 0,
                        "consumer_action": "request",
                        "primary_action_label": "Solicitar Orcamento",
                        "verified_seller": True,
                        "metadata": {
                            "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80",
                        },
                    },
                ],
                "facets": {
                    "company_types": [
                        {"id": "pro", "label": "Profissionais", "count": 12},
                    ],
                    "company_categories": [
                        {"id": "tech", "label": "Tecnologia", "count": 8},
                    ],
                    "business_activities": [
                        {"id": "consultoria", "label": "Consultoria", "count": 5},
                    ],
                },
            },
        )

    page.route("**/gateway/catalog/offers**", serve_offers)

    # Acessa o app Valley (SuperApp)
    page.goto(superapp_server, timeout=60000, wait_until="domcontentloaded")

    # Valida Header e Hero Section
    expect(page.get_by_alt_text("Valley")).to_be_visible()
    expect(page.get_by_role("heading", name="Encontre o que precisa")).to_be_visible()

    # Verifica os controles regionais e a busca simples.
    expect(page.get_by_placeholder("Ex.: eletricista, marmita, psicologo")).to_be_visible()
    expect(page.locator(".type-filter")).to_be_visible()
    expect(page.get_by_role("button", name="Tudo")).to_be_visible()
    expect(page.get_by_role("button", name="Comida e Mercado")).to_be_visible()
    expect(page.get_by_role("button", name="Casa, Reparos e Imoveis")).to_be_visible()
    expect(page.get_by_role("combobox", name="Quem oferece")).to_be_visible()
    expect(page.get_by_role("combobox", name="Area do negocio")).to_be_visible()
    expect(page.get_by_role("combobox", name="O que faz")).to_be_visible()

    # Garante que a vitrine carrega os cards e o filtro ativo responde ao clique.
    expect(page.locator(".offers-grid")).to_be_visible()
    expect(page.locator(".offer-card", has_text="Hamburguer Gourmet Valley")).to_be_visible()
    expect(page.locator(".offer-card", has_text="Consultoria de IA Estrategica")).to_be_visible()

    page.get_by_role("button", name="Comida e Mercado").click()
    expect(page.locator(".pill.active", has_text="Comida e Mercado")).to_be_visible()
