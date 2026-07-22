from playwright.sync_api import Page, expect


def test_valley_rider_online_toggle(page: Page, rider_server: str):
    """
    Testa se o entregador consegue alternar entre Online e Offline no app Rider.
    A UI Mobile-first e a renderização do estado são avaliadas.
    """
    # Emula dispositivo móvel setando viewport reduzido
    page.set_viewport_size({"width": 375, "height": 812})

    # Acessa o app
    page.goto(rider_server)

    # Valida presença do cabeçalho
    expect(page.locator(".header")).to_be_visible()
    expect(page.locator("text=V Rider")).to_be_visible()

    # Captura o botão de status (por padrão inicializa como ONLINE no App.tsx)
    status_toggle = page.locator(".status-toggle")
    expect(status_toggle).to_contain_text("ONLINE")

    # O conteúdo deve mostrar 'Oportunidades' e 'Mapa' quando Online
    expect(page.locator("text=Mapa Dinâmico")).to_be_visible()
    expect(page.locator("text=Entrega Expressa")).to_be_visible()

    # Clica para ficar OFFLINE
    status_toggle.click()

    # Valida mudança visual e textual
    expect(status_toggle).to_contain_text("OFFLINE")

    # Verifica se os Jobs sumiram e a mensagem de repouso apareceu
    expect(page.locator("text=Fique online para receber solicitações")).to_be_visible()
    expect(page.locator("text=Entrega Expressa")).not_to_be_visible()


def test_valley_rider_tabs_navigation(page: Page, rider_server: str):
    """
    Testa se o entregador consegue navegar pela tabbar inferior.
    """
    page.set_viewport_size({"width": 375, "height": 812})
    page.goto(rider_server)

    # Clica na aba de ganhos
    page.locator("text=Ganhos").click()
    expect(page.locator("text=Ganhos Hoje")).to_be_visible()
    expect(page.locator("text=Entregas Concluídas")).to_be_visible()

    # Clica na aba de perfil
    page.locator("text=Perfil").click()
    expect(page.locator("text=Perfil do Rider")).to_be_visible()
    expect(page.locator("text=Avaliação")).to_be_visible()
