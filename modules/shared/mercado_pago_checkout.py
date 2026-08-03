from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class MercadoPagoConfigurationError(RuntimeError):
    """Configuração ausente ou inválida para o Checkout Pro."""


class MercadoPagoAPIError(RuntimeError):
    """Resposta não bem-sucedida da API do Mercado Pago."""


@dataclass(frozen=True)
class MercadoPagoSettings:
    access_token: str
    webhook_secret: str
    notification_url: str
    api_base_url: str = "https://api.mercadopago.com"
    timeout_seconds: float = 10.0

    @classmethod
    def from_environment(cls) -> MercadoPagoSettings:
        access_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "").strip()
        webhook_secret = os.getenv("MERCADO_PAGO_WEBHOOK_SECRET", "").strip()
        notification_url = os.getenv("MERCADO_PAGO_NOTIFICATION_URL", "").strip()
        if not access_token:
            raise MercadoPagoConfigurationError(
                "MERCADO_PAGO_ACCESS_TOKEN não configurado."
            )
        if not webhook_secret:
            raise MercadoPagoConfigurationError(
                "MERCADO_PAGO_WEBHOOK_SECRET não configurado."
            )
        if not notification_url.startswith("https://"):
            raise MercadoPagoConfigurationError(
                "MERCADO_PAGO_NOTIFICATION_URL deve usar HTTPS."
            )
        return cls(
            access_token=access_token,
            webhook_secret=webhook_secret,
            notification_url=notification_url,
            api_base_url=os.getenv(
                "MERCADO_PAGO_API_BASE_URL", "https://api.mercadopago.com"
            ).rstrip("/"),
        )


class MercadoPagoClient:
    def __init__(self, settings: MercadoPagoSettings) -> None:
        parsed_api_url = urlsplit(settings.api_base_url)
        try:
            api_port = parsed_api_url.port
        except ValueError as exc:
            raise MercadoPagoConfigurationError(
                "MERCADO_PAGO_API_BASE_URL inválida."
            ) from exc
        if (
            parsed_api_url.scheme != "https"
            or parsed_api_url.hostname != "api.mercadopago.com"
            or api_port not in (None, 443)
            or parsed_api_url.username is not None
            or parsed_api_url.password is not None
            or parsed_api_url.path not in ("", "/")
            or parsed_api_url.query
            or parsed_api_url.fragment
        ):
            raise MercadoPagoConfigurationError(
                "MERCADO_PAGO_API_BASE_URL deve usar exclusivamente "
                "https://api.mercadopago.com sem credenciais, parâmetros ou fragmentos."
            )
        self.settings = settings

    def create_preference(
        self,
        *,
        checkout_id: str,
        order_id: str,
        total_brl: Decimal,
        title: str,
        payer_email: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "items": [
                {
                    "id": order_id,
                    "title": title[:256],
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(total_brl),
                }
            ],
            "external_reference": checkout_id,
            "notification_url": self.settings.notification_url,
            "auto_return": "approved",
        }
        if payer_email:
            body["payer"] = {"email": payer_email}
        return self._request("POST", "/checkout/preferences", body)

    def get_payment(self, payment_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/payments/{payment_id}")

    def _request(
        self, method: str, path: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        encoded = json.dumps(body).encode() if body is not None else None
        headers = {
            "Authorization": f"Bearer {self.settings.access_token}",
            "Content-Type": "application/json",
        }
        if body and body.get("external_reference"):
            headers["X-Idempotency-Key"] = str(body["external_reference"])
        request = Request(
            f"{self.settings.api_base_url}{path}",
            data=encoded,
            method=method,
            headers=headers,
        )
        try:
            # A URL é validada no construtor; B310 não modela esse limite.
            with urlopen(  # nosec B310
                request, timeout=self.settings.timeout_seconds
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, ValueError) as exc:
            raise MercadoPagoAPIError(
                "Mercado Pago não respondeu com sucesso."
            ) from exc
        if not isinstance(payload, dict):
            raise MercadoPagoAPIError("Resposta inválida do Mercado Pago.")
        return payload


def verify_webhook_signature(
    *,
    x_signature: str | None,
    x_request_id: str | None,
    data_id: str | None,
    secret: str,
    now: int | None = None,
    max_age_seconds: int = 300,
) -> bool:
    """Valida ts=...,v1=... conforme a assinatura HMAC do Mercado Pago."""
    if not x_signature or not x_request_id or not data_id or not secret:
        return False
    parts = {
        item.split("=", 1)[0]: item.split("=", 1)[1]
        for item in x_signature.split(",")
        if "=" in item
    }
    timestamp, signature = parts.get("ts"), parts.get("v1")
    if not timestamp or not signature:
        return False
    try:
        timestamp_int = int(timestamp)
    except ValueError:
        return False
    current = int(time.time()) if now is None else now
    if abs(current - timestamp_int) > max_age_seconds:
        return False
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{timestamp};"
    expected = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
