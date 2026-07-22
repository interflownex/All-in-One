from modules.shared.audit_contract import AuditContext, build_audit_record, build_read_audit_record, verify_audit_record
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
