from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class StockPostgresStore(BasePostgresStore):
    """Production Stock adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "stock"
    backend = "postgres_stock_typed_store"
    tables = {
        "suppliers": "stock.suppliers",
        "catalog_products": "stock.catalog_products",
        "price_rules": "stock.price_rules",
        "supplier_orders": "stock.supplier_orders",
        "discount_quotes": "stock.discount_quotes",
    }
    soft_deletable = frozenset(
        ["suppliers", "catalog_products", "price_rules", "supplier_orders"]
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
