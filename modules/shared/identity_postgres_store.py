from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from typing import Any, Iterator
from uuid import uuid4

import psycopg
from psycopg import Connection, sql
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .store import DuplicateValueError


TABLES = {
    "users": "identity_core.users",
    "kyc_records": "identity_core.kyc_records",
    "business_profiles": "identity_core.business_profiles",
    "consents": "identity_core.consents",
    "audit_logs": "identity_core.audit_logs",
}
SOFT_DELETABLE = frozenset({"users", "kyc_records", "business_profiles", "consents"})


class IdentityPostgresStore:
    """Production Identity adapter backed by typed PostgreSQL relations (identity_core)."""

    module = "identity"
    backend = "postgres_identity_core_store"

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
            "id": str(row["id"] if "id" in row else row["log_id"]),
            "module": self.module,
            "resource_type": resource_type,
            "user_id": str(row["id"]) if resource_type == "users" else str(row.get("user_id") or row.get("owner_user_id")),
            "entity_id": None,
            "status": row.get("account_status") or row.get("verification_status") or row.get("business_status") or "active",
            "payload": self._payload(row),
            "created_by": str(row.get("created_by") or row.get("id") or row.get("user_id") or row.get("owner_user_id")),
            "updated_by": str(row.get("updated_by") or row.get("id") or row.get("user_id") or row.get("owner_user_id")),
            "created_at": created_at.isoformat(),
            "updated_at": (row.get("updated_at") or created_at).isoformat(),
            "deleted_at": None,
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
        resource_id = str(uuid4()) if resource_type != "users" else user_id
        try:
            with self.transaction() as connection:
                row = self._insert(connection, resource_type, resource_id, user_id, entity_id, status, payload, actor, idempotency_key)
                item = self._resource(resource_type, row)
                if item is None:
                    raise RuntimeError(f"PostgreSQL nao retornou recurso Identity {resource_type} criado.")
                self._audit(connection, actor, "create", resource_type, item["id"], None, item, item["user_id"], entity_id)
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
        if resource_type == "users":
            return connection.execute(
                """INSERT INTO identity_core.users
                   (id, email, password_hash, full_name, document_cpf, mfa_enabled, mfa_secret,
                    account_status, idempotency_key, metadata)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, payload["email"], payload.get("password_hash", "argon2:initial_stub"),
                    payload["full_name"], payload.get("document_cpf"), payload.get("mfa_enabled", False),
                    payload.get("mfa_secret"), status, idempotency_key, metadata
                ),
            ).fetchone()
        
        if resource_type == "kyc_records":
            return connection.execute(
                """INSERT INTO identity_core.kyc_records
                   (id, user_id, biometry_hash, doc_front_url, doc_back_url, verification_status,
                    idempotency_key, metadata)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["biometry_hash"], payload.get("doc_front_url"),
                    payload.get("doc_back_url"), status, idempotency_key, metadata
                ),
            ).fetchone()

        if resource_type == "business_profiles":
            return connection.execute(
                """INSERT INTO identity_core.business_profiles
                   (id, owner_user_id, legal_name, trade_name, document_cnpj, cnae_primary,
                    business_status, idempotency_key, metadata)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["legal_name"], payload.get("trade_name"),
                    payload["document_cnpj"], payload.get("cnae_primary"), status, idempotency_key, metadata
                ),
            ).fetchone()

        if resource_type == "consents":
            return connection.execute(
                """INSERT INTO identity_core.consents
                   (id, user_id, document_version, consent_type, ip_address, user_agent,
                    idempotency_key, metadata)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["document_version"], payload["consent_type"],
                    payload.get("ip_address"), payload.get("user_agent"), idempotency_key, metadata
                ),
            ).fetchone()

        raise ValueError(f"Recurso Identity nao mapeado para insert direto: {resource_type}")

    def get(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            sql.SQL("SELECT * FROM {} WHERE id = %s").format(self._table(resource_type)),
            (resource_id,),
        ).fetchone()
        return self._resource(resource_type, row)

    def list(self, resource_type: str, user_id: str | None = None) -> list[dict[str, Any]]:
        parameters: list[Any] = []
        where = sql.SQL("")
        if user_id:
            col = "id" if resource_type == "users" else ("owner_user_id" if resource_type == "business_profiles" else "user_id")
            where = sql.SQL(" WHERE {} = %s").format(sql.Identifier(col))
            parameters.append(user_id)
        rows = self.connection.execute(
            sql.SQL("SELECT * FROM {}{} ORDER BY created_at DESC").format(
                self._table(resource_type), where
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
                raise RuntimeError(f"PostgreSQL nao retornou recurso Identity {item['resource_type']} atualizado.")
            self._audit(connection, actor, action, item["resource_type"], item["id"], before, updated, updated["user_id"], None)
            if event:
                self._event(connection, event, actor, updated)
            return updated

    def _update(
        self, connection: Connection, resource_type: str, resource_id: str, payload: dict[str, Any], status: str, actor: str
    ) -> dict[str, Any]:
        metadata = self._metadata(payload)
        if resource_type == "users":
            return connection.execute(
                """UPDATE identity_core.users SET full_name = %s, email = %s, account_status = %s,
                   metadata = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload["full_name"], payload["email"], status, metadata, resource_id),
            ).fetchone()
        
        if resource_type == "kyc_records":
            return connection.execute(
                """UPDATE identity_core.kyc_records SET verification_status = %s, audited_by = %s,
                   rejection_reason = %s, verified_at = CASE WHEN %s = 'APPROVED' THEN NOW() ELSE verified_at END,
                   metadata = %s WHERE id = %s RETURNING *""",
                (status, actor, payload.get("rejection_reason"), status, metadata, resource_id),
            ).fetchone()

        raise ValueError(f"Recurso Identity imutavel ou nao mapeado para update: {resource_type}")

    def soft_delete(self, item: dict[str, Any], actor: str) -> None:
        # User DDL didn't have deleted_at, but we can add it or just ignore if not needed.
        # For now, let's keep it consistent with the user's DDL which doesn't have it.
        raise HTTPException(status_code=409, detail="Recurso Identity Core nao suporta soft-delete no momento.")

    def audit_external(self, actor: str, action: str, resource_type: str, resource_id: str, data: dict[str, Any]) -> dict[str, Any]:
        with self.transaction() as connection:
            return self._audit(connection, actor, action, resource_type, resource_id, None, data, data.get("user_id"), None)

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
        # Usando a nova tabela identity_core.audit_logs conforme pedido
        evidence = connection.execute(
            """INSERT INTO identity_core.audit_logs
               (actor_user_id, action_type, target_table, target_record_id, old_payload, new_payload)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING *""",
            (actor, action, resource_type, resource_id, Jsonb(before) if before else None, Jsonb(after)),
        ).fetchone()
        # Tambem gravar na auditoria central para compatibilidade global
        connection.execute(
            """INSERT INTO audit.logs
               (user_id, actor_user_id, action, module, resource_type, resource_id, before_data, after_data)
               VALUES (%s, %s, %s, 'identity', %s, %s, %s, %s)""",
            (user_id, actor, action, resource_type, resource_id, Jsonb(before) if before else None, Jsonb(after)),
        )
        return dict(evidence)

    def _event(self, connection: Connection, routing_key: str, actor: str, item: dict[str, Any]) -> None:
        connection.execute(
            """INSERT INTO audit.domain_events
               (user_id, actor_user_id, routing_key, aggregate_type, aggregate_id, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (item["user_id"], actor, routing_key, item["resource_type"], item["id"], Jsonb(item["payload"]), actor),
        )

    def audit_log(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM identity_core.audit_logs ORDER BY created_at DESC"
        ).fetchall()]

    def outbox(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit.domain_events WHERE routing_key LIKE 'identity.%' ORDER BY created_at DESC"
        ).fetchall()]

    def metrics(self) -> tuple[int, int, int]:
        records = sum(
            self.connection.execute(
                sql.SQL("SELECT COUNT(*) AS count FROM {}").format(self._table(resource_type))
            ).fetchone()["count"]
            for resource_type in TABLES
        )
        audits = self.connection.execute("SELECT COUNT(*) AS count FROM identity_core.audit_logs").fetchone()["count"]
        events = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.domain_events WHERE routing_key LIKE 'identity.%'"
        ).fetchone()["count"]
        return records, audits, events
