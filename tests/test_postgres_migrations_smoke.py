from __future__ import annotations

import json
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
    "delivery.rider_documents",
    "delivery.rider_reviews",
    "marketplace.orders",
    "business.catalog_offers",
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


def _docker_available() -> bool:
    result = subprocess.run(
        ["docker", "version"], capture_output=True, text=True, check=False
    )
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


def _inspect_container_state(container_name: str) -> dict[str, object] | None:
    result = subprocess.run(
        ["docker", "inspect", container_name, "--format", "{{json .State}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        return {"raw": result.stdout.strip()}


def _wait_for_container_running(
    container_name: str, timeout_seconds: int = 20
) -> dict[str, object]:
    deadline = time.time() + timeout_seconds
    last_state: dict[str, object] | None = None
    while time.time() < deadline:
        state = _inspect_container_state(container_name)
        if state is not None:
            last_state = state
            if state.get("Running") is True and state.get("Status") == "running":
                return state
        time.sleep(1)
    raise RuntimeError(
        f"Container PostgreSQL efemero nao entrou em estado running: {last_state}"
    )


def _docker_logs(container_name: str) -> str:
    result = subprocess.run(
        ["docker", "logs", "--tail", "200", container_name],
        capture_output=True,
        text=True,
        check=False,
    )
    material = (result.stdout or "") + (result.stderr or "")
    return material.strip()


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

    try:
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
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        pytest.skip(
            "Docker demorou demais para responder ao iniciar o PostgreSQL efemero."
        )
    if run_result.returncode != 0:
        pytest.skip(
            f"Nao foi possivel iniciar container PostgreSQL efemero: {run_result.stderr.strip()}"
        )

    try:
        try:
            _wait_for_container_running(container_name)
        except RuntimeError as exc:
            logs = _docker_logs(container_name)
            detail = f"{exc}; logs={logs[:400]}" if logs else str(exc)
            pytest.skip(
                f"Docker nao deixou o container PostgreSQL efemero operacional: {detail}"
            )

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

            triggers = {
                row[0]
                for row in connection.execute(
                    "SELECT tgname FROM pg_trigger WHERE tgname = ANY(%s) AND NOT tgisinternal",
                    (sorted(REQUIRED_TRIGGERS),),
                ).fetchall()
            }
            assert triggers == REQUIRED_TRIGGERS

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
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            text=True,
            check=False,
        )
