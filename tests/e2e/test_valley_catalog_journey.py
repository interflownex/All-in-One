from uuid import uuid4

from playwright.sync_api import Page, Request, Route, expect

from modules.shared.valley_catalog import valley_facets
from platform_test_support import fresh_client_for


def actor_headers(
    user_id: str,
    roles: str = "owner",
    *,
    business_id: str | None = None,
    mfa: bool = False,
) -> dict[str, str]:
    headers = {"X-Actor-User-Id": user_id, "X-Actor-Roles": roles, "X-Actor-Scopes": ""}
    if mfa:
        headers["X-MFA-Verified"] = "true"
    if business_id:
        headers["X-Business-Id"] = business_id
        headers["X-Business-Status"] = "active"
    return headers


def test_business_offer_appears_in_valley_and_triggers_checkout(
    page: Page, superapp_server: str
):
    """
    Testa a jornada E2E:
    1. Criação de oferta real no módulo Business via API.
    2. Visualização do Card da oferta recém-criada no frontend Valley Superapp.
    3. Simulação de clique no botão de "Comprar" ou "Contratar" que deve acionar o fluxo na UI.
    """
    # 1. Preparar dados backend via API real
    business = fresh_client_for("business")
    seller_id = str(uuid4())
    business_id = str(uuid4())
    headers = actor_headers(seller_id, "owner", business_id=business_id, mfa=True)

    unique_title = f"Produto E2E_{str(uuid4())[:8]}"

    created = business.post(
        "/resources/catalog_offers",
        headers=headers,
        json={
            "user_id": seller_id,
            "entity_id": business_id,
            "payload": {
                "title": unique_title,
                "description": "Produto exclusivo criado via jornada E2E para validacao.",
                "offer_type": "product",
                "consumer_category": "Compras e Produtos",
                "source_module": "marketplace",
                "source_resource_type": "products",
                "company_type": "pf_vendedor",
                "company_category": "Comercio",
                "business_activity_id": "varejo",
                "service_area": "local",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "service_radius_km": 10,
                "price_brl": "99.90",
                "publish_to_valley": True,
                "publication_status": "approved",
                "visible_to_consumer": True,
                "verified_seller": True,
            },
        },
    )
    assert created.status_code == 201

    offer_id = created.json()["id"]
    approved = business.post(
        f"/resources/catalog_offers/{offer_id}/actions/approve",
        headers=headers,
        json={
            "reason": "Oferta E2E validada",
            "payload": {"publication_status": "approved"},
        },
    )
    assert approved.status_code == 200

    catalog = business.get(
        "/valley/catalog/search",
        params={"q": unique_title, "lat": -23.5505, "lng": -46.6333},
    )
    assert catalog.status_code == 200
    normalized_offers = catalog.json()
    assert any(item["title"] == unique_title for item in normalized_offers)

    # Mockamos a comunicação do frontend com o API Hub para não depender dos containers rodando no ambiente de teste
    def serve_catalog(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": normalized_offers,
                "total": len(normalized_offers),
                "partial": False,
                "facets": valley_facets(normalized_offers),
            },
        )

    page.route("**/gateway/catalog/offers**", serve_catalog)

    buyer_id = str(uuid4())

    def serve_registrations(route: Route) -> None:
        route.fulfill(
            status=201,
            content_type="application/json",
            json={"id": buyer_id},
        )

    page.route("**/registrations", serve_registrations)

    def serve_login(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "access_token": "mock-jwt-token",
                "token_type": "bearer",
                "user_id": buyer_id,
            },
        )

    page.route("**/auth/login", serve_login)
    submitted_actions: list[dict] = []

    def create_order(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )
            return
        submitted_actions.append(request.post_data_json)
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "status": "created",
                "resource_id": "order-e2e",
                "message": "Pedido criado. O pagamento sera confirmado na proxima etapa.",
                "next_step": "payment_required",
                "payment_intent": {
                    "amount": "99.90",
                    "order_id": "00000000-0000-4000-8000-000000000001",
                },
            },
        )

    page.route("**/gateway/catalog/actions*", create_order)

    def process_payment(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )
            return
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "status": "paid",
                "order_id": "00000000-0000-4000-8000-000000000001",
                "message": "Pagamento sandbox autorizado e protegido ate a conclusao do pedido.",
            },
        )

    page.route("**/gateway/payments/sandbox/authorize*", process_payment)

    def get_orders(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )
            return
        route.fulfill(
            status=200,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "data": [
                    {
                        "id": "order-e2e",
                        "kind": "order",
                        "title": unique_title,
                        "status": "completed",
                        "amount_brl": "99.90",
                        "created_at": "2026-06-05T00:00:00Z",
                    }
                ]
            },
        )

    page.route("**/gateway/consumer/orders*", get_orders)
    submitted_reviews: list[dict] = []
    submitted_support_cases: list[dict] = []

    def create_review(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )
            return
        submitted_reviews.append(request.post_data_json)
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "id": "review-e2e",
                "order_id": "order-e2e",
                "rating": 5,
                "status": "published",
                "message": "Avaliacao publicada. Obrigado por compartilhar sua experiencia.",
            },
        )

    page.route("**/gateway/consumer/orders/order-e2e/reviews*", create_review)

    def create_support(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )
            return
        submitted_support_cases.append(request.post_data_json)
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "id": "support-e2e",
                "order_id": "order-e2e",
                "kind": "support",
                "status": "open",
                "message": "Caso registrado. Nossa equipe acompanha o retorno.",
            },
        )

    page.route("**/gateway/consumer/orders/order-e2e/support*", create_support)

    # 2. Abrir o Valley Superapp e buscar a oferta criada
    page.goto(superapp_server, timeout=60000, wait_until="domcontentloaded")

    # Preencher latitude/longitude e buscar
    page.locator("input[placeholder='Latitude']").fill("-23.5505")
    page.locator("input[placeholder='Longitude']").fill("-46.6333")

    # Preencher a busca textual com o titulo unico gerado
    search_input = page.locator("input[placeholder*='eletricista']")
    search_input.fill(unique_title)
    page.get_by_role("button", name="Buscar").click()

    # Localizar o card especifico pelo titulo (Aguarda o API Hub agregar a oferta do PostgreSQL real)
    card = page.locator(".offer-card", has_text=unique_title)
    expect(card).to_be_visible(timeout=15000)

    # Validar informacoes esteticas da oferta no frontend
    expect(card.locator(".price")).to_contain_text("R$ 99,90")
    expect(card.locator(".badge")).to_contain_text("Produto")
    expect(card).to_contain_text("Compras e Produtos")

    # 3. Interagir com o fluxo (Clicar na Acao Principal)
    buy_button = card.locator("button", has_text="Comprar")
    expect(buy_button).to_be_visible()
    buy_button.click()

    # Validar se o Modal Neo-brutalista de Login abre
    login_modal = page.locator(".login-modal")
    expect(login_modal).to_be_visible()

    # Navegar para Cadastro
    page.get_by_role("button", name="Ainda nao tem conta? Cadastre-se").click()

    # Preencher dados
    buyer_email = f"buyer_{str(uuid4())[:8]}@valley.com"
    page.locator("input[type='email']").fill(buyer_email)
    page.locator("input[type='password']").fill("SenhaForte123!")

    # Enviar form (usar login_modal para evitar conflito com o botao do Header)
    login_modal.get_by_role("button", name="Cadastrar", exact=True).click()

    # Validar se o Modal Neo-brutalista de Checkout abre automaticamente apos login
    checkout_modal = page.locator(".checkout-modal")
    expect(checkout_modal).to_be_visible(timeout=10000)
    expect(checkout_modal).to_contain_text(unique_title)
    expect(checkout_modal).to_contain_text("Finalizar pedido")

    # Clicar em Confirmar pedido
    confirm_button = page.locator(".checkout-modal button", has_text="Confirmar pedido")
    confirm_button.click()

    # Aguardar feedback de sucesso que veio do API Hub real comunicando-se com Marketplace
    feedback = page.locator(".checkout-modal .action-feedback.success")
    expect(feedback).to_be_visible(timeout=15000)
    expect(feedback).to_contain_text("Pedido criado")
    assert len(submitted_actions) == 1
    published_offer = next(
        item for item in normalized_offers if item["title"] == unique_title
    )
    assert submitted_actions[0]["offer_id"] == published_offer["offer_id"]
    assert submitted_actions[0]["customer_user_id"] == buyer_id

    # 4. Validar abertura do Payment Modal
    payment_modal = page.locator(".payment-modal")
    expect(payment_modal).to_be_visible(timeout=10000)
    expect(payment_modal).to_contain_text("Pagamento Seguro")
    expect(payment_modal).to_contain_text("R$ 99,90")

    # 5. Clicar em Pagar com PIX
    pay_button = payment_modal.locator("button", has_text="Pagar com PIX")
    pay_button.click()

    # 6. Aguardar feedback de sucesso
    payment_feedback = payment_modal.locator(".action-feedback.success")
    expect(payment_feedback).to_be_visible(timeout=10000)
    expect(payment_feedback).to_contain_text("Pagamento sandbox autorizado")

    # 7. Validar abertura do Orders Drawer
    orders_drawer = page.locator(".orders-drawer")
    expect(orders_drawer).to_be_visible(timeout=10000)
    expect(orders_drawer).to_contain_text("Meus Pedidos e Agendamentos")

    # Validar listagem
    order_card = orders_drawer.locator(".order-card")
    expect(order_card).to_have_count(1)
    expect(order_card).to_contain_text(unique_title)
    expect(order_card).to_contain_text("R$ 99,90")

    # 8. Avaliar o pedido concluido e confirmar o envio ao API Hub
    order_card.get_by_role("button", name="Avaliar").click()
    review_modal = page.locator(".review-modal")
    expect(review_modal).to_be_visible()
    review_modal.get_by_role("button", name="5 de 5").click()
    review_modal.locator("textarea").fill("Experiencia concluida com sucesso.")
    review_modal.get_by_role("button", name="Publicar avaliacao").click()
    expect(review_modal.get_by_role("status")).to_contain_text("Avaliacao publicada")
    assert len(submitted_reviews) == 1
    assert submitted_reviews[0]["rating"] == 5
    assert submitted_reviews[0]["comment"] == "Experiencia concluida com sucesso."
    assert submitted_reviews[0]["idempotency_key"].startswith("review-order-e2e-")
    review_modal.locator(".actions").get_by_role("button", name="Fechar").click()

    order_card.get_by_role("button", name="Abrir suporte").click()
    support_modal = page.locator(".support-modal")
    expect(support_modal).to_be_visible()
    support_modal.get_by_role("button", name="Disputa").click()
    support_modal.locator("#support-subject").fill("Atraso na entrega")
    support_modal.locator("#support-message").fill(
        "Preciso de uma atualizacao do pedido."
    )
    support_modal.locator("#support-resolution").fill("Contato do fornecedor.")
    support_modal.get_by_role("button", name="Registrar caso").click()
    expect(support_modal.get_by_role("status")).to_contain_text("Caso registrado")
    assert len(submitted_support_cases) == 1
    assert submitted_support_cases[0]["kind"] == "dispute"
    assert submitted_support_cases[0]["subject"] == "Atraso na entrega"
