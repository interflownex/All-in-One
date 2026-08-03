import hashlib
import hmac

import pytest

from modules.shared.mercado_pago_checkout import (
    MercadoPagoClient,
    MercadoPagoConfigurationError,
    MercadoPagoSettings,
    verify_webhook_signature,
)


def test_settings_reject_missing_access_token(monkeypatch):
    monkeypatch.delenv("MERCADO_PAGO_ACCESS_TOKEN", raising=False)
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "secret")
    monkeypatch.setenv("MERCADO_PAGO_NOTIFICATION_URL", "https://example.test/webhooks")
    with pytest.raises(MercadoPagoConfigurationError) as error:
        MercadoPagoSettings.from_environment()
    assert "ACCESS_TOKEN" in str(error.value)


@pytest.mark.parametrize(
    "api_base_url",
    (
        "http://api.mercadopago.com",
        "file:///tmp/mercado-pago.json",
        "https://token@example.test",
        "https://example.test",
        "https://api.mercadopago.com.example.test",
        "https://api.mercadopago.com:8443",
        "https://api.mercadopago.com/v1",
        "https://api.mercadopago.com?redirect=example.test",
        "https://api.mercadopago.com#fragment",
        "https://api.mercadopago.com:invalid",
    ),
)
def test_client_rejects_unsafe_api_base_url(api_base_url):
    settings = MercadoPagoSettings(
        access_token="test-token",
        webhook_secret="test-secret",
        notification_url="https://example.test/webhooks",
        api_base_url=api_base_url,
    )

    with pytest.raises(MercadoPagoConfigurationError) as error:
        MercadoPagoClient(settings)

    assert "MERCADO_PAGO_API_BASE_URL" in str(error.value)


def test_client_accepts_https_api_base_url():
    settings = MercadoPagoSettings(
        access_token="test-token",
        webhook_secret="test-secret",
        notification_url="https://example.test/webhooks",
        api_base_url="https://api.mercadopago.com",
    )

    assert MercadoPagoClient(settings).settings is settings


def _signed_webhook(
    *, timestamp: str, request_id: str, data_id: str, secret: str
) -> str:
    manifest = f"id:{data_id};request-id:{request_id};ts:{timestamp};"
    digest = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return f"ts={timestamp},v1={digest}"


@pytest.mark.parametrize(
    ("timestamp", "now"),
    (
        ("1700000000", 1700000100),
        ("1700000000000", 1700000100),
    ),
)
def test_webhook_signature_accepts_fresh_seconds_and_milliseconds(timestamp, now):
    secret = "test-secret"
    request_id = "request-1"
    data_id = "payment-1"
    signature = _signed_webhook(
        timestamp=timestamp,
        request_id=request_id,
        data_id=data_id,
        secret=secret,
    )

    assert verify_webhook_signature(
        x_signature=signature,
        x_request_id=request_id,
        data_id=data_id,
        secret=secret,
        now=now,
    )


@pytest.mark.parametrize(
    ("timestamp", "now"),
    (
        ("1700000000", 1700000401),
        ("1700000000000", 1700000401),
    ),
)
def test_webhook_signature_rejects_expired_seconds_and_milliseconds(timestamp, now):
    secret = "test-secret"
    request_id = "request-1"
    data_id = "payment-1"
    signature = _signed_webhook(
        timestamp=timestamp,
        request_id=request_id,
        data_id=data_id,
        secret=secret,
    )

    assert not verify_webhook_signature(
        x_signature=signature,
        x_request_id=request_id,
        data_id=data_id,
        secret=secret,
        now=now,
    )


def test_webhook_signature_rejects_negative_or_malformed_timestamp():
    assert not verify_webhook_signature(
        x_signature="ts=-1,v1=invalid",
        x_request_id="request-1",
        data_id="payment-1",
        secret="test-secret",
        now=0,
    )
    assert not verify_webhook_signature(
        x_signature="ts=not-a-number,v1=invalid",
        x_request_id="request-1",
        data_id="payment-1",
        secret="test-secret",
        now=0,
    )
