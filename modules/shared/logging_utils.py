import logging
import json
import re
from typing import Any

from .correlation import peek_correlation_id

# Padrões para higienização de dados sensíveis (PII)
PII_PATTERNS = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "cnpj": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
    "jwt": r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
}

class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.sanitize(record.msg)
        elif isinstance(record.msg, dict):
            record.msg = self.sanitize_dict(record.msg)
        return True

    def sanitize(self, text: str) -> str:
        sanitized = text
        for name, pattern in PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[{name.upper()}_REDACTED]", sanitized)
        return sanitized

    def sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        return json.loads(self.sanitize(json.dumps(data)))


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = peek_correlation_id() or "-"
        return True


def _attach_filter_once(handler: logging.Handler, filter_instance: logging.Filter) -> None:
    if not any(isinstance(existing, filter_instance.__class__) for existing in handler.filters):
        handler.addFilter(filter_instance)

def setup_secure_logging(level: int = logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Evitar duplicidade de handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [Correlation: %(correlation_id)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    for handler in logger.handlers:
        _attach_filter_once(handler, SensitiveDataFilter())
        _attach_filter_once(handler, CorrelationIdFilter())

def get_logger(name: str):
    return logging.getLogger(name)
