from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class RidersPostgresStore(BasePostgresStore):
    """Production Riders adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "riders"
    backend = "postgres_riders_typed_store"
    tables = {
        "rider_profiles": "delivery.rider_profiles",
        "rider_documents": "delivery.rider_documents",
        "vehicles": "delivery.vehicles",
        "rider_reviews": "delivery.rider_reviews",
    }
    soft_deletable = frozenset(
        ["rider_profiles", "rider_documents", "vehicles", "rider_reviews"]
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
