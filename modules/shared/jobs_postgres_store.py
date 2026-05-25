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
    "resumes": "jobs.resumes",
    "employment_records": "jobs.employment_records",
    "resume_documents": "jobs.resume_documents",
    "job_postings": "jobs.job_postings",
    "applications": "jobs.applications",
    "resume_access_logs": "jobs.resume_access_logs",
}
SOFT_DELETABLE = frozenset({"resumes", "employment_records", "job_postings", "applications"})


def _date(value: Any) -> Any:
    if not value or isinstance(value, date):
        return value
    material = str(value)
    if "/" in material:
        return datetime.strptime(material, "%d/%m/%Y").date()
    return date.fromisoformat(material)


class JobsPostgresStore:
    """Production Jobs adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "jobs"
    backend = "postgres_jobs_typed_store"

    def __init__(self, dsn: str) -> None:
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)

    @staticmethod
    def _table(resource_type: str) -> sql.Identifier:
        schema_name, table_name = TABLES[resource_type].split(".", maxsplit=1)
        return sql.Identifier(schema_name, table_name)

    def verify_active_business_recruiter(self, user_id: str, business_id: str) -> bool:
        row = self.connection.execute(
            """SELECT 1
               FROM business.companies company
               JOIN business.user_company_memberships membership ON membership.company_id = company.id
               WHERE company.id = %s AND company.status IN ('approved', 'active')
                 AND membership.user_id = %s AND membership.status = 'active'""",
            (business_id, user_id),
        ).fetchone()
        return row is not None

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
        created_at = row.get("created_at") or row.get("accessed_at")
        if created_at is None:
            raise RuntimeError(f"PostgreSQL nao retornou timestamp para {resource_type}.")
        return {
            "id": str(row["id"]),
            "module": self.module,
            "resource_type": resource_type,
            "user_id": str(row["user_id"]),
            "entity_id": str(row.get("company_id") or row.get("business_id")) if row.get("company_id") or row.get("business_id") else None,
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
                    raise RuntimeError("PostgreSQL nao retornou recurso Jobs criado.")
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
        if resource_type == "resumes":
            return connection.execute(
                """INSERT INTO jobs.resumes
                   (id, user_id, headline, professional_summary, skills, education, recruiter_visibility,
                    status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["headline"], payload.get("professional_summary"),
                    Jsonb(payload.get("skills", [])), Jsonb(payload.get("education", [])),
                    payload["recruiter_visibility"], status, metadata, actor, actor, idempotency_key,
                ),
            ).fetchone()
        if resource_type == "resume_documents":
            return connection.execute(
                """INSERT INTO jobs.resume_documents
                   (id, user_id, resume_id, document_type, storage_key, storage_encryption, sha256,
                    page_count, evidence_status, official_verification_status, extraction_status,
                    extracted_fields, status, metadata, created_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["resume_id"], payload["document_type"], payload.get("storage_key"),
                    payload.get("storage_encryption", "AES-256-GCM"), payload["sha256"], payload.get("page_count"),
                    payload["evidence_status"], payload["official_verification_status"], payload["extraction_status"],
                    Jsonb(payload), status, metadata, actor, idempotency_key,
                ),
            ).fetchone()
        if resource_type == "employment_records":
            return connection.execute(
                """INSERT INTO jobs.employment_records
                   (id, user_id, resume_id, source_document_id, source_type, evidence_status,
                    official_verification_status, employer_name, employer_cnpj, role_title, started_on,
                    ended_on, user_activity_description, is_informal_activity, visible_to_recruiter,
                    status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING *""",
                (
                    resource_id, user_id, payload["resume_id"], payload.get("source_document_id"),
                    payload["source_type"], payload["evidence_status"], payload["official_verification_status"],
                    payload["employer_name"], payload.get("employer_cnpj"), payload.get("role_title"),
                    _date(payload["started_on"]), _date(payload.get("ended_on")), payload.get("user_activity_description"),
                    payload.get("is_informal_activity", False), payload.get("visible_to_recruiter", True),
                    status, metadata, actor, actor, idempotency_key,
                ),
            ).fetchone()
        if resource_type == "job_postings":
            return connection.execute(
                """INSERT INTO jobs.job_postings
                   (id, user_id, company_id, title, description, requirements, employment_type,
                    workplace_model, salary_min_brl, salary_max_brl, status, metadata,
                    created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["company_id"], payload["title"], payload["description"],
                    payload.get("requirements"), payload.get("employment_type"), payload.get("workplace_model"),
                    payload.get("salary_min_brl"), payload.get("salary_max_brl"), status, metadata,
                    actor, actor, idempotency_key,
                ),
            ).fetchone()
        if resource_type == "applications":
            return connection.execute(
                """INSERT INTO jobs.applications
                   (id, user_id, job_posting_id, resume_id, cover_letter, status, metadata,
                    created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["job_posting_id"], payload["resume_id"],
                    payload.get("cover_letter"), status, metadata, actor, actor, idempotency_key,
                ),
            ).fetchone()
        if resource_type == "resume_access_logs":
            return connection.execute(
                """INSERT INTO jobs.resume_access_logs
                   (id, user_id, resume_id, business_id, recruiter_user_id, purpose, status,
                    metadata, created_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id, user_id, payload["resume_id"], payload["business_id"], actor,
                    payload["purpose"], status, metadata, actor, idempotency_key,
                ),
            ).fetchone()
        raise ValueError(f"Recurso Jobs desconhecido: {resource_type}")

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
                raise RuntimeError("PostgreSQL nao retornou recurso Jobs atualizado.")
            self._audit(connection, actor, action, item["resource_type"], item["id"], before, updated, item["user_id"], item["entity_id"])
            if event:
                self._event(connection, event, actor, updated)
            return updated

    def _update(
        self, connection: Connection, resource_type: str, resource_id: str, payload: dict[str, Any], status: str, actor: str
    ) -> dict[str, Any]:
        metadata = self._metadata(payload)
        if resource_type == "resumes":
            return connection.execute(
                """UPDATE jobs.resumes SET headline = %s, professional_summary = %s, skills = %s,
                   education = %s, recruiter_visibility = %s, status = %s, metadata = %s,
                   updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (
                    payload["headline"], payload.get("professional_summary"), Jsonb(payload.get("skills", [])),
                    Jsonb(payload.get("education", [])), payload["recruiter_visibility"], status, metadata, actor, resource_id,
                ),
            ).fetchone()
        if resource_type == "employment_records":
            return connection.execute(
                """UPDATE jobs.employment_records SET role_title = %s, ended_on = %s,
                   user_activity_description = %s, visible_to_recruiter = %s, status = %s,
                   metadata = %s, updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (
                    payload.get("role_title"), _date(payload.get("ended_on")), payload.get("user_activity_description"),
                    payload.get("visible_to_recruiter", True), status, metadata, actor, resource_id,
                ),
            ).fetchone()
        if resource_type == "job_postings":
            return connection.execute(
                """UPDATE jobs.job_postings SET title = %s, description = %s, requirements = %s,
                   employment_type = %s, workplace_model = %s, salary_min_brl = %s, salary_max_brl = %s,
                   status = %s, published_at = CASE WHEN %s = 'published' AND published_at IS NULL THEN NOW() ELSE published_at END,
                   metadata = %s, updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (
                    payload["title"], payload["description"], payload.get("requirements"), payload.get("employment_type"),
                    payload.get("workplace_model"), payload.get("salary_min_brl"), payload.get("salary_max_brl"),
                    status, status, metadata, actor, resource_id,
                ),
            ).fetchone()
        if resource_type == "applications":
            return connection.execute(
                """UPDATE jobs.applications SET cover_letter = %s, status = %s, metadata = %s,
                   updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (payload.get("cover_letter"), status, metadata, actor, resource_id),
            ).fetchone()
        raise ValueError(f"Recurso Jobs imutavel ou desconhecido: {resource_type}")

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
            return self._audit(connection, actor, action, resource_type, resource_id, None, data, data.get("user_id"), data.get("business_id"))

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
               VALUES (%s, %s, %s, %s, 'jobs', %s, %s, %s, %s, %s) RETURNING *""",
            (user_id, actor, entity_id, action, resource_type, resource_id, Jsonb(before) if before else None, Jsonb(after), actor),
        ).fetchone()
        return dict(evidence)

    def _event(self, connection: Connection, routing_key: str, actor: str, item: dict[str, Any]) -> None:
        entity_id = item["entity_id"] if item["resource_type"] in {"job_postings", "resume_access_logs"} else None
        connection.execute(
            """INSERT INTO audit.domain_events
               (user_id, actor_user_id, entity_id, routing_key, aggregate_type, aggregate_id, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (item["user_id"], actor, entity_id, routing_key, item["resource_type"], item["id"], Jsonb(item["payload"]), actor),
        )

    def audit_log(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit.logs WHERE module = 'jobs' ORDER BY created_at DESC"
        ).fetchall()]

    def outbox(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.connection.execute(
            "SELECT * FROM audit.domain_events WHERE routing_key LIKE 'jobs.%' ORDER BY created_at DESC"
        ).fetchall()]

    def metrics(self) -> tuple[int, int, int]:
        records = sum(
            self.connection.execute(
                sql.SQL("SELECT COUNT(*) AS count FROM {}").format(self._table(resource_type))
            ).fetchone()["count"]
            for resource_type in TABLES
        )
        audits = self.connection.execute("SELECT COUNT(*) AS count FROM audit.logs WHERE module = 'jobs'").fetchone()["count"]
        events = self.connection.execute(
            "SELECT COUNT(*) AS count FROM audit.domain_events WHERE routing_key LIKE 'jobs.%'"
        ).fetchone()["count"]
        return records, audits, events
