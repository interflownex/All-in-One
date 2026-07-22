from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4


EVENT_SCHEMA_VERSION = 1
REDACTED_VALUE = "[REDACTED]"
PROHIBITED_FIELD_MARKERS = (
    "authorization",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_cookie",
)
PROHIBITED_TOKEN_FIELDS = frozenset(
    {
        "access_token",
        "api_key",
        "bearer_token",
        "refresh_token",
        "session_token",
        "token",
    }
)


def _is_prohibited_field(field: str) -> bool:
    normalized = field.casefold().replace("-", "_")
    return normalized in PROHIBITED_TOKEN_FIELDS or any(marker in normalized for marker in PROHIBITED_FIELD_MARKERS)


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat() if value.tzinfo else value.replace(tzinfo=UTC).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    return value


def sanitize_event_payload(value: Any, path: str = "payload") -> tuple[Any, list[str]]:
    """Remove credenciais recursivamente antes de o evento chegar ao outbox."""
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        redacted: list[str] = []
        for raw_key, raw_value in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}"
            if _is_prohibited_field(key):
                sanitized[key] = REDACTED_VALUE
                redacted.append(child_path)
                continue
            child, child_redacted = sanitize_event_payload(raw_value, child_path)
            sanitized[key] = child
            redacted.extend(child_redacted)
        return sanitized, redacted
    if isinstance(value, (list, tuple, set, frozenset)):
        sanitized_items: list[Any] = []
        redacted: list[str] = []
        for index, item in enumerate(value):
            child, child_redacted = sanitize_event_payload(item, f"{path}[{index}]")
            sanitized_items.append(child)
            redacted.extend(child_redacted)
        return sanitized_items, redacted
    return _json_value(value), []


def build_event_envelope(
    *,
    module: str,
    routing_key: str,
    actor_user_id: str,
    item: dict[str, Any],
    correlation_id: str,
    causation_id: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    payload, redacted_fields = sanitize_event_payload(item.get("payload", {}))
    aggregate_id = str(item["id"])
    idempotency_key = item.get("idempotency_key") or f"{routing_key}:{aggregate_id}"
    entity_id = item.get("entity_id") or item.get("company_id")
    return {
        "event_id": str(uuid4()),
        "event_name": routing_key,
        "schema_version": EVENT_SCHEMA_VERSION,
        "producer": module,
        "aggregate_type": item["resource_type"],
        "aggregate_id": aggregate_id,
        "idempotency_key": str(idempotency_key),
        "correlation_id": str(correlation_id),
        "causation_id": str(causation_id) if causation_id else None,
        "occurred_at": occurred_at or datetime.now(UTC).isoformat(),
        "tenant_id": str(entity_id) if entity_id else None,
        "user_id": str(item["user_id"]) if item.get("user_id") else None,
        "actor_user_id": str(actor_user_id),
        "origin": "all-in-one",
        "payload": payload,
        "data_policy": {
            "prohibited": ["credenciais", "senhas", "segredos", "tokens de acesso", "chaves privadas"],
            "redacted_fields": redacted_fields,
        },
        "retention": {"policy": "audit_business_event", "days": 2555},
        "failure_handling": {"strategy": "outbox_retry_with_dead_letter", "delivery_evidence": True},
        "replay": {"supported": True, "deduplicate_by": "event_id", "preserve_order_by": "aggregate_id"},
        "backward_compatibility": {"policy": "additive", "breaking_change_requires_new_schema_version": True},
    }
