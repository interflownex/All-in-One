from __future__ import annotations

import json
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any, Literal
from uuid import uuid4

from psycopg import Connection
from psycopg.types.json import Jsonb

from .correlation import get_correlation_id

AUDIT_SCHEMA_VERSION = 1
DEFAULT_RETENTION_DAYS = 2555
_SECRET_FRAGMENTS = (
    "password",
    "senha",
    "secret",
    "token",
    "authorization",
    "cookie",
    "private_key",
)
_audit_context: ContextVar[AuditContext | None] = ContextVar(
    "all_in_one_audit_context", default=None
)


@dataclass(frozen=True, slots=True)
class AuditContext:
    tenant_id: str | None = None
    company_id: str | None = None
    actor_role: str | None = None
    session_id: str | None = None
    device_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    origin: str = "backend"
    channel: str = "api"
    reason: str | None = None
    causation_id: str | None = None
    authorization: str | None = None
    approval_id: str | None = None
    approved_by: str | None = None


def set_audit_context(context: AuditContext) -> AuditContext:
    _audit_context.set(context)
    return context


def get_audit_context() -> AuditContext:
    return _audit_context.get() or AuditContext()


def sanitize_audit_value(value: Any) -> Any:
    """Minimiza segredos antes da persistência sem alterar o objeto de origem."""
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]"
            if any(fragment in str(key).casefold() for fragment in _SECRET_FRAGMENTS)
            else sanitize_audit_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_audit_value(item) for item in value]
    if isinstance(value, (datetime,)):
        return value.astimezone(UTC).isoformat()
    return value


def _changed_fields(before: Any, after: Any) -> list[str]:
    if not isinstance(before, dict) or not isinstance(after, dict):
        return []
    return sorted(
        key for key in set(before) | set(after) if before.get(key) != after.get(key)
    )


def _integrity_hash(record: dict[str, Any], previous_hash: str | None) -> str:
    material = {**record, "previous_hash": previous_hash}
    encoded = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return sha256(encoded.encode("utf-8")).hexdigest()


def build_audit_record(
    *,
    module: str,
    actor_user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    before: Any = None,
    after: Any = None,
    user_id: str | None = None,
    context: AuditContext | None = None,
    result: str = "success",
    error: str | None = None,
    log_type: Literal["audit", "security", "business", "technical"] = "audit",
    previous_hash: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    ctx = context or get_audit_context()
    timestamp = occurred_at or datetime.now(UTC).isoformat()
    retention_until = (
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        + timedelta(days=DEFAULT_RETENTION_DAYS)
    ).isoformat()
    safe_before = sanitize_audit_value(before)
    safe_after = sanitize_audit_value(after)
    record: dict[str, Any] = {
        "id": str(uuid4()),
        "schema_version": AUDIT_SCHEMA_VERSION,
        "event": f"{module}.{action}",
        "module": module,
        "log_type": log_type,
        "actor_user_id": actor_user_id,
        "user_id": user_id,
        "tenant_id": ctx.tenant_id,
        "company_id": ctx.company_id,
        "actor_role": ctx.actor_role,
        "session_id": ctx.session_id,
        "device_id": ctx.device_id,
        "ip_address": ctx.ip_address,
        "user_agent": ctx.user_agent,
        "origin": ctx.origin,
        "channel": ctx.channel,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "before_data": safe_before,
        "after_data": safe_after,
        "changed_fields": _changed_fields(safe_before, safe_after),
        "reason": ctx.reason,
        "correlation_id": get_correlation_id(),
        "causation_id": ctx.causation_id,
        "occurred_at": timestamp,
        "result": result,
        "error_detail": error,
        "authorization": ctx.authorization,
        "approval_id": ctx.approval_id,
        "approved_by": ctx.approved_by,
        "exported": bool(safe_after.get("exported", False))
        if isinstance(safe_after, dict)
        else False,
        "printed": bool(safe_after.get("printed", False))
        if isinstance(safe_after, dict)
        else False,
        "shared": bool(safe_after.get("shared", False))
        if isinstance(safe_after, dict)
        else False,
        "retention_until": retention_until,
        "previous_hash": previous_hash,
        "metadata": {"context": asdict(ctx), "sensitive_values": "minimized"},
    }
    record["row_hash"] = _integrity_hash(record, previous_hash)
    return record


def verify_audit_record(record: dict[str, Any]) -> bool:
    material = {key: value for key, value in record.items() if key != "row_hash"}
    return record.get("row_hash") == _integrity_hash(
        material, record.get("previous_hash")
    )


def build_read_audit_record(
    *,
    module: str,
    actor_user_id: str,
    resource_type: str,
    resource_id: str,
    purpose: str,
    context: AuditContext,
    result: str = "success",
    exported: bool = False,
    printed: bool = False,
    shared: bool = False,
) -> dict[str, Any]:
    return build_audit_record(
        module=module,
        actor_user_id=actor_user_id,
        action="sensitive_read",
        resource_type=resource_type,
        resource_id=resource_id,
        after={
            "purpose": purpose,
            "exported": exported,
            "printed": printed,
            "shared": shared,
        },
        context=context,
        result=result,
        log_type="security",
    )


def insert_postgres_audit(
    connection: Connection,
    *,
    module: str,
    actor_user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    before: Any,
    after: Any,
    user_id: str | None,
    company_id: str | None,
) -> dict[str, Any]:
    """Writer único para stores PostgreSQL; requer a migration 029 aplicada."""
    del company_id  # entity_id legado pode representar loja/armazém; empresa vem do contexto autenticado.
    previous = connection.execute(
        "SELECT row_hash FROM audit.logs WHERE module = %s ORDER BY occurred_at DESC LIMIT 1 FOR SHARE",
        (module,),
    ).fetchone()
    base_context = get_audit_context()
    context = base_context
    record = build_audit_record(
        module=module,
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        before=before,
        after=after,
        user_id=user_id,
        context=context,
        previous_hash=previous["row_hash"] if previous else None,
    )
    evidence = connection.execute(
        """INSERT INTO audit.logs
           (id, schema_version, event, log_type, user_id, actor_user_id, actor_entity_id, tenant_id,
            company_id, actor_role, session_id, device_id, ip_address, user_agent, action, module,
            resource_type, resource_id, before_data, after_data, changed_fields, reason, origin, channel,
            correlation_id, causation_id, occurred_at, result, error_detail, authorization, approval_id,
            approved_by, exported, printed, shared, previous_hash, row_hash, retention_until, metadata, created_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                   %s, %s, %s, %s) RETURNING *""",
        (
            record["id"],
            record["schema_version"],
            record["event"],
            record["log_type"],
            user_id,
            actor_user_id,
            record["company_id"],
            record["tenant_id"],
            record["company_id"],
            record["actor_role"],
            record["session_id"],
            record["device_id"],
            record["ip_address"],
            record["user_agent"],
            action,
            module,
            resource_type,
            resource_id,
            Jsonb(record["before_data"]) if record["before_data"] is not None else None,
            Jsonb(record["after_data"]) if record["after_data"] is not None else None,
            Jsonb(record["changed_fields"]),
            record["reason"],
            record["origin"],
            record["channel"],
            record["correlation_id"],
            record["causation_id"],
            record["occurred_at"],
            record["result"],
            record["error_detail"],
            record["authorization"],
            record["approval_id"],
            record["approved_by"],
            record["exported"],
            record["printed"],
            record["shared"],
            record["previous_hash"],
            record["row_hash"],
            record["retention_until"],
            Jsonb(record["metadata"]),
            actor_user_id,
        ),
    ).fetchone()
    return dict(evidence)
