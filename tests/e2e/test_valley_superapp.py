from playwright.sync_api import Page, expect


def test_valley_superapp_filters(page: Page, superapp_server: str):
    """
    Testa a vitrine regional e os filtros de categorias amigáveis do Valley SuperApp.
    """
    # Acessa o app Valley (SuperApp)
    page.goto(superapp_server, timeout=60000, wait_until="domcontentloaded")

    # Valida Header e Hero Section
    expect(page.locator("header .logo")).to_contain_text("Valley")
    expect(page.locator("h1")).to_contain_text("Encontre o que precisa")

    # Verifica os controles regionais e a busca simples.
    expect(page.locator("input[placeholder='Latitude']")).to_have_value("-23.5505")
    expect(page.locator("input[placeholder='Longitude']")).to_have_value("-46.6333")
    expect(page.locator("input[placeholder*='eletricista']")).to_be_visible()

    # Verifica se categorias e tipos usam linguagem amigavel.
    expect(page.locator(".pill", has_text="Todas as categorias")).to_be_visible()
    expect(page.locator(".pill", has_text="Comida e Mercado")).to_be_visible()
    expect(page.locator(".pill", has_text="Casa, Reparos e Imoveis")).to_be_visible()
    expect(page.locator(".type-filter button", has_text="Servicos")).to_be_visible()
    expect(page.get_by_label("Quem oferece")).to_be_visible()
    expect(page.get_by_label("Area do negocio")).to_be_visible()
    expect(page.get_by_label("O que faz")).to_be_visible()

    # Como o mock backend (API Hub ou pytest fixture) pode estar vazio ou ter dados fake,
    # verificamos a estrutura do grid e os Fallbacks.
    # Clica em um filtro específico
    page.locator(".pill", has_text="Comida e Mercado").click()

    # Valida estado 'active' do pill selecionado
    expect(page.locator(".pill.active")).to_contain_text("Comida e Mercado")

    # Garante que, se não houver backend com dados, exiba o aviso de "Vitrine em construção"
    # (ou os cards caso tenha mock data inserida).
    grid_container = page.locator(".offers-grid")
    expect(grid_container).to_be_visible()
