from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterator, Protocol
from uuid import uuid4

import psycopg
from psycopg import Connection, sql
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .correlation import get_correlation_id
from .store import DuplicateValueError


def _date(value: Any) -> Any:
    if not value or isinstance(value, date):
        return value
    material = str(value)
    if "/" in material:
        return datetime.strptime(material, "%d/%m/%Y").date()
    return date.fromisoformat(material)


class BasePostgresStore:
    """Base class for typed PostgreSQL stores with common audit and outbox logic."""

    module: str
    backend: str
    tables: dict[str, str]
    soft_deletable: frozenset[str]

    def __init__(self, dsn: str) -> None:
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)
        self._column_cache: dict[str, set[str]] = {}

    def _table(self, resource_type: str) -> sql.Identifier:
        full_name = self.tables[resource_type]
        schema_name, table_name = full_name.split(".", maxsplit=1)
        return sql.Identifier(schema_name, table_name)

    def _table_columns(self, resource_type: str) -> set[str]:
        full_name = self.tables[resource_type]
        if full_name not in self._column_cache:
            schema_name, table_name = full_name.split(".", maxsplit=1)
            rows = self.connection.execute(
                """SELECT column_name
                   FROM information_schema.columns
                   WHERE table_schema = %s AND table_name = %s""",
                (schema_name, table_name),
            ).fetchall()
            self._column_cache[full_name] = {row["column_name"] for row in rows}
        return self._column_cache[full_name]

    @staticmethod
    def _column_value(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return Jsonb(value)
        if isinstance(value, float):
            return Decimal(str(value))
        return value

    def _insert_generic(
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
        columns = self._table_columns(resource_type)
        values: dict[str, Any] = {
            "id": resource_id,
            "user_id": user_id,
            "status": status,
            "metadata": self._metadata(payload),
            "created_by": actor,
            "updated_by": actor,
            "idempotency_key": idempotency_key,
        }
        if entity_id:
            for candidate in ("company_id", "business_id", "entity_id", "store_id", "warehouse_id"):
                if candidate in columns and candidate not in payload:
                    values[candidate] = entity_id
                    break
        for key, value in payload.items():
            if key in columns and key not in values:
                values[key] = self._column_value(value)
        filtered = {key: value for key, value in values.items() if key in columns}
        return connection.execute(
            sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
                self._table(resource_type),
                sql.SQL(", ").join(sql.Identifier(column) for column in filtered),
                sql.SQL(", ").join(sql.Placeholder() for _ in filtered),
            ),
            tuple(filtered.values()),
        ).fetchone()

    def _update_generic(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        payload: dict[str, Any],
        status: str,
        actor: str,
    ) -> dict[str, Any]:
        columns = self._table_columns(resource_type)
        values: dict[str, Any] = {"status": status, "metadata": self._metadata(payload), "updated_by": actor}
        for key, value in payload.items():
            if key in columns and key not in {"id", "user_id", "created_at", "created_by"}:
                values[key] = self._column_value(value)
        set_sql = [sql.SQL("{} = %s").format(sql.Identifier(column)) for column in values]
        if "updated_at" in columns:
            set_sql.append(sql.SQL("updated_at = NOW()"))
        return connection.execute(
            sql.SQL("UPDATE {} SET {} WHERE id = %s RETURNING *").format(
                self._table(resource_type),
                sql.SQL(", ").join(set_sql),
            ),
            (*values.values(), resource_id),
        ).fetchone()

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

    @staticmethod
    def _metadata(payload: dict[str, Any]) -> Jsonb:
        return Jsonb({"runtime_payload": payload})

    def _resource(self, resource_type: str, row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        created_at = row.get("created_at") or row.get("started_at") or row.get("accessed_at")
        if created_at is None:
            raise RuntimeError(f"PostgreSQL nao retornou timestamp para {resource_type}.")
        
        entity_id = row.get("company_id") or row.get("business_id") or row.get("store_id") or row.get("warehouse_id")
        
        if resource_type == "companies":
            entity_id = row["id"]

        row_user_id = row.get("user_id") or row["id"]
        return {
            "id": str(row["id"]),
            "module": self.module,
            "resource_type": resource_type,
            "user_id": str(row_user_id),
            "entity_id": str(entity_id) if entity_id else None,
            "status": row["status"],
            "payload": self._payload(row),
            "created_by": str(row["created_by"]) if row.get("created_by") else str(row_user_id),
            "updated_by": str(row.get("updated_by") or row.get("created_by") or row_user_id),
            "created_at": created_at.isoformat(),
            "updated_at": (row.get("updated_at") or created_at).isoformat(),
            "deleted_at": row.get("deleted_at").isoformat() if row.get("deleted_at") else None,
            "idempotency_key": row.get("idempotency_key"),
        }

    def find_idempotent(self, resource_type: str, key: str | None) -> dict[str, Any] | None:
        if not key:
            return None
        if "idempotency_key" not in self._table_columns(resource_type):
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
                    raise RuntimeError(f"PostgreSQL nao retornou recurso {self.module} criado.")
                self._audit(connection, actor, "create", resource_type, resource_id, None, item, user_id, entity_id)
                self._event(connection, event, actor, item)
                return item
        except UniqueViolation as exc:
            raise DuplicateValueError(resource_type) from exc

    def _insert(self, connection: Connection, resource_type: str, resource_id: str, user_id: str, 
                entity_id: str | None, status: str, payload: dict[str, Any], actor: str, 
                idempotency_key: str | None) -> dict[str, Any]:
        """Defaults to generic insert; subclasses can override for specialized logic."""
        return self._insert_generic(
            connection, resource_type, resource_id, user_id, entity_id, status, payload, actor, idempotency_key
        )

    def get(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        deleted = sql.SQL(" AND deleted_at IS NULL") if resource_type in self.soft_deletable else sql.SQL("")
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE id = %s{}").format(self._table(resource_type), deleted),
            (resource_id,),
        ).fetchone()
        return self._resource(resource_type, row)

    def list(self, resource_type: str, user_id: str | None = None) -> list[dict[str, Any]]:
        conditions = sql.SQL("deleted_at IS NULL") if resource_type in self.soft_deletable else sql.SQL("TRUE")
        parameters: list[Any] = []
        if user_id and "user_id" in self._table_columns(resource_type):
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
                raise RuntimeError(f"PostgreSQL nao retornou recurso {self.module} atualizado.")
            self._audit(connection, actor, action, item["resource_type"], item["id"], before, updated, item["user_id"], item["entity_id"])
            if event:
                self._event(connection, event, actor, updated)
            return updated

    def _update(self, connection: Connection, resource_type: str, resource_id: str, 
                payload: dict[str, Any], status: str, actor: str) -> dict[str, Any]:
        """Defaults to generic update; subclasses can override for specialized logic."""
        return self._update_generic(
            connection, resource_type, resource_id, payload, status, actor
        )

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
            return self._audit(connection, actor, action, resource_type, resource_id, None, data, data.get("user_id"), data.get("entity_id") or data.get("company_id"))

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
            sql.SQL("""INSERT INTO audit.logs
               (user_id, actor_user_id, actor_entity_id, action, module, resource_type, resource_id,
                before_data, after_data, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *"""),
            (user_id, actor, entity_id, action, self.module, resource_type, resource_id, 
             Jsonb(before) if before else None, Jsonb(after), actor),
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
            sql.SQL("SELECT * FROM audit.logs WHERE module = %s ORDER BY created_at DESC"), (self.module,)
        ).fetchall()]

    def outbox(self) -> list[dict[str, Any]]:
        routing_prefix = f"{self.module}.%"
        if self.module == "finance": routing_prefix = "payment.%"

        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit.domain_events WHERE routing_key LIKE %s ORDER BY created_at DESC", (routing_prefix,)
        ).fetchall()]

    def metrics(self) -> tuple[int, int, int]:
        records = sum(
            self.connection.execute(
                sql.SQL("SELECT COUNT(*) AS count FROM {}").format(self._table(resource_type))
            ).fetchone()["count"]
            for resource_type in self.tables
        )
        audits = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.logs WHERE module = %s", (self.module,)
        ).fetchone()["count"]
        
        routing_prefix = f"{self.module}.%"
        if self.module == "finance": routing_prefix = "payment.%"

        events = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.domain_events WHERE routing_key LIKE %s", (routing_prefix,)
        ).fetchone()["count"]
        return records, audits, events
