import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

from .correlation import get_correlation_id

# Padrões para higienização de dados sensíveis (PII)
PII_PATTERNS = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "cnpj": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
    "jwt": r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
}

SENSITIVE_KEYS = {
    "access_token",
    "authorization",
    "cookie",
    "password",
    "refresh_token",
    "secret",
    "set_cookie",
    "token",
}


def _sanitize_value(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in SENSITIVE_KEYS:
        return "[REDACTED]"
    if isinstance(value, dict):
        return {
            str(item_key): _sanitize_value(item, str(item_key))
            for item_key, item in value.items()
        }
    if isinstance(value, tuple):
        return tuple(_sanitize_value(item) for item in value)
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, str):
        for name, pattern in PII_PATTERNS.items():
            value = re.sub(pattern, f"[{name.upper()}_REDACTED]", value)
    return value


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _sanitize_value(record.msg)
        if record.args:
            record.args = _sanitize_value(record.args)
        record.correlation_id = (
            getattr(record, "correlation_id", None) or get_correlation_id()
        )
        return True

    def sanitize(self, text: str) -> str:
        sanitized = text
        for name, pattern in PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[{name.upper()}_REDACTED]", sanitized)
        return sanitized

    def sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        return _sanitize_value(data)


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", None)
            or get_correlation_id(),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(_sanitize_value(payload), ensure_ascii=False, default=str)


def setup_secure_logging(level: int = logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    # Evitar duplicidade de handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = StructuredJsonFormatter()
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)


def get_logger(name: str):
    return logging.getLogger(name)
