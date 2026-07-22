from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class PermissionsPostgresStore(BasePostgresStore):
    """Production Permissions adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "permissions"
    backend = "postgres_permissions_typed_store"
    tables = {
        "roles": "permissions.roles",
        "permissions": "permissions.permissions",
        "user_roles": "permissions.user_roles",
        "access_policies": "permissions.access_policies",
        "approval_limits": "permissions.approval_limits",
    }
    soft_deletable = frozenset(
        ["roles", "permissions", "user_roles", "access_policies", "approval_limits"]
    )

    def _insert(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        user_id: str,
        entity_id: str | None,
        status: str,
        payload: dict[str, Any],
        actor: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        return self._insert_generic(
            connection,
            resource_type,
            resource_id,
            user_id,
            entity_id,
            status,
            payload,
            actor,
            idempotency_key,
        )

    def _update(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        payload: dict[str, Any],
        status: str,
        actor: str,
    ) -> dict[str, Any]:
        return self._update_generic(
            connection, resource_type, resource_id, payload, status, actor
        )
