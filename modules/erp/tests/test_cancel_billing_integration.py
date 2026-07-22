from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from modules.erp.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers():
    return {
        "X-Actor-User-Id": str(uuid4()),
        "X-Actor-Company-Id": str(uuid4()),
        "X-Idempotency-Key": f"test-cancel-{uuid4().hex[:8]}",
    }


def test_cancel_billing_success(auth_headers):
    """Valida o fluxo completo de criação e cancelamento de um faturamento no ERP."""
    billing_payload = {
        "amount_brl": "250.00",
        "tax_amount_brl": "25.00",
        "document_type": "nfe",
        "items": [
            {
                "description": "Licença de Software Mensal",
                "quantity": 1,
                "unit_price_brl": "250.00",
                "total_price_brl": "250.00",
                "tax_amount_brl": "25.00",
            }
        ],
    }
    create_response = client.post(
        "/erp/billing", json=billing_payload, headers=auth_headers
    )
    assert create_response.status_code == 200
    doc_id = create_response.json()["id"]

    cancel_reason = "Pedido duplicado pelo cliente"
    cancel_payload = {"reason": cancel_reason}
    cancel_response = client.post(
        f"/erp/billing/{doc_id}/cancel", json=cancel_payload, headers=auth_headers
    )

    assert cancel_response.status_code == 200
    data = cancel_response.json()
    assert data["status"] == "cancelled"
    assert data["payload"]["cancel_reason"] == cancel_reason

    assert "fiscal_cancellation" in data
    assert data["fiscal_cancellation"]["status"] == "cancelled"
    assert "auth_code" in data["fiscal_cancellation"]


def test_cancel_billing_not_found(auth_headers):
    """Valida que o sistema retorna erro ao tentar cancelar um documento inexistente."""
    fake_id = str(uuid4())
    cancel_payload = {"reason": "Teste de erro"}
    response = client.post(
        f"/erp/billing/{fake_id}/cancel", json=cancel_payload, headers=auth_headers
    )

    assert response.status_code == 400
    assert "Documento fiscal não encontrado" in response.json()["detail"]
