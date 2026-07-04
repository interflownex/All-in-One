from playwright.sync_api import Page, expect


def test_valley_business_navigation(page: Page, business_server: str):
    """
    Testa o carregamento B2B Dashboard e sua navegação baseada em layout.
    """
    # Acessa o app (Desktop default viewport)
    page.goto(business_server, timeout=60000)

    # Valida a marca e o título principal
    expect(page.get_by_alt_text("Valley")).to_be_visible()
    expect(page.locator(".sidebar-logo")).to_contain_text("Business")
    expect(page.locator("h1")).to_contain_text("Visão Geral do Negócio")

    # Valida a visualização principal (Dashboard Inicial)
    expect(page.locator(".wallet-badge")).to_contain_text("V-Gold")

    # Valida a visualização principal (Dashboard Inicial)
    # Clica na aba de Carteira Gold
    page.locator("text=Carteira Gold").click()

    # Verifica se a interface mudou para a carteira
    expect(page.locator("h1")).to_contain_text("Gestão de Valley Gold")
    expect(page.get_by_placeholder("Quantidade de V-Gold")).to_be_visible()
    expect(page.get_by_role("button", name="Gerar Pix Copia e Cola")).to_be_visible()
    
    # Valida se a listagem do Catálogo aparece
    page.locator("text=Catálogo de Ofertas").click()
    expect(page.get_by_role("heading", name="Catálogo (Valley API Hub)")).to_be_visible()
    expect(page.locator("text=Corte de Cabelo + Barba")).to_be_visible()

    # Valida a visualização de Telemetria
    page.locator("text=Telemetria Outbox").click()
    expect(page.locator("h1")).to_contain_text("Monitoramento de Telemetria")
    expect(page.get_by_role("heading", name="Monitoramento de Eventos (Outbox)")).to_be_visible()
