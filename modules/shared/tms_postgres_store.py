from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class TmsPostgresStore(BasePostgresStore):
    """Production Tms adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "tms"
    backend = "postgres_tms_typed_store"
    tables = {
        "carriers": "tms.carriers",
        "freights": "tms.freights",
        "routes": "tms.routes",
        "proofs_of_delivery": "tms.proofs_of_delivery",
        "freight_audits": "tms.freight_audits",
    }
    soft_deletable = frozenset(
        ["carriers", "freights", "routes", "proofs_of_delivery", "freight_audits"]
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
