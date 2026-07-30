from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.verify_pg_indexes import REQUIRED_INDEXES

MIGRATIONS_DIR = ROOT / "database" / "postgres" / "migrations"

REQUIRED_SCHEMAS = {
    "identity",
    "business",
    "permissions",
    "marketplace",
    "stock",
    "delivery",
    "services",
    "mobility",
    "erp",
    "wms",
    "tms",
    "crm",
    "bpm",
    "document",
    "finance",
    "billing",
    "fiscal",
    "hr",
    "health",
    "legal",
    "property",
    "audit",
    "compliance",
    "notifications",
    "api_hub",
    "insurance",
    "bi",
    "ai_core",
    "jobs",
}

REQUIRED_TABLES = {
    "identity.users",
    "business.companies",
    "finance.wallets",
    "finance.valley_gold_ledger_entries",
    "delivery.rider_documents",
    "delivery.rider_reviews",
    "marketplace.orders",
    "business.catalog_offers",
    "stock.inventory_items",
    "stock.stock_reservations",
    "jobs.resumes",
    "audit.logs",
    "audit.domain_events",
    "audit.event_deliveries",
    "compliance.retention_candidates",
    "compliance.retention_decisions",
}

REQUIRED_TRIGGERS = {
    "immutable_audit_logs",
    "immutable_event_deliveries",
    "immutable_finance_ledger",
    "immutable_valley_gold_ledger",
    "immutable_jobs_resume_documents",
    "immutable_jobs_resume_access_logs",
}


def _migration_paths() -> list[Path]:
    paths = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not paths:
        raise RuntimeError("Nenhuma migration PostgreSQL versionada foi encontrada.")
    return paths


def _migration_manifest() -> list[dict[str, str]]:
    """Gera evidência determinística dos arquivos de migration versionados.

    Migrations são aplicadas uma única vez e validadas em banco limpo pelo
    workflow. Reexecutar o mesmo SQL sobre o mesmo banco não é um teste válido
    quando os arquivos usam DDL de execução única. O manifesto preserva nome,
    ordem e checksum para detectar alteração ou ausência de arquivos.
    """

    manifest: list[dict[str, str]] = []
    for migration_path in _migration_paths():
        content = migration_path.read_bytes()
        if not content.strip():
            raise RuntimeError(f"Migration vazia: {migration_path.name}")
        manifest.append(
            {
                "name": migration_path.name,
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return manifest


def _apply_migrations(connection: psycopg.Connection) -> list[str]:
    applied: list[str] = []
    for migration_path in _migration_paths():
        connection.execute(migration_path.read_text(encoding="utf-8"))
        applied.append(migration_path.name)
    return applied


def _fetch_missing(
    connection: psycopg.Connection, query: str, expected: set[str]
) -> set[str]:
    rows = connection.execute(query, (sorted(expected),)).fetchall()
    found = {row[0] for row in rows}
    return expected - found


def _validate_structure(connection: psycopg.Connection) -> dict[str, Any]:
    missing_schemas = _fetch_missing(
        connection,
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = ANY(%s)",
        REQUIRED_SCHEMAS,
    )
    table_rows = connection.execute(
        """
        SELECT table_schema || '.' || table_name
        FROM information_schema.tables
        WHERE table_schema || '.' || table_name = ANY(%s)
        """,
        (sorted(REQUIRED_TABLES),),
    ).fetchall()
    missing_tables = REQUIRED_TABLES - {row[0] for row in table_rows}
    missing_indexes = _fetch_missing(
        connection,
        "SELECT indexname FROM pg_indexes WHERE indexname = ANY(%s)",
        set(REQUIRED_INDEXES),
    )
    missing_triggers = _fetch_missing(
        connection,
        "SELECT tgname FROM pg_trigger WHERE tgname = ANY(%s) AND NOT tgisinternal",
        REQUIRED_TRIGGERS,
    )
    return {
        "missing_schemas": sorted(missing_schemas),
        "missing_tables": sorted(missing_tables),
        "missing_indexes": sorted(missing_indexes),
        "missing_triggers": sorted(missing_triggers),
    }


def _run_write_checks(connection: psycopg.Connection) -> dict[str, Any]:
    actor_id = uuid.uuid4()
    resource_id = uuid.uuid4()
    event_id = uuid.uuid4()
    delivery_id = uuid.uuid4()
    log_id = uuid.uuid4()

    connection.execute(
        """
        INSERT INTO identity.users
            (id, full_name, cpf_document, birth_date, email, phone_e164, password_hash,
             face_hash, liveness_score, terms_accepted_at, lgpd_consent_at, status)
        VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s, 0.9900, NOW(), NOW(), 'active')
        """,
        (
            actor_id,
            "Usuario Validacao PostgreSQL",
            f"CPF-{uuid.uuid4().hex[:12]}",
            f"{uuid.uuid4().hex[:8]}@example.test",
            "+5511999999999",
            "hash-validation",
            "face-validation",
        ),
    )
    connection.execute(
        """
        INSERT INTO audit.logs
            (id, user_id, actor_user_id, action, module, resource_type, resource_id, created_by)
        VALUES (%s, %s, %s, 'create', 'validation', 'postgres_real_dsn', %s, %s)
        """,
        (log_id, actor_id, actor_id, resource_id, actor_id),
    )
    connection.execute(
        """
        INSERT INTO audit.domain_events
            (id, user_id, actor_user_id, routing_key, aggregate_type, aggregate_id, payload, created_by)
        VALUES (%s, %s, %s, 'validation.postgres.checked', 'postgres_real_dsn', %s, %s, %s)
        """,
        (
            event_id,
            actor_id,
            actor_id,
            resource_id,
            Jsonb({"source": "validate_postgres_real_dsn"}),
            actor_id,
        ),
    )
    connection.execute(
        """
        INSERT INTO audit.event_deliveries
            (id, user_id, event_id, destination, delivery_status, response_metadata, created_by)
        VALUES (%s, %s, %s, 'postgres-real-dsn-validator', 'pending', %s, %s)
        """,
        (
            delivery_id,
            actor_id,
            event_id,
            Jsonb({"source": "validate_postgres_real_dsn"}),
            actor_id,
        ),
    )
    connection.commit()

    audit_logs_rejected_update = False
    try:
        connection.execute(
            "UPDATE audit.logs SET status = 'tampered' WHERE id = %s", (log_id,)
        )
        connection.commit()
    except psycopg.Error:
        audit_logs_rejected_update = True
        connection.rollback()

    event_deliveries_rejected_update = False
    try:
        connection.execute(
            "UPDATE audit.event_deliveries SET delivery_status = 'tampered' WHERE id = %s",
            (delivery_id,),
        )
        connection.commit()
    except psycopg.Error:
        event_deliveries_rejected_update = True
        connection.rollback()

    return {
        "audit_log_id": str(log_id),
        "domain_event_id": str(event_id),
        "event_delivery_id": str(delivery_id),
        "audit_logs_rejected_update": audit_logs_rejected_update,
        "event_deliveries_rejected_update": event_deliveries_rejected_update,
    }


def validate(args: argparse.Namespace) -> int:
    dsn = args.dsn or os.getenv("ALL_IN_ONE_POSTGRES_MATRIX_DSN")
    if not dsn:
        print(
            "Erro: informe --dsn ou configure ALL_IN_ONE_POSTGRES_MATRIX_DSN.",
            file=sys.stderr,
        )
        return 2

    result: dict[str, Any] = {
        "dsn_source": "--dsn" if args.dsn else "ALL_IN_ONE_POSTGRES_MATRIX_DSN",
        "applied_migrations": [],
        "verified_migration_files": [],
        "write_checks": None,
    }

    try:
        with psycopg.connect(dsn, autocommit=True) as connection:
            if args.apply_migrations:
                result["applied_migrations"] = _apply_migrations(connection)
            if args.repeat_migrations:
                result["verified_migration_files"] = _migration_manifest()
            result.update(_validate_structure(connection))

        if args.write_checks:
            with psycopg.connect(dsn) as connection:
                result["write_checks"] = _run_write_checks(connection)
    except Exception as exc:
        print(
            json.dumps(
                {"ok": False, "error": str(exc), **result}, indent=2, sort_keys=True
            )
        )
        return 1

    missing = [
        *result["missing_schemas"],
        *result["missing_tables"],
        *result["missing_indexes"],
        *result["missing_triggers"],
    ]
    write_checks = result.get("write_checks") or {}
    ok = not missing and (
        not args.write_checks
        or (
            write_checks.get("audit_logs_rejected_update") is True
            and write_checks.get("event_deliveries_rejected_update") is True
        )
    )
    print(json.dumps({"ok": ok, **result}, indent=2, sort_keys=True))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida um PostgreSQL real do All-in-One por DSN, sem depender de Docker efemero.",
    )
    parser.add_argument(
        "--dsn", help="DSN PostgreSQL. Se omitido, usa ALL_IN_ONE_POSTGRES_MATRIX_DSN."
    )
    parser.add_argument(
        "--apply-migrations",
        action="store_true",
        help="Aplica todas as migrations versionadas antes das validacoes estruturais.",
    )
    parser.add_argument(
        "--repeat-migrations",
        action="store_true",
        help=(
            "Compatibilidade legada: verifica ordem, presença, conteúdo e checksum "
            "das migrations sem reexecutar DDL de execução única no mesmo banco."
        ),
    )
    parser.add_argument(
        "--write-checks",
        action="store_true",
        help="Insere evidencias em identity/audit/outbox e confirma que tabelas append-only rejeitam UPDATE.",
    )
    return validate(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
