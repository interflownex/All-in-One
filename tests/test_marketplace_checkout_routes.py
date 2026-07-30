from uuid import uuid4

from fastapi.testclient import TestClient

from modules.marketplace.main import app


def test_marketplace_registers_checkout_routes_once() -> None:
    paths = [route.path for route in app.routes]
    assert paths.count("/valley/checkout") == 1
    assert paths.count("/valley/checkout/{checkout_id}") == 1
    assert paths.count("/valley/checkout/{checkout_id}/confirm") == 1
    assert paths.count("/valley/checkout/{checkout_id}/cancel") == 1


def test_checkout_creation_is_blocked_while_feature_flag_is_off(monkeypatch) -> None:
    monkeypatch.delenv("MARKETPLACE_CHECKOUT_V1_ENABLED", raising=False)
    monkeypatch.delenv("ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN", raising=False)
    actor_id = uuid4()
    response = TestClient(app).post(
        "/valley/checkout",
        headers={
            "X-Actor-User-Id": str(actor_id),
            "X-Idempotency-Key": f"checkout-{uuid4()}",
            "X-Correlation-Id": str(uuid4()),
        },
        json={
            "cart_id": str(uuid4()),
            "currency": "BRL",
            "expected_total_brl": "10.00",
            "payment_method": "wallet",
        },
    )
    assert response.status_code == 503
    assert "feature flag" in response.json()["detail"].casefold()
