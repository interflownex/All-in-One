from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class WmsPostgresStore(BasePostgresStore):
    """Production Wms adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "wms"
    backend = "postgres_wms_typed_store"
    tables = {
        "warehouses": "wms.warehouses",
        "bins": "wms.bins",
        "inventory": "wms.inventory",
        "picking_waves": "wms.picking_waves",
        "shipments": "wms.shipments",
    }
    soft_deletable = frozenset(
        ["warehouses", "bins", "inventory", "picking_waves", "shipments"]
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
