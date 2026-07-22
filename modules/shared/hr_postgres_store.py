from __future__ import annotations

from typing import Any

from psycopg import Connection

from .postgres_store import BasePostgresStore


class HrPostgresStore(BasePostgresStore):
    """Production Hr adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "hr"
    backend = "postgres_hr_typed_store"
    tables = {
        "employees": "hr.employees",
        "payroll_runs": "hr.payroll_runs",
        "candidates": "hr.candidates",
        "courses": "hr.courses",
        "occupational_records": "hr.occupational_records",
    }
    soft_deletable = frozenset(
        ["employees", "payroll_runs", "candidates", "courses", "occupational_records"]
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
