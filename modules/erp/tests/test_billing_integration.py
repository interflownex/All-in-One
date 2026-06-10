import pytest
from fastapi.testclient import TestClient
from modules.erp.main import app
from uuid import uuid4
import os

client = TestClient(app)

@pytest.fixture
def auth_headers():
    return {
        "X-Actor-User-Id": str(uuid4()),
        "X-Actor-Company-Id": str(uuid4()),
        "X-Idempotency-Key": f"test-billing-{uuid4().hex[:8]}"
    }

def test_create_billing_with_items_and_sandbox(auth_headers):
    """Valida a criação de faturamento, persistência de itens e resposta do sandbox fiscal."""
    payload = {
        "amount_brl": "150.00",
        "tax_amount_brl": "15.00",
        "document_type": "nfe",
        "items": [
            {
                "description": "Serviço de Consultoria Técnica",
                "quantity": 1,
                "unit_price_brl": "100.00",
                "total_price_brl": "100.00",
                "tax_amount_brl": "10.00"
            },
            {
                "description": "Licença de Software",
                "quantity": 1,
                "unit_price_brl": "50.00",
                "total_price_brl": "50.00",
                "tax_amount_brl": "5.00"
            }
        ]
    }

    response = client.post("/erp/billing", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "pending"
    assert data["items_count"] == 2

    assert "fiscal_authorization" in data
    assert data["fiscal_authorization"]["status"] == "authorized"
    assert "auth_code" in data["fiscal_authorization"]