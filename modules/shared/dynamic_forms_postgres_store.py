from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from uuid import uuid4

import psycopg
from psycopg import Connection
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .correlation import get_correlation_id
from .dynamic_forms import (
    DynamicFormValidationError,
    assert_transition,
    validate_blueprint,
    validate_submission_values,
)
from .event_contract import EVENT_SCHEMA_VERSION, build_event_envelope


class DynamicFormsPostgresStore:
    """Persistência normalizada do builder; toda consulta de negócio inclui tenant_id."""

    def __init__(self, dsn: str) -> None:
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        try:
            with self.connection.transaction():
                yield self.connection
        except Exception:
            raise

    def close(self) -> None:
        self.connection.close()

    def list_catalog(self, domain: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM forms.field_catalog WHERE status = 'active'"
        params: list[Any] = []
        if domain:
            query += " AND domain = %s"
            params.append(domain)
        query += " ORDER BY domain, logical_entity, logical_field, version DESC"
        return [dict(row) for row in self.connection.execute(query, params).fetchall()]

    def list_bindings(self, catalog_ids: list[str]) -> list[dict[str, Any]]:
        if not catalog_ids:
            return []
        return [
            dict(row)
            for row in self.connection.execute(
                """SELECT * FROM forms.field_bindings
                   WHERE status = 'active' AND field_catalog_id = ANY(%s::uuid[])
                   ORDER BY field_catalog_id, version DESC""",
                (catalog_ids,),
            ).fetchall()
        ]

    def create_definition(
        self,
        *,
        tenant_id: str,
        company_id: str | None,
        module_id: str,
        business_context: str,
        name: str,
        description: str | None,
        change_summary: str,
        actor_user_id: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        definition_id = str(uuid4())
        version_id = str(uuid4())
        try:
            with self.transaction() as connection:
                definition = connection.execute(
                    """INSERT INTO forms.form_definitions
                       (id, tenant_id, company_id, module_id, business_context, name, description,
                        status, created_by, updated_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s)
                       RETURNING *""",
                    (
                        definition_id,
                        tenant_id,
                        company_id,
                        module_id,
                        business_context,
                        name,
                        description,
                        actor_user_id,
                        actor_user_id,
                    ),
                ).fetchone()
                version = connection.execute(
                    """INSERT INTO forms.form_versions
                       (id, form_definition_id, version_number, schema_version, status, change_summary, created_by)
                       VALUES (%s, %s, 1, 1, 'draft', %s, %s)
                       RETURNING *""",
                    (version_id, definition_id, change_summary, actor_user_id),
                ).fetchone()
                connection.execute(
                    "UPDATE forms.form_definitions SET current_version_id = %s WHERE id = %s",
                    (version_id, definition_id),
                )
                self._billing_event(
                    connection,
                    tenant_id=tenant_id,
                    definition_id=definition_id,
                    version_id=version_id,
                    event_type="form_request_created",
                    actor_user_id=actor_user_id,
                    idempotency_key=idempotency_key,
                )
                return {"definition": dict(definition), "version": dict(version)}
        except UniqueViolation as exc:
            raise DynamicFormValidationError(
                "Formulario ou chave de idempotencia ja existente no tenant."
            ) from exc

    def list_definitions(
        self, tenant_id: str, *, status: str | None = None
    ) -> list[dict[str, Any]]:
        query = """SELECT d.*, v.version_number, v.status AS version_status, v.checksum
                   FROM forms.form_definitions d
                   JOIN forms.form_versions v ON v.id = d.current_version_id
                   WHERE d.tenant_id = %s AND d.deleted_at IS NULL"""
        params: list[Any] = [tenant_id]
        if status:
            query += " AND d.status = %s"
            params.append(status)
        query += " ORDER BY d.updated_at DESC, d.id"
        return [dict(row) for row in self.connection.execute(query, params).fetchall()]

    def get_blueprint(
        self,
        tenant_id: str,
        version_id: str,
        *,
        connection: Connection | None = None,
        lock: bool = False,
    ) -> dict[str, Any]:
        executor = connection or self.connection
        lock_sql = " FOR UPDATE" if lock else ""
        version = executor.execute(
            """SELECT v.*, d.tenant_id, d.company_id, d.module_id, d.business_context, d.name AS form_name
               FROM forms.form_versions v
               JOIN forms.form_definitions d ON d.id = v.form_definition_id
               WHERE v.id = %s AND d.tenant_id = %s AND d.deleted_at IS NULL"""
            + lock_sql,
            (version_id, tenant_id),
        ).fetchone()
        if version is None:
            raise KeyError("Versao de formulario nao localizada no tenant.")
        collections = {
            "blocks": "form_blocks",
            "fields": "form_fields",
            "calculations": "form_calculations",
            "validations": "form_validations",
            "visibility_rules": "form_visibility_rules",
        }
        blueprint: dict[str, Any] = {}
        for key, table in collections.items():
            order = (
                "display_order, id"
                if key in {"blocks", "fields", "calculations"}
                else "created_at, id"
            )
            blueprint[key] = [
                dict(row)
                for row in executor.execute(
                    f"SELECT * FROM forms.{table} WHERE form_version_id = %s ORDER BY {order}",
                    (version_id,),
                ).fetchall()
            ]
        return {"version": dict(version), "blueprint": blueprint}

    def replace_blueprint(
        self,
        tenant_id: str,
        version_id: str,
        blueprint: dict[str, Any],
        actor_user_id: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            current = self.get_blueprint(
                tenant_id, version_id, connection=connection, lock=True
            )
            if current["version"]["status"] not in {
                "draft",
                "editing",
                "changes_requested",
                "rejected",
            }:
                raise DynamicFormValidationError(
                    "Somente versao editavel pode receber alteracoes."
                )
            catalog_ids = sorted(
                {
                    str(item.get("field_catalog_id"))
                    for item in blueprint.get("fields") or []
                }
            )
            binding_ids = sorted(
                {
                    str(item.get("field_binding_id"))
                    for item in blueprint.get("fields") or []
                }
            )
            catalog_rows = (
                connection.execute(
                    "SELECT * FROM forms.field_catalog WHERE id = ANY(%s::uuid[]) AND status = 'active'",
                    (catalog_ids,),
                ).fetchall()
                if catalog_ids
                else []
            )
            binding_rows = (
                connection.execute(
                    "SELECT * FROM forms.field_bindings WHERE id = ANY(%s::uuid[]) AND status = 'active'",
                    (binding_ids,),
                ).fetchall()
                if binding_ids
                else []
            )
            validated = validate_blueprint(
                blueprint,
                catalog={str(row["id"]): dict(row) for row in catalog_rows},
                bindings={str(row["id"]): dict(row) for row in binding_rows},
            )
            self._delete_blueprint(connection, version_id)
            self._insert_blueprint(
                connection, version_id, validated["blueprint"], actor_user_id
            )
            connection.execute(
                """UPDATE forms.form_versions
                   SET status = 'editing', checksum = %s
                   WHERE id = %s""",
                (validated["checksum"], version_id),
            )
            connection.execute(
                """UPDATE forms.form_definitions d SET updated_at = NOW(), updated_by = %s
                   FROM forms.form_versions v
                   WHERE v.id = %s AND d.id = v.form_definition_id AND d.tenant_id = %s""",
                (actor_user_id, version_id, tenant_id),
            )
            return self.get_blueprint(tenant_id, version_id, connection=connection)

    def request_homologation(
        self,
        tenant_id: str,
        version_id: str,
        actor_user_id: str,
        checklist: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            current = self.get_blueprint(
                tenant_id, version_id, connection=connection, lock=True
            )
            status = str(current["version"]["status"])
            assert_transition(status, "submitted")
            if not current["blueprint"]["fields"]:
                raise DynamicFormValidationError(
                    "Formulario vazio nao pode ser homologado."
                )
            homologation = connection.execute(
                """INSERT INTO forms.form_homologations
                   (form_version_id, requester_id, checklist, status)
                   VALUES (%s, %s, %s, 'requested') RETURNING *""",
                (version_id, actor_user_id, Jsonb(checklist)),
            ).fetchone()
            connection.execute(
                """UPDATE forms.form_versions SET status = 'submitted', submitted_at = NOW(), submitted_by = %s
                   WHERE id = %s""",
                (actor_user_id, version_id),
            )
            self._billing_event(
                connection,
                tenant_id=tenant_id,
                definition_id=str(current["version"]["form_definition_id"]),
                version_id=version_id,
                event_type="homologation_submitted",
                actor_user_id=actor_user_id,
                idempotency_key=idempotency_key,
            )
            return dict(homologation)

    def review_homologation(
        self,
        tenant_id: str,
        homologation_id: str,
        actor_user_id: str,
        result: str,
        notes: str | None,
        problems: list[dict[str, Any]],
        corrections: list[dict[str, Any]],
        evidence: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        target_status = {
            "approved": "approved",
            "changes_requested": "changes_requested",
            "rejected": "rejected",
        }.get(result)
        if target_status is None:
            raise DynamicFormValidationError("Resultado de homologacao invalido.")
        with self.transaction() as connection:
            homologation = connection.execute(
                """SELECT h.*, v.status AS version_status, v.form_definition_id
                   FROM forms.form_homologations h
                   JOIN forms.form_versions v ON v.id = h.form_version_id
                   JOIN forms.form_definitions d ON d.id = v.form_definition_id
                   WHERE h.id = %s AND d.tenant_id = %s
                   FOR UPDATE OF h, v""",
                (homologation_id, tenant_id),
            ).fetchone()
            if homologation is None:
                raise KeyError("Homologacao nao localizada no tenant.")
            if str(homologation["requester_id"]) == actor_user_id:
                raise DynamicFormValidationError(
                    "Segregacao de funcoes: solicitante nao pode homologar a propria versao."
                )
            if homologation["status"] not in {"requested", "under_review"}:
                raise DynamicFormValidationError("Homologacao ja encerrada.")
            assert_transition(str(homologation["version_status"]), target_status)
            updated = connection.execute(
                """UPDATE forms.form_homologations
                   SET result = %s, reviewer_id = %s, reviewed_at = NOW(), notes = %s,
                       problems = %s, corrections = %s, evidence = %s, status = %s
                   WHERE id = %s RETURNING *""",
                (
                    result,
                    actor_user_id,
                    notes,
                    Jsonb(problems),
                    Jsonb(corrections),
                    Jsonb(evidence),
                    target_status,
                    homologation_id,
                ),
            ).fetchone()
            if target_status == "approved":
                connection.execute(
                    """UPDATE forms.form_versions SET status = 'approved', approved_at = NOW(), approved_by = %s
                       WHERE id = %s""",
                    (actor_user_id, homologation["form_version_id"]),
                )
            elif target_status == "rejected":
                connection.execute(
                    """UPDATE forms.form_versions SET status = 'rejected', rejected_at = NOW(), rejected_by = %s,
                       rejection_reason = %s WHERE id = %s""",
                    (
                        actor_user_id,
                        notes or "Homologacao rejeitada.",
                        homologation["form_version_id"],
                    ),
                )
            else:
                connection.execute(
                    "UPDATE forms.form_versions SET status = 'changes_requested' WHERE id = %s",
                    (homologation["form_version_id"],),
                )
            self._billing_event(
                connection,
                tenant_id=tenant_id,
                definition_id=str(homologation["form_definition_id"]),
                version_id=str(homologation["form_version_id"]),
                event_type="homologation_approved"
                if target_status == "approved"
                else "change_requested",
                actor_user_id=actor_user_id,
                idempotency_key=idempotency_key,
            )
            return dict(updated)

    def publish_version(
        self,
        tenant_id: str,
        version_id: str,
        actor_user_id: str,
        environment: str,
        rollout_policy: dict[str, Any],
        tenant_scope: dict[str, Any],
        channels: list[str],
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            current = self.get_blueprint(
                tenant_id, version_id, connection=connection, lock=True
            )
            version = current["version"]
            assert_transition(str(version["status"]), "published")
            approved = connection.execute(
                """SELECT 1 FROM forms.form_homologations
                   WHERE form_version_id = %s AND status = 'approved' LIMIT 1""",
                (version_id,),
            ).fetchone()
            if approved is None or not version.get("checksum"):
                raise DynamicFormValidationError(
                    "Publicacao exige homologacao aprovada e checksum."
                )
            publication = connection.execute(
                """INSERT INTO forms.form_publications
                   (form_version_id, environment, published_by, rollout_policy, tenant_scope, channels, checksum)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *""",
                (
                    version_id,
                    environment,
                    actor_user_id,
                    Jsonb(rollout_policy),
                    Jsonb(tenant_scope),
                    Jsonb(channels),
                    version["checksum"],
                ),
            ).fetchone()
            connection.execute(
                """UPDATE forms.form_versions SET status = 'published', published_at = NOW(), published_by = %s
                   WHERE id = %s""",
                (actor_user_id, version_id),
            )
            connection.execute(
                """UPDATE forms.form_definitions SET status = 'active', current_version_id = %s,
                   updated_at = NOW(), updated_by = %s WHERE id = %s AND tenant_id = %s""",
                (version_id, actor_user_id, version["form_definition_id"], tenant_id),
            )
            previous = connection.execute(
                """SELECT COUNT(*) AS total FROM forms.form_publications p
                   JOIN forms.form_versions v ON v.id = p.form_version_id
                   WHERE v.form_definition_id = %s""",
                (version["form_definition_id"],),
            ).fetchone()
            event_type = (
                "initial_publication"
                if int(previous["total"]) == 1
                else "new_version_published"
            )
            self._billing_event(
                connection,
                tenant_id=tenant_id,
                definition_id=str(version["form_definition_id"]),
                version_id=version_id,
                event_type=event_type,
                actor_user_id=actor_user_id,
                idempotency_key=idempotency_key,
            )
            return dict(publication)

    def submit_form(
        self,
        tenant_id: str,
        definition_id: str,
        actor_user_id: str,
        values: dict[str, Any],
        context: dict[str, Any],
        source: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            previous = connection.execute(
                "SELECT * FROM forms.form_submissions WHERE tenant_id = %s AND idempotency_key = %s",
                (tenant_id, idempotency_key),
            ).fetchone()
            if previous is not None:
                return {"submission": dict(previous), "idempotent_replay": True}
            definition = connection.execute(
                """SELECT d.*, v.status AS version_status
                   FROM forms.form_definitions d
                   JOIN forms.form_versions v ON v.id = d.current_version_id
                   WHERE d.id = %s AND d.tenant_id = %s AND d.status = 'active'
                     AND v.status = 'published' AND d.deleted_at IS NULL
                   FOR SHARE OF d, v""",
                (definition_id, tenant_id),
            ).fetchone()
            if definition is None:
                raise KeyError("Formulario publicado nao localizado no tenant.")
            version_id = str(definition["current_version_id"])
            fields = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM forms.form_fields WHERE form_version_id = %s ORDER BY display_order, id",
                    (version_id,),
                ).fetchall()
            ]
            catalog_ids = sorted({str(field["field_catalog_id"]) for field in fields})
            catalogs = connection.execute(
                "SELECT * FROM forms.field_catalog WHERE id = ANY(%s::uuid[]) AND status = 'active'",
                (catalog_ids,),
            ).fetchall()
            normalized = validate_submission_values(
                fields=fields,
                catalog={str(row["id"]): dict(row) for row in catalogs},
                values=values,
            )
            submission_id = str(uuid4())
            correlation_id = get_correlation_id()
            submission = connection.execute(
                """INSERT INTO forms.form_submissions
                   (id, form_definition_id, form_version_id, user_id, tenant_id, context, target_entity,
                    status, completed_at, source, correlation_id, idempotency_key, validation_result)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 'completed', NOW(), %s, %s, %s, %s)
                   RETURNING *""",
                (
                    submission_id,
                    definition_id,
                    version_id,
                    actor_user_id,
                    tenant_id,
                    Jsonb(context),
                    definition["business_context"],
                    source,
                    correlation_id,
                    idempotency_key,
                    Jsonb({"valid": True, "field_count": len(normalized)}),
                ),
            ).fetchone()
            for value in normalized:
                connection.execute(
                    """INSERT INTO forms.form_submission_values
                       (submission_id, field_catalog_id, data_type, normalized_value, display_value,
                        unit, source, validation_result, sensitivity, encryption, schema_version)
                       VALUES (%s, %s, %s, %s, %s, %s, 'user', %s, %s, %s, 1)""",
                    (
                        submission_id,
                        value["field_catalog_id"],
                        value["data_type"],
                        Jsonb(value["normalized_value"]),
                        value["display_value"],
                        value["unit"],
                        Jsonb({"valid": True}),
                        value["sensitivity"],
                        "field_level"
                        if value["sensitivity"]
                        in {"personal", "sensitive", "restricted"}
                        else "platform_managed",
                    ),
                )
            event_item = {
                "id": submission_id,
                "resource_type": "form_submissions",
                "user_id": actor_user_id,
                "entity_id": tenant_id,
                "idempotency_key": idempotency_key,
                "payload": {
                    "form_definition_id": definition_id,
                    "form_version_id": version_id,
                    "status": "completed",
                    "field_count": len(normalized),
                    "source": source,
                },
            }
            envelope = build_event_envelope(
                module="dynamic_forms",
                routing_key="forms.submission.completed",
                actor_user_id=actor_user_id,
                item=event_item,
                correlation_id=correlation_id,
            )
            event_id = envelope["event_id"]
            connection.execute(
                """INSERT INTO audit.domain_events
                   (id, user_id, actor_user_id, entity_id, routing_key, aggregate_type, aggregate_id,
                    correlation_id, schema_version, payload, created_by)
                   VALUES (%s, %s, %s, %s, 'forms.submission.completed', 'form_submissions', %s,
                           %s, %s, %s, %s)""",
                (
                    event_id,
                    actor_user_id,
                    actor_user_id,
                    definition.get("company_id"),
                    submission_id,
                    correlation_id,
                    EVENT_SCHEMA_VERSION,
                    Jsonb(envelope),
                    actor_user_id,
                ),
            )
            connection.execute(
                "UPDATE forms.form_submissions SET audit_event_id = %s WHERE id = %s",
                (event_id, submission_id),
            )
            result = dict(submission)
            result["audit_event_id"] = event_id
            return {"submission": result, "idempotent_replay": False}

    @staticmethod
    def _delete_blueprint(connection: Connection, version_id: str) -> None:
        for table in (
            "form_calculations",
            "form_validations",
            "form_fields",
            "form_blocks",
            "form_visibility_rules",
        ):
            connection.execute(
                f"DELETE FROM forms.{table} WHERE form_version_id = %s", (version_id,)
            )

    @staticmethod
    def _ordered_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        pending = {str(item["id"]): item for item in blocks}
        ordered: list[dict[str, Any]] = []
        while pending:
            ready = [
                item
                for item in pending.values()
                if not item.get("parent_block_id")
                or str(item["parent_block_id"]) not in pending
            ]
            if not ready:
                raise DynamicFormValidationError(
                    "Ciclo de blocos impediu persistencia."
                )
            for item in sorted(
                ready,
                key=lambda row: (int(row.get("display_order", 0)), str(row["id"])),
            ):
                ordered.append(item)
                pending.pop(str(item["id"]))
        return ordered

    def _insert_blueprint(
        self,
        connection: Connection,
        version_id: str,
        blueprint: dict[str, Any],
        actor_user_id: str,
    ) -> None:
        for rule in blueprint["visibility_rules"]:
            connection.execute(
                """INSERT INTO forms.form_visibility_rules
                   (id, form_version_id, target_type, target_id, condition, operator, comparison_value,
                    result, priority, combination, status, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    rule["id"],
                    version_id,
                    rule["target_type"],
                    rule["target_id"],
                    Jsonb(rule["condition"]),
                    rule["operator"],
                    Jsonb(rule.get("comparison_value")),
                    rule["result"],
                    rule.get("priority", 0),
                    rule.get("combination", "and"),
                    rule.get("status", "active"),
                    actor_user_id,
                ),
            )
        for block in self._ordered_blocks(blueprint["blocks"]):
            connection.execute(
                """INSERT INTO forms.form_blocks
                   (id, form_version_id, block_type, parent_block_id, display_order, title, description,
                    width, collapsible, visibility_rule_id, repeatable, allowed_style, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    block["id"],
                    version_id,
                    block["block_type"],
                    block.get("parent_block_id"),
                    block.get("display_order", 0),
                    block["title"],
                    block.get("description"),
                    block.get("width", 12),
                    block.get("collapsible", False),
                    block.get("visibility_rule_id"),
                    block.get("repeatable", False),
                    block.get("allowed_style", "default"),
                    actor_user_id,
                ),
            )
        for field in blueprint["fields"]:
            connection.execute(
                """INSERT INTO forms.form_fields
                   (id, form_version_id, block_id, field_catalog_id, field_binding_id, component, label,
                    help_text, placeholder, required, read_only, hidden, display_order, width, mask, format,
                    default_value, value_source, unit, permissions, visibility_rule_id, validation_ids,
                    audit_policy, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                           %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    field["id"],
                    version_id,
                    field["block_id"],
                    field["field_catalog_id"],
                    field["field_binding_id"],
                    field["component"],
                    field["label"],
                    field.get("help_text"),
                    field.get("placeholder"),
                    field.get("required", False),
                    field.get("read_only", False),
                    field.get("hidden", False),
                    field.get("display_order", 0),
                    field.get("width", 12),
                    field.get("mask"),
                    field.get("format"),
                    Jsonb(field.get("default_value")),
                    field.get("value_source", "user"),
                    field.get("unit"),
                    Jsonb(field.get("permissions") or {}),
                    field.get("visibility_rule_id"),
                    Jsonb(field.get("validation_ids") or []),
                    Jsonb(field.get("audit_policy") or {}),
                    actor_user_id,
                ),
            )
        for validation in blueprint["validations"]:
            connection.execute(
                """INSERT INTO forms.form_validations
                   (id, form_version_id, field_id, validation_type, parameters, message_pt_br, severity,
                    condition, run_frontend, run_backend, status, version, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    validation["id"],
                    version_id,
                    validation.get("field_id"),
                    validation["validation_type"],
                    Jsonb(validation.get("parameters") or {}),
                    validation.get("message_pt_br") or "Valor invalido.",
                    validation.get("severity", "error"),
                    Jsonb(validation.get("condition")),
                    validation.get("run_frontend", True),
                    validation.get("run_backend", True),
                    validation.get("status", "active"),
                    validation.get("version", 1),
                    actor_user_id,
                ),
            )
        for calculation in blueprint["calculations"]:
            connection.execute(
                """INSERT INTO forms.form_calculations
                   (id, form_version_id, name, result_field_id, operand_field_ids, operation, safe_expression,
                    display_order, precision, rounding, trigger_mode, condition, unit, null_handling,
                    division_by_zero_handling, visibility, validation, status, version, created_by)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    calculation["id"],
                    version_id,
                    calculation.get("name") or str(calculation["id"]),
                    calculation["result_field_id"],
                    Jsonb(calculation["operand_field_ids"]),
                    calculation["operation"],
                    Jsonb(calculation["safe_expression"]),
                    calculation.get("display_order", 0),
                    calculation.get("precision"),
                    calculation.get("rounding"),
                    calculation.get("trigger_mode", "on_change"),
                    Jsonb(calculation.get("condition")),
                    calculation.get("unit"),
                    calculation.get("null_handling", "error"),
                    calculation.get("division_by_zero_handling", "error"),
                    calculation.get("visibility", "visible"),
                    Jsonb(calculation.get("validation") or {}),
                    calculation.get("status", "active"),
                    calculation.get("version", 1),
                    actor_user_id,
                ),
            )

    @staticmethod
    def _billing_event(
        connection: Connection,
        *,
        tenant_id: str,
        definition_id: str,
        version_id: str,
        event_type: str,
        actor_user_id: str,
        idempotency_key: str,
    ) -> None:
        connection.execute(
            """INSERT INTO forms.form_billing_events
               (tenant_id, form_definition_id, form_version_id, event_type, actor_user_id,
                idempotency_key, billing_reference)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                tenant_id,
                definition_id,
                version_id,
                event_type,
                actor_user_id,
                idempotency_key,
                Jsonb({"source": "dynamic_forms_api"}),
            ),
        )
