from uuid import uuid4

from fastapi.testclient import TestClient

from modules.property.main import app


def _create_property(
    *,
    title: str,
    status: str,
    public_listing: bool = True,
    rent_amount: str = "1800.00",
) -> dict:
    store = app.extra["store"]
    owner_id = str(uuid4())
    return store.create(
        "properties",
        owner_id,
        None,
        status,
        {
            "title": title,
            "description": "Apartamento com varanda e acesso controlado.",
            "property_type": "apartamento",
            "region": "Betim, MG",
            "address": {
                "street": "Rua protegida",
                "number": "999",
                "neighborhood": "Centro",
                "city": "Betim",
                "state": "MG",
            },
            "rent_amount": rent_amount,
            "bedrooms": 2,
            "bathrooms": 1,
            "area_m2": 62,
            "public_listing": public_listing,
        },
        owner_id,
        (),
        "property.property.created",
        str(uuid4()),
    )


def test_valley_property_catalog_exposes_only_public_available_listings() -> None:
    marker = f"valley-catalog-{uuid4()}"
    available = _create_property(title=f"{marker}-available", status="available")
    _create_property(title=f"{marker}-draft", status="draft")
    _create_property(
        title=f"{marker}-private",
        status="available",
        public_listing=False,
    )

    response = TestClient(app).get(
        "/valley/catalog",
        params={"q": marker, "region": "Betim", "property_type": "apartamento"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == available["id"]
    assert body["items"][0]["public_address"] == "Centro, Betim, MG"
    assert "Rua protegida" not in str(body)
    assert "999" not in str(body)


def test_valley_property_catalog_applies_maximum_rent_filter() -> None:
    marker = f"valley-price-{uuid4()}"
    affordable = _create_property(
        title=f"{marker}-affordable",
        status="published",
        rent_amount="1400.00",
    )
    _create_property(
        title=f"{marker}-expensive",
        status="published",
        rent_amount="4500.00",
    )

    response = TestClient(app).get(
        "/valley/catalog",
        params={"q": marker, "max_price_brl": "2000.00"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == affordable["id"]
    assert body["items"][0]["rent_amount"] == 1400.0
