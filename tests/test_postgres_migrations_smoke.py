from __future__ import annotations

import os
import socket
import subprocess
import time
import uuid
from pathlib import Path

import psycopg
import pytest

from scripts.verify_pg_indexes import REQUIRED_INDEXES


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "database" / "postgres" / "migrations"
POSTGRES_IMAGE = os.getenv("ALL_IN_ONE_POSTGRES_SMOKE_IMAGE", "postgres:16")
POSTGRES_SMOKE_ENABLED = os.getenv("ALL_IN_ONE_ENABLE_POSTGRES_SMOKE") == "1"

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
    "hr",
    "health",
    "vision",
    "legal",
    "property",
    "audit",
    "compliance",
    "api_hub",
    "bi",
    "ai_core",
    "jobs",
}

REQUIRED_TABLES = {
    "identity.users",
    "business.companies",
    "finance.wallets",
    "finance.valley_gold_ledger_entries",
    "marketplace.orders",
    "business.catalog_offers",
    "jobs.resumes",
    "audit.logs",
    "audit.domain_events",
    "compliance.retention_jobs",
}


def _docker_available() -> bool:
    result = subprocess.run(["docker", "version"], capture_output=True, text=True, check=False)
    return result.returncode == 0


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_postgres(dsn: str, timeout_seconds: int = 45) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with psycopg.connect(dsn, connect_timeout=2):
                return
        except psycopg.Error:
            time.sleep(1)
    raise RuntimeError("PostgreSQL efemero nao ficou pronto no tempo esperado.")


def _apply_all_migrations(dsn: str) -> None:
    with psycopg.connect(dsn, autocommit=True) as connection:
        for migration_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            connection.execute(migration_path.read_text(encoding="utf-8"))


@pytest.mark.skipif(
    not POSTGRES_SMOKE_ENABLED,
    reason="Smoke test de PostgreSQL efemero desativado; defina ALL_IN_ONE_ENABLE_POSTGRES_SMOKE=1 para executar.",
)
def test_postgres_migrations_apply_cleanly_on_fresh_database() -> None:
    if not _docker_available():
        pytest.skip("Docker nao disponivel para smoke test de PostgreSQL.")
    container_name = f"all-in-one-postgres-smoke-{uuid.uuid4().hex[:8]}"
    port = _free_port()
    dsn = f"postgresql://all_in_one:local-development-only@127.0.0.1:{port}/all_in_one"

    run_result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "--name",
            container_name,
            "-e",
            "POSTGRES_DB=all_in_one",
            "-e",
            "POSTGRES_USER=all_in_one",
            "-e",
            "POSTGRES_PASSWORD=local-development-only",
            "-p",
            f"127.0.0.1:{port}:5432",
            POSTGRES_IMAGE,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if run_result.returncode != 0:
        pytest.skip(f"Nao foi possivel iniciar container PostgreSQL efemero: {run_result.stderr.strip()}")

    try:
        _wait_for_postgres(dsn)
        _apply_all_migrations(dsn)

        with psycopg.connect(dsn) as connection:
            schemas = {
                row[0]
                for row in connection.execute(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = ANY(%s)",
                    (sorted(REQUIRED_SCHEMAS),),
                ).fetchall()
            }
            assert schemas == REQUIRED_SCHEMAS

            tables = {
                f"{row[0]}.{row[1]}"
                for row in connection.execute(
                    """
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE (table_schema || '.' || table_name) = ANY(%s)
                    """,
                    (sorted(REQUIRED_TABLES),),
                ).fetchall()
            }
            assert tables == REQUIRED_TABLES

            indexes = {
                row[0]
                for row in connection.execute(
                    "SELECT indexname FROM pg_indexes WHERE indexname = ANY(%s)",
                    (REQUIRED_INDEXES,),
                ).fetchall()
            }
            assert indexes == set(REQUIRED_INDEXES)

            trigger_count = connection.execute(
                "SELECT COUNT(*) FROM pg_trigger WHERE tgname = 'immutable_audit_logs' AND NOT tgisinternal"
            ).fetchone()[0]
            assert trigger_count == 1

            actor_id = uuid.uuid4()
            connection.execute(
                """
                INSERT INTO identity.users
                    (id, full_name, cpf_document, birth_date, email, phone_e164, password_hash,
                     face_hash, liveness_score, terms_accepted_at, lgpd_consent_at, status)
                VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s, 0.9900, NOW(), NOW(), 'active')
                """,
                (
                    actor_id,
                    "Usuario Smoke",
                    f"CPF-{uuid.uuid4().hex[:12]}",
                    f"{uuid.uuid4().hex[:8]}@example.test",
                    "+5511999999999",
                    "hash-smoke",
                    "face-smoke",
                ),
            )
            log_id = uuid.uuid4()
            connection.execute(
                """
                INSERT INTO audit.logs
                    (id, user_id, actor_user_id, action, module, resource_type, resource_id, created_by)
                VALUES (%s, %s, %s, 'create', 'smoke', 'migration_test', %s, %s)
                """,
                (log_id, actor_id, actor_id, uuid.uuid4(), actor_id),
            )

            with pytest.raises(psycopg.Error):
                connection.execute(
                    "UPDATE audit.logs SET status = 'tampered' WHERE id = %s",
                    (log_id,),
                )
                connection.rollback()
    finally:
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, text=True, check=False)
