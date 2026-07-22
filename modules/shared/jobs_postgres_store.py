from __future__ import annotations

from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb

from .postgres_store import BasePostgresStore, _date


class JobsPostgresStore(BasePostgresStore):
    """Production Jobs adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "jobs"
    backend = "postgres_jobs_typed_store"
    tables = {
        "resumes": "jobs.resumes",
        "employment_records": "jobs.employment_records",
        "resume_documents": "jobs.resume_documents",
        "job_postings": "jobs.job_postings",
        "applications": "jobs.applications",
        "resume_access_logs": "jobs.resume_access_logs",
    }
    soft_deletable = frozenset(
        {"resumes", "employment_records", "job_postings", "applications"}
    )

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
                    resource_id,
                    user_id,
                    payload["headline"],
                    payload.get("professional_summary"),
                    Jsonb(payload.get("skills", [])),
                    Jsonb(payload.get("education", [])),
                    payload["recruiter_visibility"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
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
                    resource_id,
                    user_id,
                    payload["resume_id"],
                    payload["document_type"],
                    payload.get("storage_key"),
                    payload.get("storage_encryption", "AES-256-GCM"),
                    payload["sha256"],
                    payload.get("page_count"),
                    payload["evidence_status"],
                    payload["official_verification_status"],
                    payload["extraction_status"],
                    Jsonb(payload),
                    status,
                    metadata,
                    actor,
                    idempotency_key,
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
                    resource_id,
                    user_id,
                    payload["resume_id"],
                    payload.get("source_document_id"),
                    payload["source_type"],
                    payload["evidence_status"],
                    payload["official_verification_status"],
                    payload["employer_name"],
                    payload.get("employer_cnpj"),
                    payload.get("role_title"),
                    _date(payload["started_on"]),
                    _date(payload.get("ended_on")),
                    payload.get("user_activity_description"),
                    payload.get("is_informal_activity", False),
                    payload.get("visible_to_recruiter", True),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
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
                    resource_id,
                    user_id,
                    payload["company_id"],
                    payload["title"],
                    payload["description"],
                    payload.get("requirements"),
                    payload.get("employment_type"),
                    payload.get("workplace_model"),
                    payload.get("salary_min_brl"),
                    payload.get("salary_max_brl"),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "applications":
            return connection.execute(
                """INSERT INTO jobs.applications
                   (id, user_id, job_posting_id, resume_id, cover_letter, status, metadata,
                    created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["job_posting_id"],
                    payload["resume_id"],
                    payload.get("cover_letter"),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "resume_access_logs":
            return connection.execute(
                """INSERT INTO jobs.resume_access_logs
                   (id, user_id, resume_id, business_id, recruiter_user_id, purpose, status,
                    metadata, created_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["resume_id"],
                    payload["business_id"],
                    actor,
                    payload["purpose"],
                    status,
                    metadata,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        raise ValueError(f"Recurso Jobs desconhecido: {resource_type}")

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
        if resource_type == "resumes":
            return connection.execute(
                """UPDATE jobs.resumes SET headline = %s, professional_summary = %s, skills = %s,
                   education = %s, recruiter_visibility = %s, status = %s, metadata = %s,
                   updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (
                    payload["headline"],
                    payload.get("professional_summary"),
                    Jsonb(payload.get("skills", [])),
                    Jsonb(payload.get("education", [])),
                    payload["recruiter_visibility"],
                    status,
                    metadata,
                    actor,
                    resource_id,
                ),
            ).fetchone()
        if resource_type == "employment_records":
            return connection.execute(
                """UPDATE jobs.employment_records SET role_title = %s, ended_on = %s,
                   user_activity_description = %s, visible_to_recruiter = %s, status = %s,
                   metadata = %s, updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (
                    payload.get("role_title"),
                    _date(payload.get("ended_on")),
                    payload.get("user_activity_description"),
                    payload.get("visible_to_recruiter", True),
                    status,
                    metadata,
                    actor,
                    resource_id,
                ),
            ).fetchone()
        if resource_type == "job_postings":
            return connection.execute(
                """UPDATE jobs.job_postings SET title = %s, description = %s, requirements = %s,
                   employment_type = %s, workplace_model = %s, salary_min_brl = %s, salary_max_brl = %s,
                   status = %s, published_at = CASE WHEN %s = 'published' AND published_at IS NULL THEN NOW() ELSE published_at END,
                   metadata = %s, updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (
                    payload["title"],
                    payload["description"],
                    payload.get("requirements"),
                    payload.get("employment_type"),
                    payload.get("workplace_model"),
                    payload.get("salary_min_brl"),
                    payload.get("salary_max_brl"),
                    status,
                    status,
                    metadata,
                    actor,
                    resource_id,
                ),
            ).fetchone()
        if resource_type == "applications":
            return connection.execute(
                """UPDATE jobs.applications SET cover_letter = %s, status = %s, metadata = %s,
                   updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *""",
                (payload.get("cover_letter"), status, metadata, actor, resource_id),
            ).fetchone()
        raise ValueError(f"Recurso Jobs imutavel ou desconhecido: {resource_type}")
