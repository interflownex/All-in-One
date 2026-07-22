"""Assinatura Ed25519 de respostas críticas sem compartilhar segredo com clientes."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from functools import lru_cache
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import HTTPException
from fastapi.responses import JSONResponse

PRIVATE_KEY_ENV = "VALLEY_RESPONSE_SIGNING_PRIVATE_KEY_B64"
PRODUCTION_ENVIRONMENTS = {"production", "prod"}


@lru_cache(maxsize=1)
def _private_key() -> Ed25519PrivateKey:
    encoded = os.getenv(PRIVATE_KEY_ENV, "").strip()
    if encoded:
        try:
            raw = base64.b64decode(encoded, validate=True)
            if len(raw) != 32:
                raise ValueError("tamanho invalido")
            return Ed25519PrivateKey.from_private_bytes(raw)
        except (ValueError, TypeError) as exc:
            raise RuntimeError(f"{PRIVATE_KEY_ENV} invalida") from exc
    environment = os.getenv("ALL_IN_ONE_ENVIRONMENT", "development").strip().lower()
    if environment in PRODUCTION_ENVIRONMENTS:
        raise RuntimeError(f"{PRIVATE_KEY_ENV} obrigatoria em producao")
    return Ed25519PrivateKey.generate()


def public_key_contract() -> dict[str, str]:
    public_raw = (
        _private_key()
        .public_key()
        .public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    return {
        "algorithm": "Ed25519",
        "key_id": hashlib.sha256(public_raw).hexdigest()[:16],
        "public_key_b64": base64.b64encode(public_raw).decode("ascii"),
    }


def canonical_response(payload: Any, timestamp: str) -> bytes:
    body = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()
    return f"{timestamp}\n{digest}".encode("ascii")


def signed_json_response(payload: Any, *, status_code: int = 200) -> JSONResponse:
    try:
        contract = public_key_contract()
        timestamp = str(int(time.time()))
        signature = _private_key().sign(canonical_response(payload, timestamp))
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503, detail="Assinatura de resposta crítica indisponível."
        ) from exc
    return JSONResponse(
        status_code=status_code,
        content=payload,
        headers={
            "X-Valley-Signature-Algorithm": contract["algorithm"],
            "X-Valley-Signature-Key-Id": contract["key_id"],
            "X-Valley-Signature-Timestamp": timestamp,
            "X-Valley-Response-Signature": base64.b64encode(signature).decode("ascii"),
        },
    )
