from __future__ import annotations

from typing import Any
from uuid import uuid4

from psycopg import Connection
from psycopg.errors import UniqueViolation

from .postgres_store import BasePostgresStore
from .store import DuplicateValueError


class IdentityPostgresStore(BasePostgresStore):
    """Production Identity adapter backed by typed PostgreSQL relations and central audit/outbox."""

    module = "identity"
    backend = "postgres_identity_typed_store"
    tables = {
        "users": "identity.users",
        "documents": "identity.documents",
        "biometrics": "identity.biometrics",
        "sessions": "identity.sessions",
        "identity_verifications": "identity.identity_verifications",
        "kyc_records": "identity.identity_verifications",
        "consent_records": "identity.consent_records",
    }
    soft_deletable = frozenset(
        {
            "users",
            "documents",
            "biometrics",
            "sessions",
            "identity_verifications",
            "kyc_records",
            "consent_records",
        }
    )

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
        if resource_type != "users":
            return super().create(
                resource_type,
                user_id,
                entity_id,
                status,
                payload,
                actor,
                unique_fields,
                event,
                idempotency_key,
            )

        previous = self.find_idempotent(resource_type, idempotency_key)
        if previous:
            return previous

        resource_id = str(payload.get("id") or user_id or uuid4())
        try:
            with self.transaction() as connection:
                row = self._insert(
                    connection,
                    resource_type,
                    resource_id,
                    resource_id,
                    entity_id,
                    status,
                    payload,
                    resource_id,
                    idempotency_key,
                )
                item = self._resource(resource_type, row)
                if item is None:
                    raise RuntimeError(
                        "PostgreSQL nao retornou usuario Identity criado."
                    )
                self._audit(
                    connection,
                    resource_id,
                    "create",
                    resource_type,
                    item["id"],
                    None,
                    item,
                    item["user_id"],
                    entity_id,
                )
                self._event(connection, event, resource_id, item)
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
                """INSERT INTO identity.users
                   (id, full_name, cpf_document, birth_date, email, phone_e164, password_hash,
                    face_hash, liveness_score, terms_accepted_at, lgpd_consent_at,
                    status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    payload["full_name"],
                    payload["cpf_document"],
                    payload["birth_date"],
                    payload["email"],
                    payload["phone_e164"],
                    payload["password_hash"],
                    payload["face_hash"],
                    payload["liveness_score"],
                    payload["terms_accepted_at"],
                    payload["lgpd_consent_at"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "documents":
            return connection.execute(
                """INSERT INTO identity.documents
                   (id, user_id, document_type, document_number_hash, storage_key, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["document_type"],
                    payload["document_number_hash"],
                    payload["storage_key"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "biometrics":
            return connection.execute(
                """INSERT INTO identity.biometrics
                   (id, user_id, face_hash, consent_recorded_at, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["face_hash"],
                    payload["consent_recorded_at"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "sessions":
            return connection.execute(
                """INSERT INTO identity.sessions
                   (id, user_id, token_hash, device_fingerprint, ip_address, expires_at, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["token_hash"],
                    payload["device_fingerprint"],
                    payload["ip_address"],
                    payload["expires_at"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type in {"identity_verifications", "kyc_records"}:
            return connection.execute(
                """INSERT INTO identity.identity_verifications
                   (id, user_id, verification_type, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload.get("verification_type", "kyc"),
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        if resource_type == "consent_records":
            return connection.execute(
                """INSERT INTO identity.consent_records
                   (id, user_id, consent_type, policy_version, accepted_at, status, metadata, created_by, updated_by, idempotency_key)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    resource_id,
                    user_id,
                    payload["consent_type"],
                    payload["policy_version"],
                    payload["accepted_at"],
                    status,
                    metadata,
                    actor,
                    actor,
                    idempotency_key,
                ),
            ).fetchone()
        raise ValueError(f"Recurso Identity desconhecido: {resource_type}")

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
        if resource_type == "users":
            return connection.execute(
                """UPDATE identity.users SET full_name = %s, status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload["full_name"], status, metadata, actor, resource_id),
            ).fetchone()
        if resource_type == "sessions":
            return connection.execute(
                """UPDATE identity.sessions SET revoked_at = %s, status = %s, metadata = %s, updated_by = %s, updated_at = NOW()
                   WHERE id = %s RETURNING *""",
                (payload.get("revoked_at"), status, metadata, actor, resource_id),
            ).fetchone()
        if resource_type in {
            "documents",
            "biometrics",
            "identity_verifications",
            "kyc_records",
            "consent_records",
        }:
            return connection.execute(
                sql.SQL(
                    "UPDATE {} SET status = %s, metadata = %s, updated_by = %s, updated_at = NOW() WHERE id = %s RETURNING *"
                ).format(self._table(resource_type)),
                (status, metadata, actor, resource_id),
            ).fetchone()
        raise ValueError(f"Recurso Identity imutavel ou desconhecido: {resource_type}")
