from uuid import uuid4

from fastapi.testclient import TestClient

from modules.business.main import app
from modules.business.module_settings import (
    BusinessClassificationInput,
    recommend_business_modules,
)


def test_recommend_business_modules_for_ecommerce():
    recommendations = recommend_business_modules(
        BusinessClassificationInput(
            businessKind="ecommerce",
            hasPhysicalStock=True,
            sellsOnline=True,
            performsDelivery=True,
            issuesFiscalDocuments=True,
        )
    )

    states = {item.module_slug: item.state for item in recommendations}

    assert states["identity"] == "mandatory"
    assert states["business"] == "mandatory"
    assert states["permissions"] == "mandatory"
    assert states["marketplace"] == "active"
    assert states["finance"] == "active"
    assert states["stock"] == "active"
    assert states["delivery"] == "active"
    assert states["health"] == "hidden"


def test_apply_and_patch_company_modules_endpoint():
    client = TestClient(app)
    company_id = uuid4()

    apply_response = client.post(
        f"/business-modules/companies/{company_id}/apply-recommendations",
        json={
            "actor_id": "pytest",
            "classification": {
                "businessKind": "restaurant",
                "hasPhysicalStock": True,
                "sellsOnline": False,
                "performsDelivery": True,
                "hiresPeople": True,
                "issuesFiscalDocuments": True,
                "operatesFleet": False,
                "hasWarehouse": False,
            },
        },
    )

    assert apply_response.status_code == 200
    body = apply_response.json()
    assert body["company_id"] == str(company_id)
    assert any(
        module["module_slug"] == "delivery" and module["state"] == "active"
        for module in body["modules"]
    )
    assert body["audit"][0]["action"] == "business.module.recommendations_applied"

    patch_response = client.patch(
        f"/business-modules/companies/{company_id}/modules/stock",
        json={
            "state": "hidden",
            "reason": "Empresa optou por controlar estoque em outro sistema por enquanto.",
        },
    )

    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["module_slug"] == "stock"
    assert patched["state"] == "hidden"
    assert patched["visibility"] == "hidden"
    assert patched["source"] == "manual"


def test_mandatory_module_cannot_be_hidden():
    client = TestClient(app)
    company_id = uuid4()

    client.post(
        f"/business-modules/companies/{company_id}/apply-recommendations",
        json={
            "classification": {
                "businessKind": "office",
                "hasPhysicalStock": False,
                "sellsOnline": False,
                "performsDelivery": False,
                "hiresPeople": True,
                "issuesFiscalDocuments": True,
                "operatesFleet": False,
                "hasWarehouse": False,
            },
        },
    )

    response = client.patch(
        f"/business-modules/companies/{company_id}/modules/identity",
        json={"state": "hidden", "reason": "Tentativa de ocultar modulo essencial."},
    )

    assert response.status_code == 409
    assert "Modulo obrigatorio" in response.json()["detail"]
