import asyncio
import hashlib
import hmac
import sys
from types import SimpleNamespace

from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from platform_test_support import ROOT


def _load_api_hub(monkeypatch):
    import importlib.util

    monkeypatch.setenv("ALL_IN_ONE_API_KEYS", "test-key:test-client:gateway:read;denied-key:denied:jobs:read")
    monkeypatch.setenv("ALL_IN_ONE_WEBHOOK_SECRET", "test-secret")
    path = ROOT / "modules" / "api_hub" / "main.py"
    module_dir = str(path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = importlib.util.spec_from_file_location("all_in_one_api_hub_gateway_security", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_api_key_check_accepts_configured_key(monkeypatch):
    module = _load_api_hub(monkeypatch)

    async def noop_rate_limiter(request: Request):
        return None

    module.app.dependency_overrides[module.rate_limiter] = noop_rate_limiter
    client = TestClient(module.app)

    response = client.get("/gateway/api-key/check", headers={"X-API-Key": "test-key"})

    assert response.status_code == 200
    assert response.json()["client_id"] == "test-client"
    assert response.json()["scopes"] == ["gateway:read"]


def test_api_key_check_rejects_missing_invalid_and_unscoped_keys(monkeypatch):
    module = _load_api_hub(monkeypatch)

    async def noop_rate_limiter(request: Request):
        return None

    module.app.dependency_overrides[module.rate_limiter] = noop_rate_limiter
    client = TestClient(module.app)

    assert client.get("/gateway/api-key/check").status_code == 401
    assert client.get("/gateway/api-key/check", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/gateway/api-key/check", headers={"X-API-Key": "denied-key"}).status_code == 403


def test_webhook_signature_verification(monkeypatch):
    module = _load_api_hub(monkeypatch)
    client = TestClient(module.app)
    body = b'{"event":"api.webhook.delivered"}'
    digest = hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()

    accepted = client.post(
        "/gateway/webhooks/verify",
        content=body,
        headers={"X-All-In-One-Signature": f"sha256={digest}", "Content-Type": "application/json"},
    )
    rejected = client.post(
        "/gateway/webhooks/verify",
        content=body,
        headers={"X-All-In-One-Signature": "sha256=invalid", "Content-Type": "application/json"},
    )

    assert accepted.status_code == 200
    assert accepted.json()["algorithm"] == "hmac-sha256"
    assert rejected.status_code == 401


def test_rate_limiter_blocks_after_limit(monkeypatch):
    module = _load_api_hub(monkeypatch)

    class FakePipeline:
        def incr(self, key):
            return self

        def expire(self, key, window):
            return self

        async def execute(self):
            return [101, True]

    class FakeRedis:
        async def get(self, key):
            return "100"

        def pipeline(self):
            return FakePipeline()

    monkeypatch.setattr(module, "redis_client", FakeRedis())
    request = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"))

    try:
        asyncio.run(module.rate_limiter(request))
    except HTTPException as exc:
        assert exc.status_code == 429
    else:
        raise AssertionError("rate_limiter deveria bloquear quando limite estiver esgotado")


def test_health_module_proxy_paths_still_require_jwt(monkeypatch):
    module = _load_api_hub(monkeypatch)
    token = module.jwt.encode({"sub": "11111111-1111-4111-8111-111111111111"}, module.JWT_SECRET, algorithm="HS256")

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    public_health = Request({"type": "http", "method": "GET", "path": "/health", "headers": []}, receive)
    module_health = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/health/resources/patients",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
        },
        receive,
    )

    assert asyncio.run(module.validate_jwt_edge(public_health)) is None
    assert asyncio.run(module.validate_jwt_edge(module_health))["sub"] == "11111111-1111-4111-8111-111111111111"


def test_proxy_maps_jwt_claims_to_actor_headers(monkeypatch):
    module = _load_api_hub(monkeypatch)
    captured: dict[str, str] = {}

    class FakeResponse:
        status_code = 200
        headers: dict[str, str] = {}

        async def aiter_raw(self):
            yield b"{}"

        async def aclose(self):
            return None

    class FakeClient:
        def build_request(self, *, method, url, headers, content):
            captured.update(headers)
            return SimpleNamespace(method=method, url=url, headers=headers, content=content)

        async def send(self, req, stream):
            return FakeResponse()

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    request = Request({"type": "http", "method": "POST", "path": "/riders/resources/rider_profiles", "headers": []}, receive)
    monkeypatch.setattr(module, "client", FakeClient())

    asyncio.run(
        module.proxy_request(
            "http://riders:8000",
            request,
            {
                "sub": "11111111-1111-4111-8111-111111111111",
                "roles": ["compliance_officer", "auditor"],
                "scopes": ["riders:approve"],
                "mfa_verified": True,
            },
            "/resources/rider_profiles",
        )
    )

    assert captured["X-Actor-User-Id"] == "11111111-1111-4111-8111-111111111111"
    assert captured["X-Actor-Roles"] == "compliance_officer,auditor"
    assert captured["X-Actor-Scopes"] == "riders:approve"
    assert captured["X-MFA-Verified"] == "true"
