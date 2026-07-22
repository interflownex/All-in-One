from pathlib import Path

from modules.shared.audit_contract import (
    AuditContext, build_audit_record, build_read_audit_record, insert_postgres_audit,
    set_audit_context, verify_audit_record,
)
from modules.shared.correlation import set_correlation_id
from modules.shared.store import SQLiteStore


def test_unified_audit_contract_covers_context_integrity_and_retention() -> None:
    set_correlation_id("00000000-0000-0000-0000-000000000100")
    record = build_audit_record(
        module="business", actor_user_id="actor", action="update", resource_type="companies",
        resource_id="company", before={"name": "Antes", "password": "segredo"},
        after={"name": "Depois", "token": "segredo"},
        context=AuditContext(
            tenant_id="tenant", company_id="company", actor_role="administrator", session_id="session",
            device_id="device", ip_address="127.0.0.1", user_agent="pytest", origin="web", channel="browser",
            reason="Correção cadastral", authorization="business:write",
        ),
        occurred_at="2026-07-21T12:00:00+00:00",
    )

    assert record["before_data"]["password"] == "[REDACTED]"
    assert record["after_data"]["token"] == "[REDACTED]"
    assert record["changed_fields"] == ["name", "password", "token"]
    assert record["correlation_id"] == "00000000-0000-0000-0000-000000000100"
    assert record["retention_until"] == "2033-07-19T12:00:00+00:00"
    assert verify_audit_record(record)
    record["result"] = "failure"
    assert not verify_audit_record(record)


def test_sensitive_read_contract_records_purpose_authorization_and_outputs() -> None:
    record = build_read_audit_record(
        module="health", actor_user_id="doctor", resource_type="medical_records", resource_id="record",
        purpose="Atendimento assistencial", context=AuditContext(authorization="health:records:read"),
        exported=True, printed=False, shared=False,
    )

    assert record["action"] == "sensitive_read"
    assert record["log_type"] == "security"
    assert record["after_data"] == {
        "purpose": "Atendimento assistencial", "exported": True, "printed": False, "shared": False,
    }
    assert verify_audit_record(record)


def test_sqlite_store_persists_a_hash_chained_append_only_contract() -> None:
    store = SQLiteStore("business")
    first = store.audit_external("actor", "read", "companies", "one", {"name": "Empresa"})
    second = store.audit_external("actor", "update", "companies", "one", {"name": "Nova"})
    rows = store.audit_log()

    assert first["row_hash"]
    assert second["previous_hash"] == first["row_hash"]
    assert rows[0]["event"] == "business.update"
    assert rows[0]["row_hash"] == second["row_hash"]
    assert rows[1]["event"] == "business.read"


def test_postgres_writer_persists_the_full_request_context() -> None:
    calls: list[tuple[str, tuple | None]] = []

    class Result:
        def __init__(self, row): self.row = row
        def fetchone(self): return self.row

    class Connection:
        def execute(self, query, params=None):
            calls.append((str(query), params))
            return Result(None if query.startswith("SELECT") else {"id": "audit-id", "row_hash": params[36]})

    set_audit_context(AuditContext(
        tenant_id="00000000-0000-0000-0000-000000000001", actor_role="doctor",
        session_id="session", device_id="device", ip_address="127.0.0.1", user_agent="pytest",
        origin="web", channel="web", reason="Atendimento", authorization="health:records:read",
    ))
    evidence = insert_postgres_audit(
        Connection(), module="health", actor_user_id="actor", action="sensitive_read",
        resource_type="patients", resource_id="patient", before=None,
        after={"purpose": "Atendimento", "exported": True}, user_id="patient", company_id=None,
    )

    insert_sql, parameters = calls[1]
    assert "session_id" in insert_sql and "retention_until" in insert_sql
    assert parameters is not None and len(parameters) == 40
    assert parameters[10:14] == ("session", "device", "127.0.0.1", "pytest")
    assert parameters[32:35] == (True, False, False)
    assert evidence["row_hash"] == parameters[36]


def test_specialized_postgres_stores_do_not_bypass_the_unified_writer() -> None:
    root = Path(__file__).resolve().parents[1] / "modules" / "shared"
    specialized = (
        "api_hub", "business", "delivery", "finance", "marketplace", "mobility", "services",
    )
    for module in specialized:
        source = (root / f"{module}_postgres_store.py").read_text(encoding="utf-8")
        assert "insert_postgres_audit" in source
        assert "INSERT INTO audit.logs" not in source
