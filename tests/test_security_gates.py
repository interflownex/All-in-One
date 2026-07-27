from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.api_hub import main as api_hub
from modules.shared import auth as shared_auth


def test_api_key_header_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_hub, "EXPECTED_API_KEY", "local-api-key")
    with TestClient(api_hub.app) as client:
        response = client.get("/gateway/api-key/check")
    assert response.status_code == 401


def test_invalid_api_key_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_hub, "EXPECTED_API_KEY", "local-api-key")
    with TestClient(api_hub.app) as client:
        response = client.get(
            "/gateway/api-key/check", headers={"X-API-Key": "invalid"}
        )
    assert response.status_code == 403


def test_valid_api_key_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_hub, "EXPECTED_API_KEY", "local-api-key")
    with TestClient(api_hub.app) as client:
        response = client.get(
            "/gateway/api-key/check", headers={"X-API-Key": "local-api-key"}
        )
    assert response.status_code == 200
    assert response.json()["status"] == "valid"


def test_hash_secret_uses_argon2() -> None:
    encoded = shared_auth.hash_secret("correct-horse-battery-staple")
    assert encoded.startswith("$argon2")
    assert shared_auth.verify_secret("correct-horse-battery-staple", encoded)
    assert not shared_auth.verify_secret("wrong", encoded)


def test_authorization_header_parser_rejects_malformed_values() -> None:
    assert shared_auth.parse_bearer_token(None) is None
    assert shared_auth.parse_bearer_token("") is None
    assert shared_auth.parse_bearer_token("Bearer") is None
    assert shared_auth.parse_bearer_token("Basic value") is None
    assert shared_auth.parse_bearer_token("Bearer token extra") is None
    assert shared_auth.parse_bearer_token("Bearer valid-token") == "valid-token"


def test_expired_session_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shared_auth, "SESSION_SECRET", "test-session-secret")
    token = shared_auth.encode_session_token(
        subject="test-user",
        tenant_id="test-tenant",
        roles=["user"],
        permissions=["profile:read"],
        ttl_seconds=-1,
    )
    with pytest.raises(shared_auth.InvalidSessionToken):
        shared_auth.decode_session_token(token)


def test_csrf_token_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shared_auth, "CSRF_SECRET", "test-csrf-secret")
    token = shared_auth.issue_csrf_token("session-123")
    assert shared_auth.verify_csrf_token("session-123", token)
    assert not shared_auth.verify_csrf_token("different-session", token)


def test_rate_limit_rejects_after_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_hub, "EXPECTED_API_KEY", "local-api-key")
    monkeypatch.setattr(api_hub, "RATE_LIMIT_PER_MINUTE", 1)

    class FakeRedisPipeline:
        def __init__(self, state: dict[str, int]) -> None:
            self._state = state
            self._key: str | None = None

        def incr(self, key: str) -> FakeRedisPipeline:
            self._key = key
            return self

        def expire(self, key: str, seconds: int) -> FakeRedisPipeline:
            return self

        async def execute(self) -> list[int]:
            assert self._key is not None
            self._state[self._key] = self._state.get(self._key, 0) + 1
            return [self._state[self._key], True]

    class FakeRedis:
        def __init__(self) -> None:
            self._state: dict[str, int] = {}

        async def get(self, key: str) -> int | None:
            return self._state.get(key)

        def pipeline(self) -> FakeRedisPipeline:
            return FakeRedisPipeline(self._state)

    monkeypatch.setattr(api_hub, "redis_client", FakeRedis())

    with TestClient(api_hub.app) as client:
        first = client.get(
            "/gateway/api-key/check", headers={"X-API-Key": "local-api-key"}
        )
        second = client.get(
            "/gateway/api-key/check", headers={"X-API-Key": "local-api-key"}
        )

    assert first.status_code == 200
    assert first.json()["status"] == "valid"
    assert second.status_code == 429
    assert second.json()["detail"] == "Too many requests. Tente novamente em um minuto."


def test_security_workflow_runs_mandatory_scans() -> None:
    workflow = (ROOT / ".github" / "workflows" / "security.yml").read_text(
        encoding="utf-8"
    )

    assert "matrix:" in workflow
    assert "pip-audit -r requirements-dev.txt" in workflow
    assert "pip-audit --local" not in workflow
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
