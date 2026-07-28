from uuid import uuid4

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


def test_valley_catalog_lists_all_modules_with_simple_categories() -> None:
    marketplace = fresh_client_for("marketplace")

    modules = marketplace.get("/valley/catalog/modules")
    assert modules.status_code == 200
    payload = modules.json()
    assert len(payload) == 24
    assert {item["source_module"] for item in payload} >= {
        "health",
        "services",
        "marketplace",
        "delivery",
    }
    assert {item["consumer_category"] for item in payload} >= {
        "Saude e Bem-estar",
        "Casa, Reparos e Imoveis",
        "Comida e Mercado",
    }
    assert all(item["consumer_title"] != item["source_module"] for item in payload)

    offers = marketplace.get("/valley/catalog/offers")
    assert offers.status_code == 200
    source_modules = {item["source_module"] for item in offers.json()}
    assert len(source_modules) == 24
    assert all(
        item["offer_type"] in {"food", "product", "service"} for item in offers.json()
    )


def test_valley_catalog_search_filters_food_product_service_and_radius() -> None:
    marketplace = fresh_client_for("marketplace")
    merchant_id = str(uuid4())
    business_id = str(uuid4())

    near_food = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-food",
                "sku": "FOOD-ALPHA",
                "name": "Marmita local",
                "description": "Alimento pronto para entrega regional",
                "price_brl": "29.90",
                "stock_location_type": "local_physical",
                "stock_quantity": 10,
                "publish_to_valley": True,
                "publication_status": "approved",
                "offer_type": "food",
                "consumer_category": "Comida e Mercado",
                "company_type": "mei",
                "company_category": "Comercio",
                "business_activity_id": "alimentacao",
                "service_area": "local",
                "service_radius_km": 5,
                "latitude": -23.5505,
                "longitude": -46.6333,
                "region_label": "Centro de Sao Paulo",
                "rewards": ["Pepitas"],
            },
        },
    )
    assert near_food.status_code == 201

    far_food = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-food",
                "sku": "FOOD-BETA",
                "name": "Marmita fora do raio",
                "description": "Alimento longe do usuario",
                "price_brl": "32.90",
                "stock_location_type": "local_physical",
                "stock_quantity": 10,
                "publish_to_valley": True,
                "publication_status": "approved",
                "offer_type": "food",
                "consumer_category": "Comida e Mercado",
                "company_type": "mei",
                "company_category": "Comercio",
                "business_activity_id": "alimentacao",
                "service_area": "local",
                "service_radius_km": 2,
                "latitude": -22.9068,
                "longitude": -43.1729,
                "region_label": "Rio de Janeiro",
            },
        },
    )
    assert far_food.status_code == 201

    online_product = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-digital",
                "sku": "DIGITAL-ALPHA",
                "name": "Curso digital",
                "description": "Produto digital disponivel online",
                "price_brl": "49.90",
                "stock_location_type": "local_physical",
                "stock_quantity": 99,
                "publish_to_valley": True,
                "publication_status": "approved",
                "offer_type": "product",
                "consumer_category": "Compras e Produtos",
                "company_type": "microempresa",
                "company_category": "Comercio",
                "business_activity_id": "educacao",
                "service_area": "online",
                "region_label": "Online",
            },
        },
    )
    assert online_product.status_code == 201

    local_without_radius = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-local",
                "sku": "LOCAL-NO-RADIUS",
                "name": "Produto local incompleto",
                "description": "Produto local sem raio cadastrado",
                "price_brl": "19.90",
                "stock_location_type": "local_physical",
                "stock_quantity": 3,
                "publish_to_valley": True,
                "publication_status": "approved",
                "offer_type": "product",
                "consumer_category": "Compras e Produtos",
                "company_type": "microempresa",
                "company_category": "Comercio",
                "business_activity_id": "varejo",
                "service_area": "local",
                "latitude": -23.5505,
                "longitude": -46.6333,
            },
        },
    )
    assert local_without_radius.status_code == 201

    food_results = marketplace.get(
        "/valley/catalog/search",
        params={"offer_type": "food", "lat": -23.551, "lng": -46.634},
    )
    assert food_results.status_code == 200
    titles = [item["title"] for item in food_results.json()]
    assert "Marmita local" in titles
    assert "Marmita fora do raio" not in titles
    assert all(item["offer_type"] == "food" for item in food_results.json())
    local_offer = next(
        item for item in food_results.json() if item["title"] == "Marmita local"
    )
    assert local_offer["distance_km"] is not None
    assert local_offer["distance_km"] <= local_offer["service_radius_km"]

    product_results = marketplace.get(
        "/valley/catalog/search",
        params={"offer_type": "product", "lat": -23.551, "lng": -46.634},
    )
    product_titles = [item["title"] for item in product_results.json()]
    assert "Curso digital" in product_titles
    assert "Produto local incompleto" not in product_titles

    mei_food = marketplace.get(
        "/valley/catalog",
        params={
            "company_type": "mei",
            "company_category": "Comercio",
            "business_activity": "alimentacao",
        },
    )
    assert mei_food.status_code == 200
    assert any(item["title"] == "Marmita local" for item in mei_food.json())
    food_offer = next(
        item for item in mei_food.json() if item["title"] == "Marmita local"
    )
    assert food_offer["primary_action_label"] == "Comprar"
    assert food_offer["short_description"]
    assert len(food_offer["short_description"]) <= 160

    detail = marketplace.get(f"/valley/catalog/offers/{food_offer['offer_id']}")
    assert detail.status_code == 200
    assert detail.json()["business_activity_label"] == "Restaurantes e mercados"


def test_valley_catalog_groups_repair_health_and_food_in_plain_language() -> None:
    services = fresh_client_for("services")
    provider_id = str(uuid4())

    provider = services.post(
        "/resources/providers",
        headers=actor_headers(provider_id),
        json={
            "user_id": provider_id,
            "payload": {
                "category": "eletricista residencial",
                "public_title": "Eletricista residencial",
                "public_description": "Reparos eletricos para casas e apartamentos",
                "offer_type": "service",
                "publish_to_valley": True,
                "publication_status": "approved",
                "consumer_category": "Casa, Reparos e Imoveis",
                "company_type": "pf_profissional",
                "company_category": "Servicos",
                "business_activity_id": "servicos_domesticos",
                "service_radius_km": 12,
                "latitude": -23.5505,
                "longitude": -46.6333,
                "region_label": "Sao Paulo",
            },
        },
    )
    assert provider.status_code == 201

    repairs = services.get(
        "/valley/catalog/search",
        params={"category": "Casa", "lat": -23.551, "lng": -46.634},
    )
    assert repairs.status_code == 200
    assert any(item["title"] == "Eletricista residencial" for item in repairs.json())
    assert any(item["source_module"] == "property" for item in repairs.json())

    health = services.get("/valley/catalog/search", params={"category": "Saude"})
    assert health.status_code == 200
    assert any(item["source_module"] == "health" for item in health.json())
    assert all("consumer_category" in item for item in health.json())


def test_valley_catalog_hides_business_offers_without_publication_authorization() -> (
    None
):
    marketplace = fresh_client_for("marketplace")
    merchant_id = str(uuid4())
    business_id = str(uuid4())

    draft = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-hidden",
                "sku": "HIDDEN-ALPHA",
                "name": "Produto ainda nao autorizado",
                "description": "Nao deve aparecer no Valley sem aprovacao Business",
                "price_brl": "10.00",
                "stock_location_type": "local_physical",
                "stock_quantity": 1,
                "offer_type": "product",
                "consumer_category": "Compras e Produtos",
                "service_area": "online",
            },
        },
    )
    assert draft.status_code == 201

    visible = marketplace.post(
        "/resources/products",
        headers=actor_headers(merchant_id, "merchant", business_id=business_id),
        json={
            "user_id": merchant_id,
            "entity_id": business_id,
            "payload": {
                "store_id": "store-visible",
                "sku": "VISIBLE-ALPHA",
                "name": "Produto autorizado",
                "description": "Configurado no Business para publicacao no Valley",
                "price_brl": "20.00",
                "stock_location_type": "local_physical",
                "stock_quantity": 4,
                "offer_type": "product",
                "consumer_category": "Compras e Produtos",
                "company_type": "microempresa",
                "company_category": "Comercio",
                "business_activity_id": "varejo",
                "service_area": "online",
                "publish_to_valley": True,
                "publication_status": "approved",
                "verified_seller": True,
            },
        },
    )
    assert visible.status_code == 201

    results = marketplace.get(
        "/valley/catalog/search", params={"q": "Produto", "verified_only": True}
    )
    assert results.status_code == 200
    titles = [item["title"] for item in results.json()]
    assert "Produto autorizado" in titles
    assert "Produto ainda nao autorizado" not in titles


def test_valley_catalog_exposes_business_activity_reference() -> None:
    marketplace = fresh_client_for("marketplace")

    activities = marketplace.get("/valley/catalog/business-activities")
    assert activities.status_code == 200
    payload = activities.json()
    ids = {item["business_activity_id"] for item in payload}
    assert {"alimentacao", "varejo", "saude", "servicos_domesticos", "logistica"} <= ids
    assert all("label_for_consumer" in item for item in payload)


def test_business_catalog_offer_publishes_product_to_valley_with_simple_filters() -> (
    None
):
    business = fresh_client_for("business")
    seller_id = str(uuid4())
    business_id = str(uuid4())
    headers = actor_headers(seller_id, "owner", business_id=business_id, mfa=True)

    created = business.post(
        "/resources/catalog_offers",
        headers=headers,
        json={
            "user_id": seller_id,
            "entity_id": business_id,
            "payload": {
                "title": "Kit cafe artesanal",
                "description": "Produto local configurado no Business para aparecer no Valley.",
                "offer_type": "product",
                "consumer_category": "Compras e Produtos",
                "source_module": "marketplace",
                "source_resource_type": "products",
                "company_type": "pf_vendedor",
                "company_category": "Comercio",
                "business_activity_id": "varejo",
                "service_area": "online",
                "region_label": "Online",
                "price_brl": "79.90",
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
            "reason": "Oferta comercial revisada",
            "payload": {"publication_status": "approved"},
        },
    )
    assert approved.status_code == 200

    results = business.get(
        "/valley/catalog/search",
        params={
            "offer_type": "product",
            "company_type": "pf_vendedor",
            "company_category": "Comercio",
            "business_activity": "varejo",
            "verified_only": True,
        },
    )
    assert results.status_code == 200
    offer = next(
        item for item in results.json() if item["title"] == "Kit cafe artesanal"
    )
    assert offer["source_module"] == "marketplace"
    assert offer["source_resource_type"] == "products"
    assert offer["configured_in_module"] == "business"
    assert offer["offer_type_label"] == "Produto"
    assert offer["business_activity_label"] == "Produtos e lojas"
    assert offer["seller_context_label"] == "Vendedor pessoa fisica em Produtos e lojas"
    assert offer["primary_action_label"] == "Comprar"
    assert "Produto em Compras e Produtos" in offer["consumer_filter_text"]

    facets = business.get("/valley/catalog/facets")
    assert facets.status_code == 200
    facet_payload = facets.json()
    assert any(
        item["id"] == "product" and item["label"] == "Produto"
        for item in facet_payload["offer_types"]
    )
    assert any(item["id"] == "pf_vendedor" for item in facet_payload["company_types"])
    assert any(
        item["id"] == "varejo" and item["label"] == "Produtos e lojas"
        for item in facet_payload["business_activities"]
    )


def test_business_catalog_offer_publishes_service_to_valley_by_activity_and_radius() -> (
    None
):
    business = fresh_client_for("business")
    provider_id = str(uuid4())
    business_id = str(uuid4())
    headers = actor_headers(provider_id, "owner", business_id=business_id, mfa=True)

    created = business.post(
        "/resources/catalog_offers",
        headers=headers,
        json={
            "user_id": provider_id,
            "entity_id": business_id,
            "payload": {
                "title": "Montagem de moveis",
                "description": "Servico residencial cadastrado no Business com atendimento regional.",
                "offer_type": "service",
                "consumer_category": "Casa, Reparos e Imoveis",
                "source_module": "services",
                "source_resource_type": "providers",
                "company_type": "pf_profissional",
                "company_category": "Servicos",
                "business_activity_id": "servicos_domesticos",
                "service_area": "local",
                "service_radius_km": 8,
                "latitude": -23.5505,
                "longitude": -46.6333,
                "region_label": "Centro de Sao Paulo",
                "price_type": "sob_orcamento",
                "publish_to_valley": True,
                "publication_status": "approved",
                "visible_to_consumer": True,
            },
        },
    )
    assert created.status_code == 201
    offer_id = created.json()["id"]
    approved = business.post(
        f"/resources/catalog_offers/{offer_id}/actions/approve",
        headers=headers,
        json={
            "reason": "Prestador revisado",
            "payload": {"publication_status": "approved"},
        },
    )
    assert approved.status_code == 200

    nearby = business.get(
        "/valley/catalog/search",
        params={
            "category": "Casa",
            "offer_type": "service",
            "lat": -23.551,
            "lng": -46.634,
            "business_activity": "servicos_domesticos",
        },
    )
    assert nearby.status_code == 200
    offer = next(
        item for item in nearby.json() if item["title"] == "Montagem de moveis"
    )
    assert offer["distance_km"] is not None
    assert offer["distance_km"] <= offer["service_radius_km"]
    assert offer["primary_action_label"] == "Contratar"
    assert offer["seller_context_label"] == "Profissional autonomo em Casa e manutencao"

    far = business.get(
        "/valley/catalog/search",
        params={"q": "Montagem", "lat": -22.9068, "lng": -43.1729},
    )
    assert far.status_code == 200
    assert "Montagem de moveis" not in [item["title"] for item in far.json()]
