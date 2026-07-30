from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from modules.marketplace.main import app
from modules.shared.marketplace_checkout_postgres_store import (
    MarketplaceCheckoutPostgresStore,
)
from modules.shared.marketplace_checkout_routes import (
    MarketplaceCheckoutRequest,
    _recover_concurrent_checkout_creation,
)


class _FakeResult:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def fetchone(self) -> dict[str, object] | None:
        return self._row


class _FakeConnection:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row
        self.parameters: tuple[object, ...] | None = None

    def execute(self, _query: str, parameters: tuple[object, ...]) -> _FakeResult:
        self.parameters = parameters
        return _FakeResult(self._row)


class _FakeStore:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.connection = _FakeConnection(row)


def _checkout_row(body: MarketplaceCheckoutRequest) -> dict[str, object]:
    now = datetime.now(UTC)
    user_id = uuid4()
    return {
        "id": uuid4(),
        "order_id": uuid4(),
        "cart_id": body.cart_id,
        "user_id": user_id,
        "company_id": uuid4(),
        "store_id": uuid4(),
        "status": "pending_payment",
        "payment_status": "not_started",
        "payment_method": body.payment_method,
        "currency": body.currency,
        "expected_total_brl": body.expected_total_brl,
        "total_brl": body.expected_total_brl,
        "reservation_ids": [uuid4()],
        "expires_at": now + timedelta(minutes=15),
        "escrow_id": None,
        "snapshot": {"items": []},
        "correlation_id": uuid4(),
        "confirmed_at": None,
        "cancelled_at": None,
        "created_at": now,
        "updated_at": now,
        "request_hash": MarketplaceCheckoutPostgresStore.checkout_request_hash(
            cart_id=str(body.cart_id),
            currency=body.currency,
            expected_total_brl=body.expected_total_brl,
            payment_method=body.payment_method,
        ),
    }


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


def test_concurrent_unique_violation_replays_same_checkout() -> None:
    body = MarketplaceCheckoutRequest(
        cart_id=uuid4(),
        currency="BRL",
        expected_total_brl=Decimal("10.00"),
        payment_method="wallet",
    )
    row = _checkout_row(body)
    store = _FakeStore(row)
    key = f"checkout-{uuid4()}"

    recovered = _recover_concurrent_checkout_creation(
        store=store,  # type: ignore[arg-type]
        body=body,
        user_id=str(row["user_id"]),
        idempotency_key=key,
    )

    assert recovered["checkout_id"] == str(row["id"])
    assert recovered["order_id"] == str(row["order_id"])
    assert store.connection.parameters == (str(row["user_id"]), key)


def test_concurrent_unique_violation_rejects_different_body() -> None:
    body = MarketplaceCheckoutRequest(
        cart_id=uuid4(),
        currency="BRL",
        expected_total_brl=Decimal("10.00"),
        payment_method="wallet",
    )
    row = _checkout_row(body)
    row["request_hash"] = "0" * 64
    store = _FakeStore(row)

    with pytest.raises(HTTPException) as caught:
        _recover_concurrent_checkout_creation(
            store=store,  # type: ignore[arg-type]
            body=body,
            user_id=str(row["user_id"]),
            idempotency_key=f"checkout-{uuid4()}",
        )

    assert caught.value.status_code == 409
    assert "outro corpo" in str(caught.value.detail).casefold()
