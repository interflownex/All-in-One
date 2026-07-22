from datetime import UTC, datetime

from playwright.sync_api import Page, Request, Route, expect


def test_valley_orders_support_and_review_journey(page: Page, superapp_server: str) -> None:
    user_id = "valley-orders-e2e-user"
    order_id = "order-orders-e2e"
    order_title = "Pedido de teste Valley"
    support_requests: list[dict] = []
    review_requests: list[dict] = []

    page.add_init_script(
        f"""
        window.localStorage.setItem('valley.session.token', 'token-orders-e2e');
        window.localStorage.setItem('valley.session.user-id', '{user_id}');
        """
    )

    def serve_orders(route: Route) -> None:
        route.fulfill(
            status=200,
            content_type="application/json",
            json={
                "data": [
                    {
                        "id": order_id,
                        "kind": "order",
                        "title": order_title,
                        "status": "completed",
                        "amount_brl": "74.90",
                        "created_at": datetime.now(UTC).isoformat(),
                    }
                ]
            },
        )

    def serve_support(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"},
            )
            return
        support_requests.append(request.post_data_json)
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "id": "support-orders-e2e",
                "order_id": order_id,
                "kind": request.post_data_json["kind"],
                "status": "open",
                "message": "Caso registrado. Vamos acompanhar a resolucao.",
            },
        )

    def serve_review(route: Route, request: Request) -> None:
        if request.method == "OPTIONS":
            route.fulfill(
                status=204,
                headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"},
            )
            return
        review_requests.append(request.post_data_json)
        route.fulfill(
            status=201,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "id": "review-orders-e2e",
                "order_id": order_id,
                "rating": request.post_data_json["rating"],
                "status": "published",
                "message": "Avaliacao publicada. Obrigado pelo retorno.",
            },
        )

    page.route("**/gateway/consumer/orders", serve_orders)
    page.route(f"**/gateway/consumer/orders/{order_id}/support*", serve_support)
    page.route(f"**/gateway/consumer/orders/{order_id}/reviews*", serve_review)

    page.goto(superapp_server, timeout=60000, wait_until="domcontentloaded")

    page.get_by_role("button", name="Meus Pedidos").click()

    drawer = page.locator(".orders-drawer")
    expect(drawer).to_be_visible()
    expect(drawer.get_by_role("heading", name="Meus Pedidos e Agendamentos")).to_be_visible()

    order_card = page.locator(".order-card", has_text=order_title)
    expect(order_card).to_be_visible()
    expect(order_card).to_contain_text("Status: Concluido")
    expect(order_card).to_contain_text("Valor: R$ 74,90")

    order_card.get_by_role("button", name="Abrir suporte").click()
    support_modal = page.locator(".support-modal")
    expect(support_modal).to_be_visible()
    expect(support_modal.get_by_role("heading", name="Abrir suporte")).to_be_visible()

    support_modal.locator("#support-subject").fill("Atraso na entrega")
    support_modal.locator("#support-message").fill("O pedido chegou fora do prazo combinado.")
    support_modal.locator("#support-resolution").fill("Quero reembolso ou reentrega.")
    support_modal.get_by_role("button", name="Disputa").click()
    support_modal.get_by_role("button", name="Registrar caso").click()

    expect(support_modal.get_by_role("status")).to_contain_text("Caso registrado")
    support_modal.get_by_label("Fechar").click()
    expect(page.locator(".support-modal")).to_have_count(0)

    order_card.get_by_role("button", name="Avaliar").click()
    review_modal = page.locator(".review-modal")
    expect(review_modal).to_be_visible()
    review_modal.get_by_role("button", name="5 de 5").click()
    review_modal.locator("#review-comment").fill("Entrega rápida e comunicação clara.")
    review_modal.get_by_role("button", name="Publicar avaliacao").click()

    expect(review_modal.get_by_role("status")).to_contain_text("Avaliacao publicada")
    review_modal.get_by_label("Fechar").click()
    expect(page.locator(".review-modal")).to_have_count(0)

    expect(page.get_by_role("button", name="Avaliacao enviada")).to_be_visible()

    assert support_requests[0]["kind"] == "dispute"
    assert support_requests[0]["subject"] == "Atraso na entrega"
    assert review_requests[0]["rating"] == 5
    assert review_requests[0]["comment"] == "Entrega rápida e comunicação clara."
