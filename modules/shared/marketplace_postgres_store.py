from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator
from uuid import uuid4

import psycopg
from psycopg import Connection, sql
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .correlation import get_correlation_id
from .store import DuplicateValueError
from .generic_postgres_resource import insert_generic_resource, update_generic_resource


TABLES = {
    "stores": "marketplace.stores",
    "products": "marketplace.products",
    "orders": "marketplace.orders",
    "reviews": "marketplace.reviews",
    "disputes": "marketplace.disputes",
    "pepita_grants": "marketplace.pepita_grants",
    "carts": "marketplace.carts",
}
SOFT_DELETABLE = frozenset(TABLES)


class MarketplacePostgresStore:
    """Production Marketplace adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "marketplace"
    backend = "postgres_marketplace_typed_store"

    def __init__(self, dsn: str) -> None:
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)

    @staticmethod
    def _table(resource_type: str) -> sql.Identifier:
        schema_name, table_name = TABLES[resource_type].split(".", maxsplit=1)
        return sql.Identifier(schema_name, table_name)

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    @staticmethod
    def _payload(row: dict[str, Any]) -> dict[str, Any]:
        return dict((row.get("metadata") or {}).get("runtime_payload", {}))

    def _resource(self, resource_type: str, row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        created_at = row.get("created_at")
        if created_at is None:
            raise RuntimeError(f"PostgreSQL nao retornou timestamp para {resource_type}.")
        return {
            "id": str(row["id"]),
            "module": self.module,
            "resource_type": resource_type,
            "user_id": str(row["user_id"]),
            "entity_id": str(row.get("store_id") or row.get("company_id")) if row.get("store_id") or row.get("company_id") else None,
            "status": row["status"],
            "payload": self._payload(row),
            "created_by": str(row["created_by"]) if row.get("created_by") else str(row["user_id"]),
            "updated_by": str(row.get("updated_by") or row.get("created_by") or row["user_id"]),
            "created_at": created_at.isoformat(),
            "updated_at": (row.get("updated_at") or created_at).isoformat(),
            "deleted_at": row.get("deleted_at").isoformat() if row.get("deleted_at") else None,
            "idempotency_key": row.get("idempotency_key"),
        }

    @staticmethod
    def _metadata(payload: dict[str, Any]) -> Jsonb:
        return Jsonb({"runtime_payload": payload})

    def find_idempotent(self, resource_type: str, key: str | None) -> dict[str, Any] | None:
        if not key:
            return None
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE idempotency_key = %s").format(self._table(resource_type)),
            (key,),
        ).fetchone()
        return self._resource(resource_type, row)

    def create(
        self,
        resource_type: str,
        user_id: str,
        entity_id: str | None,
        status: str,
        payload: dict[str, Any],
        actor: str,
        unique_fields: tuple[str, ...],
        event: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        del unique_fields
        previous = self.find_idempotent(resource_type, idempotency_key)
        if previous:
            return previous
        resource_id = str(uuid4())
        try:
            with self.transaction() as connection:
                row = self._insert(connection, resource_type, resource_id, user_id, entity_id, status, payload, actor, idempotency_key)
                item = self._resource(resource_type, row)
                if item is None:
                    raise RuntimeError("PostgreSQL nao retornou recurso Marketplace criado.")
                self._audit(connection, actor, "create", resource_type, resource_id, None, item, user_id, entity_id)
                self._event(connection, event, actor, item)
                return item
        except UniqueViolation as exc:
            raise DuplicateValueError(resource_type) from exc

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
        metadata = self._metadata(payload)
        if resource_type == "stores":
            return connection.execute(
                """INSERT INTO marketplace.stores
                   (id, user_id, company_id, name, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (resource_id, user_id, payload["company_id"], payload["name"], status, metadata, actor, actor, idempotency_key),
            ).fetchone()
        if resource_type == "products":
            return connection.execute(
                """INSERT INTO marketplace.products
                   (id, user_id, store_id, sku, name, price_brl, stock_quantity, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["store_id"], payload["sku"], payload["name"],
                    payload["price_brl"], payload.get("stock_quantity", 0), status, metadata, actor, actor, idempotency_key,
                ),
            ).fetchone()
        if resource_type == "orders":
            return connection.execute(
                """INSERT INTO marketplace.orders
                   (id, user_id, store_id, escrow_id, total_brl, commission_brl, status, metadata, created_by, updated_by, idempotency_key, offer_id, company_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload.get("store_id"), payload.get("escrow_id"), payload.get("total_brl", 0),
                    payload.get("commission_brl", 0), status, metadata, actor, actor, idempotency_key,
                    payload.get("offer_id"), payload.get("company_id")
                ),
            ).fetchone()
        if resource_type == "reviews":
            return connection.execute(
                """INSERT INTO marketplace.reviews
                   (id, user_id, order_id, store_id, offer_id, rating, comment, moderation_status,
                    status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["order_id"],
                    payload.get("store_id"),
                    payload.get("offer_id"),
                    payload["rating"],
                    payload.get("comment"),
                    payload.get("moderation_status", "published"),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "disputes":
            return connection.execute(
                """INSERT INTO marketplace.disputes
                   (id, user_id, order_id, store_id, company_id, offer_id, case_type, subject, message,
                    desired_resolution, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["order_id"],
                    payload.get("store_id"),
                    payload.get("company_id"),
                    payload.get("offer_id"),
                    payload["case_type"],
                    payload.get("subject"),
                    payload["message"],
                    payload.get("desired_resolution"),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "pepita_grants":
            return connection.execute(
                """INSERT INTO marketplace.pepita_grants
                   (id, user_id, company_id, order_id, customer_user_id, pepitas, merchant_gold_ledger_id, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, entity_id, payload["order_id"], payload["customer_user_id"],
                    payload["pepitas"], payload["merchant_gold_ledger_id"], status, metadata, actor, actor, idempotency_key,
                ),
            ).fetchone()
        return insert_generic_resource(
            connection, TABLES[resource_type], resource_id, user_id, entity_id, status, payload, actor, idempotency_key
        )

    def get(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        deleted = sql.SQL(" AND deleted_at IS NULL") if resource_type in SOFT_DELETABLE else sql.SQL("")
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE id = %s{}").format(self._table(resource_type), deleted),
            (resource_id,),
        ).fetchone()
        return self._resource(resource_type, row)

    def list(self, resource_type: str, user_id: str | None = None) -> list[dict[str, Any]]:
        conditions = sql.SQL("deleted_at IS NULL") if resource_type in SOFT_DELETABLE else sql.SQL("TRUE")
        parameters: list[Any] = []
        if user_id:
            conditions = conditions + sql.SQL(" AND user_id = %s")
            parameters.append(user_id)
        rows = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE {} ORDER BY created_at DESC").format(
                self._table(resource_type), conditions
            ),
            parameters,
        ).fetchall()
        return [item for row in rows if (item := self._resource(resource_type, row)) is not None]

    def update(
        self,
        item: dict[str, Any],
        payload: dict[str, Any],
        status: str,
        actor: str,
        action: str,
        event: str | None = None,
    ) -> dict[str, Any]:
        before = {**item, "payload": dict(item["payload"])}
        with self.transaction() as connection:
            row = self._update(connection, item["resource_type"], item["id"], payload, status, actor)
            updated = self._resource(item["resource_type"], row)
            if updated is None:
                raise RuntimeError("PostgreSQL nao retornou recurso Marketplace atualizado.")
            self._audit(connection, actor, action, item["resource_type"], item["id"], before, updated, item["user_id"], item["entity_id"])
            if event:
                self._event(connection, event, actor, updated)
            return updated

    def _update(
        self, connection: Connection, resource_type: str, resource_id: str, payload: dict[str, Any], status: str, actor: str
    ) -> dict[str, Any]:
        metadata = self._metadata(payload)
        if resource_type == "stores":
            return connection.execute(
                """UPDATE marketplace.stores SET name = %s, published_at = %s, status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload["name"], payload.get("published_at"), status, metadata, actor, resource_id),
            ).fetchone()
        if resource_type == "products":
            return connection.execute(
                """UPDATE marketplace.products SET name = %s, price_brl = %s, stock_quantity = %s, status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload["name"], payload["price_brl"], payload["stock_quantity"], status, metadata, actor, resource_id),
            ).fetchone()
        if resource_type == "orders":
            return connection.execute(
                """UPDATE marketplace.orders SET status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (status, metadata, actor, resource_id),
            ).fetchone()
        if resource_type == "reviews":
            return connection.execute(
                """UPDATE marketplace.reviews
                   SET moderation_status = %s, status = %s, metadata = %s,
                       updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (
                    payload.get("moderation_status", status),
                    status,
                    metadata,
                    actor,
                    resource_id,
                ),
            ).fetchone()
        if resource_type == "disputes":
            return connection.execute(
                """UPDATE marketplace.disputes SET status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (status, metadata, actor, resource_id),
            ).fetchone()
        return update_generic_resource(connection, TABLES[resource_type], resource_id, payload, status, actor)

    def soft_delete(self, item: dict[str, Any], actor: str) -> None:
        with self.transaction() as connection:
            connection.execute(
                sql.SQL(
                    "UPDATE {} SET deleted_at = NOW(), updated_by = %s, updated_at = NOW() WHERE id = %s"
                ).format(self._table(item["resource_type"])),
                (actor, item["id"]),
            )
            self._audit(connection, actor, "soft_delete", item["resource_type"], item["id"], item, None, item["user_id"], item["entity_id"])

    def audit_external(self, actor: str, action: str, resource_type: str, resource_id: str, data: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            return self._audit(connection, actor, action, resource_type, resource_id, None, data, data.get("user_id"), data.get("store_id"))

    def _audit(
        self,
        connection: Connection,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        before: Any,
        after: Any,
        user_id: str | None,
        entity_id: str | None,
    ) -> dict[str, Any]:
        evidence = connection.execute(
            """INSERT INTO audit.logs
               (user_id, actor_user_id, actor_entity_id, action, module, resource_type, resource_id,
                before_data, after_data, created_by)
               VALUES (%s, %s, %s, %s, 'marketplace', %s, %s, %s, %s, %s) RETURNING *""",
            (user_id, actor, entity_id, action, resource_type, resource_id, Jsonb(before) if before else None, Jsonb(after), actor),
        ).fetchone()
        return dict(evidence)

    def _event(self, connection: Connection, routing_key: str, actor: str, item: dict[str, Any]) -> None:
        connection.execute(
            """INSERT INTO audit.domain_events
               (user_id, actor_user_id, entity_id, routing_key, aggregate_type, aggregate_id, correlation_id, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                item["user_id"],
                actor,
                item["entity_id"],
                routing_key,
                item["resource_type"],
                item["id"],
                get_correlation_id(),
                Jsonb(item["payload"]),
                actor,
            ),
        )

    def audit_log(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit.logs WHERE module = 'marketplace' ORDER BY created_at DESC"
        ).fetchall()]

    def outbox(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit.domain_events WHERE routing_key LIKE 'marketplace.%' OR routing_key LIKE 'valley.%' ORDER BY created_at DESC"
        ).fetchall()]

    def metrics(self) -> tuple[int, int, int]:
        records = sum(
            self.connection.execute(
                sql.SQL("SELECT COUNT(*) AS count FROM {}").format(self._table(resource_type))
            ).fetchone()["count"]
            for resource_type in TABLES
        )
        audits = self.connection.execute("SELECT COUNT(*) AS count FROM audit.logs WHERE module = 'marketplace'").fetchone()["count"]
        events = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.domain_events WHERE routing_key LIKE 'marketplace.%' OR routing_key LIKE 'valley.%'"
        ).fetchone()["count"]
        return records, audits, events
