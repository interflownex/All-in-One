from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class AiCorePostgresStore(BasePostgresStore):
    """Production Ai_Core adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "ai_core"
    backend = "postgres_ai_core_typed_store"
    tables = {
        "ai_memories": "ai_core.ai_memories",
        "moderation_decisions": "ai_core.moderation_decisions",
        "model_runs": "ai_core.model_runs",
    }
    soft_deletable = frozenset(["ai_memories", "moderation_decisions", "model_runs"])

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
