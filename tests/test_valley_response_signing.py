from __future__ import annotations

import base64
import hashlib
import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from modules.shared import response_signing
from modules.shared.response_signing import public_key_contract, signed_json_response


def test_signed_response_is_verifiable_with_published_public_key() -> None:
    payload = {"status": "paid", "order_id": "order-1", "amount": "99.90"}

    response = signed_json_response(payload)
    contract = public_key_contract()
    timestamp = response.headers["X-Valley-Signature-Timestamp"]
    body = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    canonical = f"{timestamp}\n{hashlib.sha256(body).hexdigest()}".encode("ascii")

    public_key = Ed25519PublicKey.from_public_bytes(
        base64.b64decode(contract["public_key_b64"])
    )
    public_key.verify(
        base64.b64decode(response.headers["X-Valley-Response-Signature"]), canonical
    )
    assert response.headers["X-Valley-Signature-Key-Id"] == contract["key_id"]


def test_production_refuses_to_start_signing_without_private_key(monkeypatch) -> None:
    monkeypatch.setenv("ALL_IN_ONE_ENVIRONMENT", "production")
    monkeypatch.delenv("VALLEY_RESPONSE_SIGNING_PRIVATE_KEY_B64", raising=False)
    response_signing._private_key.cache_clear()

    with pytest.raises(RuntimeError, match="obrigatoria em producao"):
        public_key_contract()

    response_signing._private_key.cache_clear()
