from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

import psycopg
from psycopg import Connection, sql
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .audit_contract import insert_postgres_audit
from .correlation import get_correlation_id
from .event_contract import EVENT_SCHEMA_VERSION, build_event_envelope
from .generic_postgres_resource import insert_generic_resource, update_generic_resource
from .store import DuplicateValueError

TABLES = {
    "rides": "mobility.rides",
    "tickets": "mobility.tickets",
    "routes": "mobility.routes",
    "stops": "mobility.stops",
    "fare_rules": "mobility.fare_rules",
}
SOFT_DELETABLE = frozenset(TABLES)


class MobilityPostgresStore:
    """Production Mobility adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "mobility"
    backend = "postgres_mobility_typed_store"

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

    def _resource(
        self, resource_type: str, row: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        if row is None:
            return None
        created_at = row.get("created_at")
        if created_at is None:
            raise RuntimeError(
                f"PostgreSQL nao retornou timestamp para {resource_type}."
            )
        return {
            "id": str(row["id"]),
            "module": self.module,
            "resource_type": resource_type,
            "user_id": str(row["user_id"]),
            "entity_id": None,
            "status": row["status"],
            "payload": self._payload(row),
            "created_by": str(row["created_by"])
            if row.get("created_by")
            else str(row["user_id"]),
            "updated_by": str(
                row.get("updated_by") or row.get("created_by") or row["user_id"]
            ),
            "created_at": created_at.isoformat(),
            "updated_at": (row.get("updated_at") or created_at).isoformat(),
            "deleted_at": row.get("deleted_at").isoformat()
            if row.get("deleted_at")
            else None,
            "idempotency_key": row.get("idempotency_key"),
        }

    @staticmethod
    def _metadata(payload: dict[str, Any]) -> Jsonb:
        return Jsonb({"runtime_payload": payload})

    def find_idempotent(
        self, resource_type: str, key: str | None
    ) -> dict[str, Any] | None:
        if not key:
            return None
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE idempotency_key = %s").format(
                self._table(resource_type)
            ),
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
                row = self._insert(
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
                item = self._resource(resource_type, row)
                if item is None:
                    raise RuntimeError(
                        "PostgreSQL nao retornou recurso Mobility criado."
                    )
                self._audit(
                    connection,
                    actor,
                    "create",
                    resource_type,
                    resource_id,
                    None,
                    item,
                    user_id,
                    entity_id,
                )
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
        if resource_type == "rides":
            return connection.execute(
                """INSERT INTO mobility.rides
                   (id, user_id, driver_user_id, escrow_id, origin, destination, fare_brl, vehicle_type,
                    status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload.get("driver_user_id"),
                    payload.get("escrow_id"),
                    Jsonb(payload["origin"]),
                    Jsonb(payload["destination"]),
                    payload.get("fare_brl"),
                    payload.get("vehicle_type"),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "tickets":
            return connection.execute(
                """INSERT INTO mobility.tickets
                   (id, user_id, route_code, amount_brl, qr_token_hash, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["route_code"],
                    payload["amount_brl"],
                    payload["qr_token_hash"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        return insert_generic_resource(
            connection,
            TABLES[resource_type],
            resource_id,
            user_id,
            entity_id,
            status,
            payload,
            actor,
            idempotency_key,
        )

    def get(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        deleted = (
            sql.SQL(" AND deleted_at IS NULL")
            if resource_type in SOFT_DELETABLE
            else sql.SQL("")
        )
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE id = %s{}").format(
                self._table(resource_type), deleted
            ),
            (resource_id,),
        ).fetchone()
        return self._resource(resource_type, row)

    def list(
        self, resource_type: str, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        conditions = (
            sql.SQL("deleted_at IS NULL")
            if resource_type in SOFT_DELETABLE
            else sql.SQL("TRUE")
        )
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
        return [
            item
            for row in rows
            if (item := self._resource(resource_type, row)) is not None
        ]

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
            row = self._update(
                connection, item["resource_type"], item["id"], payload, status, actor
            )
            updated = self._resource(item["resource_type"], row)
            if updated is None:
                raise RuntimeError(
                    "PostgreSQL nao retornou recurso Mobility atualizado."
                )
            self._audit(
                connection,
                actor,
                action,
                item["resource_type"],
                item["id"],
                before,
                updated,
                item["user_id"],
                item["entity_id"],
            )
            if event:
                self._event(connection, event, actor, updated)
            return updated

    def _update(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        payload: dict[str, Any],
        status: str,
        actor: str,
    ) -> dict[str, Any]:
        metadata = self._metadata(payload)
        if resource_type == "rides":
            return connection.execute(
                """UPDATE mobility.rides SET driver_user_id = %s, status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload.get("driver_user_id"), status, metadata, actor, resource_id),
            ).fetchone()
        if resource_type == "tickets":
            return connection.execute(
                """UPDATE mobility.tickets SET used_at = %s, status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload.get("used_at"), status, metadata, actor, resource_id),
            ).fetchone()
        return update_generic_resource(
            connection, TABLES[resource_type], resource_id, payload, status, actor
        )

    def soft_delete(self, item: dict[str, Any], actor: str) -> None:
        with self.transaction() as connection:
            connection.execute(
                sql.SQL(
                    "UPDATE {} SET deleted_at = NOW(), updated_by = %s, updated_at = NOW() WHERE id = %s"
                ).format(self._table(item["resource_type"])),
                (actor, item["id"]),
            )
            self._audit(
                connection,
                actor,
                "soft_delete",
                item["resource_type"],
                item["id"],
                item,
                None,
                item["user_id"],
                item["entity_id"],
            )

    def audit_external(
        self,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            return self._audit(
                connection,
                actor,
                action,
                resource_type,
                resource_id,
                None,
                data,
                data.get("user_id"),
                None,
            )

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
        return insert_postgres_audit(
            connection,
            module="mobility",
            actor_user_id=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before=before,
            after=after,
            user_id=user_id,
            company_id=entity_id,
        )

    def _event(
        self, connection: Connection, routing_key: str, actor: str, item: dict[str, Any]
    ) -> None:
        correlation_id = get_correlation_id()
        envelope = build_event_envelope(
            module=self.module,
            routing_key=routing_key,
            actor_user_id=actor,
            item=item,
            correlation_id=correlation_id,
        )
        connection.execute(
            """INSERT INTO audit.domain_events
               (id, user_id, actor_user_id, entity_id, routing_key, aggregate_type, aggregate_id, correlation_id, schema_version, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                envelope["event_id"],
                item["user_id"],
                actor,
                item["entity_id"],
                routing_key,
                item["resource_type"],
                item["id"],
                correlation_id,
                EVENT_SCHEMA_VERSION,
                Jsonb(envelope),
                actor,
            ),
        )

    def audit_log(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM audit.logs WHERE module = 'mobility' ORDER BY created_at DESC"
            ).fetchall()
        ]

    def outbox(self) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.connection.execute(
                "SELECT * FROM audit.domain_events WHERE routing_key LIKE 'mobility.%' ORDER BY created_at DESC"
            ).fetchall()
        ]

    def metrics(self) -> tuple[int, int, int]:
        records = sum(
            self.connection.execute(
                sql.SQL("SELECT COUNT(*) AS count FROM {}").format(
                    self._table(resource_type)
                )
            ).fetchone()["count"]
            for resource_type in TABLES
        )
        audits = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.logs WHERE module = 'mobility'"
        ).fetchone()["count"]
        events = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.domain_events WHERE routing_key LIKE 'mobility.%'"
        ).fetchone()["count"]
        return records, audits, events
