import logging
import json
import re
from typing import Any

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
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)

def get_logger(name: str):
    return logging.getLogger(name)
