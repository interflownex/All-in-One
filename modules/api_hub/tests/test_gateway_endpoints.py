from uuid import uuid4

from platform_test_support import client_for


def test_gateway_public_reviews():
    # Public review route should not throw 401/403 since it's unauthenticated
    client = client_for("api_hub")
    response = client.get("/gateway/reviews?limit=5")
    # It might return 502 if downstream service is mock/empty, but should not return 404
    assert response.status_code in {200, 502}


def test_gateway_resolve_dispute_unauthenticated():
    client = client_for("api_hub")
    dispute_id = str(uuid4())
    # A rota autenticada deve rejeitar a chamada sem token e cabecalhos.
    response = client.post(
        f"/gateway/merchant/disputes/{dispute_id}/resolve",
        json={"resolution_notes": "Resolving.", "action": "resolve"},
    )
    assert response.status_code in {401, 403, 502}
