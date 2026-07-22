from __future__ import annotations

from typing import Any

from psycopg import Connection, sql
from psycopg.types.json import Jsonb


def insert_generic_resource(
    connection: Connection,
    table: str,
    resource_id: str,
    user_id: str,
    entity_id: str | None,
    status: str,
    payload: dict[str, Any],
    actor: str,
    idempotency_key: str | None,
) -> dict[str, Any]:
    schema_name, table_name = table.split(".", maxsplit=1)
    return connection.execute(
        sql.SQL(
            "INSERT INTO {} (id, user_id, company_id, status, metadata, created_by, updated_by, idempotency_key) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *"
        ).format(sql.Identifier(schema_name, table_name)),
        (resource_id, user_id, entity_id, status, Jsonb({"runtime_payload": payload}), actor, actor, idempotency_key),
    ).fetchone()


def update_generic_resource(
    connection: Connection,
    table: str,
    resource_id: str,
    payload: dict[str, Any],
    status: str,
    actor: str,
) -> dict[str, Any]:
    schema_name, table_name = table.split(".", maxsplit=1)
    return connection.execute(
        sql.SQL(
            "UPDATE {} SET status = %s, metadata = %s, updated_by = %s, updated_at = NOW() "
            "WHERE id = %s RETURNING *"
        ).format(sql.Identifier(schema_name, table_name)),
        (status, Jsonb({"runtime_payload": payload}), actor, resource_id),
    ).fetchone()
