from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from modules.api_hub import main as api_hub


class FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Any:
        return self._payload


class FakeCatalogClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.posts: list[tuple[str, dict[str, Any], dict[str, str]]] = []

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float,
    ) -> FakeResponse:
        self.calls.append((url, params or {}))
        if url.endswith(
            "marketplace:8000/resources/orders/00000000-0000-4000-8000-000000000002"
        ):
            return FakeResponse(
                200,
                {
                    "id": "order-completed",
                    "user_id": "11111111-1111-4111-8111-111111111111",
                    "status": "completed",
                    "payload": {
                        "store_id": "00000000-0000-4000-8000-000000000099",
                        "business_id": "00000000-0000-4000-8000-000000000099",
                        "offer_id": "business:catalog_offers:offer-1",
                    },
                },
            )
        if url.endswith(
            "marketplace:8000/resources/orders/00000000-0000-4000-8000-000000000001"
        ):
            return FakeResponse(
                200,
                {
                    "id": "resource-created",
                    "user_id": "11111111-1111-4111-8111-111111111111",
                    "status": "created",
                    "payload": {
                        "total_brl": "99.90",
                        "seller_user_id": "seller-1",
                        "offer_title": "Produto Valley",
                    },
                },
            )
        if url.endswith("crm:8000/status"):
            return FakeResponse(
                200, {"records": 3, "audit_events": 1, "outbox_events": 1}
            )
        if url.endswith("bi:8000/status"):
            return FakeResponse(
                200, {"records": 2, "audit_events": 1, "outbox_events": 1}
            )
        if url.endswith("marketplace:8000/valley/insights/commercial"):
            return FakeResponse(
                200,
                {
                    "orders_total": 2,
                    "orders_paid": 1,
                    "orders_completed": 1,
                    "reviews_total": 1,
                    "reviews_pending_moderation": 1,
                    "average_rating": 5.0,
                    "support_cases_total": 1,
                    "support_cases_open": 1,
                    "support_cases_resolved": 0,
                    "conversion_rate_percent": 50.0,
                    "source": "marketplace.commercial_insights",
                },
            )
        if url.endswith("marketplace:8000/resources/orders"):
            return FakeResponse(
                200,
                [
                    {
                        "id": "resource-created",
                        "status": "created",
                        "created_at": "2026-06-05T12:00:00Z",
                        "payload": {
                            "offer_title": "Produto Valley",
                            "total_brl": "99.90",
                        },
                    }
                ],
            )
        if url.endswith("health:8000/resources/appointments") or url.endswith(
            "services:8000/resources/service_contracts"
        ):
            return FakeResponse(200, [])
        if "/valley/catalog/offers/" in url:
            return FakeResponse(
                200,
                {
                    "offer_id": "business:catalog_offers:offer-1",
                    "offer_type": "product",
                    "consumer_action": "buy",
                    "title": "Produto Valley",
                    "source_module": "marketplace",
                    "source_resource_type": "products",
                    "source_entity_id": "offer-1",
                    "seller_user_id": "seller-1",
                    "business_id": "store-1",
                    "availability_status": "available",
                    "price_amount": "99.90",
                },
            )
        if url.endswith("business:8000/valley/catalog/search"):
            return FakeResponse(
                200,
                [
                    {
                        "offer_id": "business:catalog_offers:offer-1",
                        "offer_type": "service",
                        "offer_type_label": "Servico",
                        "consumer_category": "Casa, Reparos e Imoveis",
                        "title": "Eletricista residencial",
                        "short_description": "Atendimento eletrico em residencias.",
                        "source_module": "services",
                        "source_resource_type": "providers",
                        "source_entity_id": "offer-1",
                        "availability_status": "available",
                        "service_area": "local",
                        "service_radius_km": 15,
                        "distance_km": 2.4,
                        "company_type": "pf_profissional",
                        "company_type_label": "Profissional autonomo",
                        "company_category": "Servicos",
                        "business_activity_id": "servicos_domesticos",
                        "business_activity_label": "Casa e manutencao",
                        "provider_label": "Profissional verificado",
                        "primary_action_label": "Contratar",
                    },
                    {
                        "offer_id": "module:services",
                        "title": "Servicos",
                        "availability_status": "coming_soon",
                        "service_area": "national",
                    },
                ],
            )
        if url.endswith("services:8000/valley/catalog/search"):
            return FakeResponse(
                200,
                [
                    {
                        "offer_id": "module:services",
                        "title": "Servicos",
                        "availability_status": "coming_soon",
                        "service_area": "national",
                    }
                ],
            )
        return FakeResponse(503, {"detail": "indisponivel"})

    async def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> FakeResponse:
        self.posts.append((url, json, headers))
        if url.endswith("finance:8000/integrations/sandbox/psp/pix/authorize"):
            return FakeResponse(
                200, {"status": "authorized", "reference_id": "pix-ref"}
            )
        if url.endswith("finance:8000/integrations/sandbox/psp/escrows"):
            return FakeResponse(200, {"status": "held", "reference_id": "escrow-ref"})
        if url.endswith(
            "marketplace:8000/resources/orders/00000000-0000-4000-8000-000000000001/actions/pay"
        ):
            return FakeResponse(200, {"id": "resource-created", "status": "paid"})
        if url.endswith("marketplace:8000/resources/reviews"):
            return FakeResponse(
                201, {"id": "review-created", "status": "pending_review"}
            )
        if url.endswith(
            "marketplace:8000/valley/orders/00000000-0000-4000-8000-000000000002/support"
        ):
            return FakeResponse(
                201,
                {
                    "id": "support-created",
                    "status": "open",
                    "message": "Caso registrado.",
                },
            )
        return FakeResponse(201, {"id": "resource-created", "status": "created"})


def test_gateway_aggregates_business_offer_with_consumer_filters(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)

    response = client.get(
        "/gateway/catalog/offers",
        params={
            "q": "eletricista",
            "category": "Casa, Reparos e Imoveis",
            "offer_type": "service",
            "lat": -23.5505,
            "lng": -46.6333,
            "company_type": "pf_profissional",
            "company_category": "Servicos",
            "business_activity": "servicos_domesticos",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-valley-signature-algorithm"] == "Ed25519"
    assert response.headers["x-valley-response-signature"]
    payload = response.json()
    assert payload["partial"] is True
    assert payload["total"] == 2
    assert sum(item["offer_id"] == "module:services" for item in payload["data"]) == 1
    assert payload["facets"]["company_types"] == [
        {"id": "pf_profissional", "label": "Profissional autonomo", "count": 1}
    ]
    assert payload["facets"]["company_categories"] == [
        {"id": "Servicos", "label": "Servicos", "count": 1}
    ]
    assert payload["facets"]["business_activities"] == [
        {"id": "servicos_domesticos", "label": "Casa e manutencao", "count": 1}
    ]

    offer = next(
        item
        for item in payload["data"]
        if item["offer_id"] == "business:catalog_offers:offer-1"
    )
    assert offer["title"] == "Eletricista residencial"
    assert offer["source_module"] == "services"
    assert offer["consumer_category"] == "Casa, Reparos e Imoveis"
    assert offer["business_activity_id"] == "servicos_domesticos"

    assert len(fake_client.calls) == len(api_hub.CATALOG_SOURCE_MODULES)
    assert all(url.endswith("/valley/catalog/search") for url, _ in fake_client.calls)
    forwarded = fake_client.calls[0][1]
    assert forwarded["offer_type"] == "service"
    assert forwarded["company_type"] == "pf_profissional"
    assert forwarded["business_activity"] == "servicos_domesticos"


def test_gateway_applies_pagination_after_global_deduplication(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)

    response = client.get("/gateway/catalog/offers", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["limit"] == 1
    assert payload["offset"] == 1
    assert len(payload["data"]) == 1


def test_gateway_creates_marketplace_order_from_canonical_offer(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.post(
        "/gateway/catalog/actions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "offer_id": "business:catalog_offers:offer-1",
            "action": "buy",
            "customer_user_id": user_id,
            "idempotency_key": "checkout-offer-1",
            "quantity": 2,
        },
    )

    assert response.status_code == 201
    assert response.headers["x-valley-signature-algorithm"] == "Ed25519"
    assert response.headers["x-valley-response-signature"]
    assert response.json() == {
        "status": "created",
        "action": "buy",
        "target_module": "marketplace",
        "resource_type": "orders",
        "resource_id": "resource-created",
        "next_step": "payment_required",
        "message": "Pedido criado. O pagamento sera confirmado na proxima etapa.",
        "payment_intent": {
            "amount": "99.90",
            "order_id": "resource-created",
        },
    }
    assert len(fake_client.posts) == 1
    url, request_body, headers = fake_client.posts[0]
    assert url.endswith("marketplace:8000/resources/orders")
    assert headers["X-Idempotency-Key"] == "checkout-offer-1"
    assert request_body["payload"]["total_brl"] == "99.90"
    assert request_body["payload"]["store_id"] == "store-1"
    assert request_body["payload"]["items"][0]["quantity"] == 2


def test_gateway_rejects_action_different_from_published_offer(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.post(
        "/gateway/catalog/actions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "offer_id": "business:catalog_offers:offer-1",
            "action": "hire",
            "customer_user_id": user_id,
            "idempotency_key": "checkout-offer-1",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"] == "A acao solicitada nao corresponde a esta oferta."
    )


def test_gateway_authorizes_pix_sandbox_using_server_side_order_data(
    monkeypatch,
) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.post(
        "/gateway/payments/sandbox/authorize",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "order_id": "00000000-0000-4000-8000-000000000001",
            "idempotency_key": "payment-resource-created",
            "method": "pix_sandbox",
        },
    )

    assert response.status_code == 200
    assert response.headers["x-valley-signature-algorithm"] == "Ed25519"
    assert response.headers["x-valley-response-signature"]
    assert response.json()["status"] == "paid"
    assert response.json()["provider_environment"] == "sandbox"
    pix_call = next(
        call for call in fake_client.posts if call[0].endswith("/psp/pix/authorize")
    )
    assert pix_call[1]["amount_brl"] == "99.90"
    assert pix_call[1]["payer_id"] == user_id
    escrow_call = next(
        call for call in fake_client.posts if call[0].endswith("/psp/escrows")
    )
    assert escrow_call[1]["beneficiary_id"] == "seller-1"
    assert fake_client.posts[-1][0].endswith("/actions/pay")
    pay_payload = fake_client.posts[-1][1]
    assert "Pix" not in pay_payload["reason"]
    assert "pix" not in pay_payload["payload"]["payment_provider"]


def test_gateway_returns_normalized_consumer_history(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.get(
        "/gateway/consumer/orders",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "id": "resource-created",
                "kind": "order",
                "title": "Produto Valley",
                "status": "created",
                "amount_brl": "99.90",
                "scheduled_at": None,
                "created_at": "2026-06-05T12:00:00Z",
                "updated_at": None,
            }
        ],
        "total": 1,
        "partial": False,
        "failures": [],
    }


def test_gateway_returns_partial_history_when_module_fails(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    # Mock services:8000 to raise RequestError
    original_get = fake_client.get

    async def mock_get(url: str, **kwargs):
        if url.endswith("services:8000/resources/service_contracts"):
            import httpx

            raise httpx.RequestError(
                "Conexao recusada", request=httpx.Request("GET", url)
            )
        return await original_get(url, **kwargs)

    fake_client.get = mock_get
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.get(
        "/gateway/consumer/orders",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["partial"] is True
    assert len(payload["failures"]) == 1
    assert payload["failures"][0]["module"] == "services"
    assert payload["failures"][0]["error"] == "RequestError"


def test_gateway_creates_review_only_for_completed_owned_order(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.post(
        "/gateway/consumer/orders/00000000-0000-4000-8000-000000000002/reviews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "rating": 5,
            "comment": "Entrega concluida com cuidado.",
            "idempotency_key": "review-order-completed",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending_review"
    review_call = fake_client.posts[-1]
    assert review_call[0].endswith("marketplace:8000/resources/reviews")
    assert review_call[2]["X-Idempotency-Key"] == "review-order-completed"
    assert review_call[1]["payload"]["rating"] == 5
    assert (
        review_call[1]["payload"]["order_id"] == "00000000-0000-4000-8000-000000000002"
    )
    assert review_call[1]["payload"]["moderation_status"] == "pending_review"


def test_gateway_rejects_review_before_order_completion(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.post(
        "/gateway/consumer/orders/00000000-0000-4000-8000-000000000001/reviews",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "rating": 4,
            "idempotency_key": "review-order-created",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "A avaliacao fica disponivel apos a conclusao do pedido."
    )


def test_gateway_creates_support_case_for_owned_paid_order(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)
    user_id = "11111111-1111-4111-8111-111111111111"
    token = api_hub.jwt.encode({"sub": user_id}, api_hub.JWT_SECRET, algorithm="HS256")

    response = client.post(
        "/gateway/consumer/orders/00000000-0000-4000-8000-000000000002/support",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "kind": "support",
            "subject": "Atraso na entrega",
            "message": "Preciso de uma atualizacao do pedido.",
            "desired_resolution": "Contato do fornecedor.",
            "idempotency_key": "support-order-completed",
        },
    )

    assert response.status_code == 201
    assert response.json()["kind"] == "support"
    assert response.json()["status"] == "open"
    support_call = fake_client.posts[-1]
    assert support_call[0].endswith(
        "marketplace:8000/valley/orders/00000000-0000-4000-8000-000000000002/support"
    )
    assert support_call[2]["X-Idempotency-Key"] == "support-order-completed"
    assert support_call[1]["kind"] == "support"


def test_gateway_returns_commercial_insights(monkeypatch) -> None:
    fake_client = FakeCatalogClient()
    monkeypatch.setattr(api_hub, "client", fake_client)
    monkeypatch.setattr(api_hub, "redis_client", None)
    client = TestClient(api_hub.app)

    response = client.get("/gateway/insights/commercial")

    assert response.status_code == 200
    payload = response.json()
    assert payload["orders_total"] == 2
    assert payload["reviews_total"] == 1
    assert payload["support_cases_total"] == 1
    assert payload["crm_records"] == 3
    assert payload["bi_records"] == 2
    assert payload["commercial_attention"]["pending_reviews"] == 1
    assert payload["commercial_attention"]["open_support_cases"] == 1
    assert payload["commercial_attention"]["signal_count"] == 4
    assert payload["notification_policy"]["include_sensitive_payload"] is False
