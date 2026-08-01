import hashlib
import hmac

import pytest

from modules.shared.mercado_pago_checkout import (
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


def test_webhook_signature_requires_fresh_hmac_manifest():
    secret = "test-secret"
    timestamp = "1700000000"
    request_id = "request-1"
    data_id = "payment-1"
    manifest = f"id:{data_id};request-id:{request_id};ts:{timestamp};"
    digest = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    signature = f"ts={timestamp},v1={digest}"
    assert verify_webhook_signature(
        x_signature=signature,
        x_request_id=request_id,
        data_id=data_id,
        secret=secret,
        now=1700000100,
    )
    assert not verify_webhook_signature(
        x_signature=signature,
        x_request_id=request_id,
        data_id=data_id,
        secret=secret,
        now=1700000401,
    )
