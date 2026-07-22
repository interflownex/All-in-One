from __future__ import annotations

import hashlib
import hmac
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from modules.api_hub import main as api_hub


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def disable_api_hub_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_hub, "redis_client", None)


def test_gateway_public_status_surface_is_minimal() -> None:
    with TestClient(api_hub.app) as client:
        response = client.get("/gateway/status")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"service", "status", "security", "rate_limit", "routes"}
    assert payload["status"] == "active"
    assert payload["security"] == "JWT_EDGE_VALIDATION_ENABLED"
    assert "JWT_SECRET" not in str(payload)
    assert "WEBHOOK_SECRET" not in str(payload)


@pytest.mark.parametrize(
    ("method", "path", "json_body", "detail"),
    [
        ("get", "/gateway/consumer/orders", None, "Entre no Valley para continuar."),
        (
            "post",
            "/gateway/catalog/actions",
            {
                "offer_id": "business:catalog_offers:offer-1",
                "action": "buy",
                "customer_user_id": str(uuid4()),
                "idempotency_key": "security-smoke-001",
            },
            "Entre no Valley para continuar.",
        ),
    ],
)
def test_gateway_stateful_routes_require_bearer_token(
    method: str,
    path: str,
    json_body: dict[str, object] | None,
    detail: str,
) -> None:
    with TestClient(api_hub.app) as client:
        response = client.request(method.upper(), path, json=json_body)

    assert response.status_code == 401
    assert response.json()["detail"] == detail


def test_gateway_api_key_and_webhook_validation_are_strict() -> None:
    body = b"{}"
    signature = hmac.new(
        api_hub.WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    with TestClient(api_hub.app) as client:
        missing_key = client.get("/gateway/api-key/check")
        invalid_key = client.get("/gateway/api-key/check", headers={"X-API-Key": "invalid"})
        valid_key = client.get("/gateway/api-key/check", headers={"X-API-Key": "local-api-key"})
        invalid_webhook = client.post("/gateway/webhooks/verify", content=body, headers={"X-All-In-One-Signature": "sha256=bad"})
        valid_webhook = client.post(
            "/gateway/webhooks/verify",
            content=body,
            headers={"X-All-In-One-Signature": f"sha256={signature}"},
        )

    assert missing_key.status_code == 401
    assert missing_key.json()["detail"] == "API key ausente."
    assert invalid_key.status_code == 401
    assert invalid_key.json()["detail"] == "API key invalida."
    assert valid_key.status_code == 200
    assert valid_key.json() == {
        "status": "valid",
        "client_id": "local-client",
        "scopes": ["*"],
    }
    assert invalid_webhook.status_code == 401
    assert invalid_webhook.json()["detail"] == "Assinatura de webhook invalida."
    assert valid_webhook.status_code == 200
    assert valid_webhook.json() == {"status": "valid", "algorithm": "hmac-sha256"}


def test_gateway_rate_limit_blocks_repeated_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeRedisPipeline:
        def __init__(self, state: dict[str, int]) -> None:
            self._state = state
            self._key: str | None = None
            self._window: int | None = None

        def incr(self, key: str) -> "FakeRedisPipeline":
            self._key = key
            return self

        def expire(self, key: str, window: int) -> "FakeRedisPipeline":
            self._key = key
            self._window = window
            return self

        async def execute(self) -> None:
            assert self._key is not None
            self._state[self._key] = self._state.get(self._key, 0) + 1

    class FakeRedis:
        def __init__(self) -> None:
            self._state: dict[str, int] = {"rate_limit:testclient": 99}

        async def get(self, key: str) -> int | None:
            return self._state.get(key)

        def pipeline(self) -> FakeRedisPipeline:
            return FakeRedisPipeline(self._state)

    monkeypatch.setattr(api_hub, "redis_client", FakeRedis())

    with TestClient(api_hub.app) as client:
        first = client.get("/gateway/api-key/check", headers={"X-API-Key": "local-api-key"})
        second = client.get("/gateway/api-key/check", headers={"X-API-Key": "local-api-key"})

    assert first.status_code == 200
    assert first.json()["status"] == "valid"
    assert second.status_code == 429
    assert second.json()["detail"] == "Too many requests. Tente novamente em um minuto."


def test_security_workflow_runs_mandatory_scans() -> None:
    workflow = (ROOT / ".github" / "workflows" / "security.yml").read_text(encoding="utf-8")

    assert "matrix:" in workflow
    assert "pip-audit --local" in workflow
    assert "bandit -r modules/shared scripts workers -q -ll" in workflow
    assert "python -m pytest -q tests/test_security_gates.py" in workflow
    assert "modules/api_hub/Dockerfile" in workflow
    assert "modules/identity/Dockerfile" in workflow
    assert "modules/jobs/Dockerfile" in workflow
    assert "all-in-one-api-hub:security" in workflow
    assert "all-in-one-identity:security" in workflow
    assert "all-in-one-jobs:security" in workflow
    assert "aquasecurity/trivy-action" in workflow
    assert "severity: HIGH,CRITICAL" in workflow
    assert "ignore-unfixed: true" in workflow
