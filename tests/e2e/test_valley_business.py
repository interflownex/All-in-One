from playwright.sync_api import Page, expect


def test_valley_business_navigation(page: Page, business_server: str):
    """
    Testa o carregamento B2B Dashboard e sua navegação baseada em layout.
    """
    # Acessa o app (Desktop default viewport)
    page.goto(business_server, timeout=60000)

    # Valida Sidebar Title
    expect(page.locator(".sidebar-logo")).to_contain_text("Valley Business")

    # Valida a visualização principal (Dashboard Inicial)
    expect(page.locator("h1")).to_contain_text("Visão Geral do Negócio")

    # Verifica o Badge da carteira Gold global (sempre visível)
    expect(page.locator(".wallet-badge")).to_contain_text("V-Gold")

    # Clica na aba de Carteira Gold
    page.locator("text=Carteira Gold").click()

    # Verifica se a interface mudou para o Ledger
    expect(page.locator("h1")).to_contain_text("Gestão de Valley Gold")
    expect(page.locator("text=Histórico Append-Only")).to_be_visible()

    # Valida se a listagem do Catálogo aparece
    page.locator("text=Catálogo de Ofertas").click()
    expect(page.locator("h3:has-text('Catálogo')")).to_be_visible()
    expect(page.locator("text=Corte de Cabelo + Barba")).to_be_visible()

    # Valida a visualização de Telemetria
    page.locator("text=Telemetria Outbox").click()
    expect(page.locator("h1")).to_contain_text("Monitoramento de Telemetria")
    expect(
        page.locator("h3:has-text('Monitoramento de Eventos (Outbox)')")
    ).to_be_visible()
