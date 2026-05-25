from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any, Iterator
from uuid import uuid4


def now() -> str:
    return datetime.now(UTC).isoformat()


class DuplicateValueError(ValueError):
    pass


class SQLiteStore:
    """Durable local contract store; PostgreSQL migrations remain production authority."""

    def __init__(self, module: str, database_path: str = ":memory:") -> None:
        self.module = module
        self.backend = "sqlite_contract_store"
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = RLock()
        self._initialize()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self.lock:
            try:
                yield self.connection
                self.connection.commit()
            except Exception:
                self.connection.rollback()
                raise

    def _initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    module TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    entity_id TEXT,
                    status TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    updated_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    deleted_at TEXT,
                    idempotency_key TEXT
                );
                CREATE UNIQUE INDEX IF NOT EXISTS resources_idempotency
                    ON resources(module, idempotency_key)
                    WHERE idempotency_key IS NOT NULL;
                CREATE INDEX IF NOT EXISTS resources_query
                    ON resources(module, resource_type, user_id, status);
                CREATE TABLE IF NOT EXISTS unique_attributes (
                    module TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    PRIMARY KEY (module, resource_type, attribute, value)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    module TEXT NOT NULL,
                    actor_user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    before_data TEXT,
                    after_data TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS domain_events (
                    id TEXT PRIMARY KEY,
                    module TEXT NOT NULL,
                    routing_key TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    actor_user_id TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    published_at TEXT
                );
                """
            )

    @staticmethod
    def _resource(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        item = dict(row)
        item["payload"] = json.loads(item["payload"])
        return item

    def find_idempotent(self, key: str | None) -> dict[str, Any] | None:
        if not key:
            return None
        row = self.connection.execute(
            "SELECT * FROM resources WHERE module = ? AND idempotency_key = ?",
            (self.module, key),
        ).fetchone()
        return self._resource(row)

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
        previous = self.find_idempotent(idempotency_key)
        if previous:
            return previous
        resource_id = str(uuid4())
        timestamp = now()
        item = {
            "id": resource_id,
            "module": self.module,
            "resource_type": resource_type,
            "user_id": user_id,
            "entity_id": entity_id,
            "status": status,
            "payload": payload,
            "created_by": actor,
            "updated_by": actor,
            "created_at": timestamp,
            "updated_at": timestamp,
            "deleted_at": None,
            "idempotency_key": idempotency_key,
        }
        with self.transaction() as connection:
            for field in unique_fields:
                value = payload.get(field)
                if value is None:
                    continue
                try:
                    connection.execute(
                        "INSERT INTO unique_attributes VALUES (?, ?, ?, ?, ?)",
                        (self.module, resource_type, field, str(value).casefold(), resource_id),
                    )
                except sqlite3.IntegrityError as exc:
                    raise DuplicateValueError(field) from exc
            connection.execute(
                """
                INSERT INTO resources
                (id, module, resource_type, user_id, entity_id, status, payload, created_by,
                 updated_by, created_at, updated_at, deleted_at, idempotency_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    resource_id,
                    self.module,
                    resource_type,
                    user_id,
                    entity_id,
                    status,
                    json.dumps(payload, sort_keys=True),
                    actor,
                    actor,
                    timestamp,
                    timestamp,
                    None,
                    idempotency_key,
                ),
            )
            self._audit(connection, actor, "create", resource_type, resource_id, None, item)
            self._event(connection, event, actor, item)
        return item

    def get(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM resources WHERE module = ? AND resource_type = ? AND id = ? AND deleted_at IS NULL",
            (self.module, resource_type, resource_id),
        ).fetchone()
        return self._resource(row)

    def list(self, resource_type: str, user_id: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM resources WHERE module = ? AND resource_type = ? AND deleted_at IS NULL"
        params: list[Any] = [self.module, resource_type]
        if user_id:
            sql += " AND user_id = ?"
            params.append(user_id)
        sql += " ORDER BY created_at DESC"
        return [self._resource(row) for row in self.connection.execute(sql, params).fetchall()]  # type: ignore[misc]

    def update(
        self,
        item: dict[str, Any],
        payload: dict[str, Any],
        status: str,
        actor: str,
        action: str,
        event: str | None = None,
    ) -> dict[str, Any]:
        before = dict(item)
        before["payload"] = dict(item["payload"])
        item["payload"] = payload
        item["status"] = status
        item["updated_by"] = actor
        item["updated_at"] = now()
        with self.transaction() as connection:
            connection.execute(
                "UPDATE resources SET payload = ?, status = ?, updated_by = ?, updated_at = ? WHERE id = ?",
                (json.dumps(payload, sort_keys=True), status, actor, item["updated_at"], item["id"]),
            )
            self._audit(connection, actor, action, item["resource_type"], item["id"], before, item)
            if event:
                self._event(connection, event, actor, item)
        return item

    def soft_delete(self, item: dict[str, Any], actor: str) -> None:
        item["deleted_at"] = now()
        item["updated_by"] = actor
        with self.transaction() as connection:
            connection.execute(
                "UPDATE resources SET deleted_at = ?, updated_by = ?, updated_at = ? WHERE id = ?",
                (item["deleted_at"], actor, item["deleted_at"], item["id"]),
            )
            self._audit(connection, actor, "soft_delete", item["resource_type"], item["id"], item, None)

    def audit_external(self, actor: str, action: str, resource_type: str, resource_id: str, data: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            return self._audit(connection, actor, action, resource_type, resource_id, None, data)

    def _audit(
        self,
        connection: sqlite3.Connection,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        before: Any,
        after: Any,
    ) -> dict[str, Any]:
        evidence = {
            "id": str(uuid4()),
            "module": self.module,
            "actor_user_id": actor,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "before_data": before,
            "after_data": after,
            "created_at": now(),
        }
        connection.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                evidence["id"],
                self.module,
                actor,
                action,
                resource_type,
                resource_id,
                json.dumps(before, sort_keys=True) if before else None,
                json.dumps(after, sort_keys=True) if after else None,
                evidence["created_at"],
            ),
        )
        return evidence

    def _event(self, connection: sqlite3.Connection, routing_key: str, actor: str, item: dict[str, Any]) -> None:
        connection.execute(
            "INSERT INTO domain_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid4()),
                self.module,
                routing_key,
                item["user_id"],
                item["resource_type"],
                item["id"],
                actor,
                json.dumps(item["payload"], sort_keys=True),
                now(),
                None,
            ),
        )

    def audit_log(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit_events WHERE module = ? ORDER BY created_at DESC", (self.module,)
        ).fetchall()]

    def outbox(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM domain_events WHERE module = ? ORDER BY created_at DESC", (self.module,)
        ).fetchall()]

    def metrics(self) -> tuple[int, int, int]:
        records = self.connection.execute(
            "SELECT COUNT(*) FROM resources WHERE module = ? AND deleted_at IS NULL", (self.module,)
        ).fetchone()[0]
        audits = self.connection.execute("SELECT COUNT(*) FROM audit_events WHERE module = ?", (self.module,)).fetchone()[0]
        events = self.connection.execute("SELECT COUNT(*) FROM domain_events WHERE module = ?", (self.module,)).fetchone()[0]
        return records, audits, events
