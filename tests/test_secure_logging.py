from __future__ import annotations

import json
import logging

from modules.shared.correlation import set_correlation_id
from modules.shared.logging_utils import SensitiveDataFilter, StructuredJsonFormatter


def _render(message: object, *args: object) -> dict[str, object]:
    record = logging.LogRecord("valley", logging.INFO, __file__, 1, message, args, None)
    assert SensitiveDataFilter().filter(record)
    return json.loads(StructuredJsonFormatter().format(record))


def test_structured_log_always_contains_correlation_and_core_fields() -> None:
    set_correlation_id("5de05e35-1f5d-4f64-acb3-ab0743ddab5e")
    payload = _render("request completed")

    assert payload["correlation_id"] == "5de05e35-1f5d-4f64-acb3-ab0743ddab5e"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "valley"
    assert payload["message"] == "request completed"
    assert str(payload["timestamp"]).endswith("+00:00")


def test_structured_log_redacts_pii_and_secret_keys() -> None:
    payload = _render(
        {"email": "ana@example.com", "access_token": "secret-value", "status": "ok"}
    )
    serialized = json.dumps(payload)

    assert "ana@example.com" not in serialized
    assert "secret-value" not in serialized
    assert "[EMAIL_REDACTED]" in serialized
    assert "[REDACTED]" in serialized
