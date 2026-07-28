from modules.shared.audit_contract import (
    AuditContext,
    build_audit_record,
    normalize_audit_ip_address,
)


def test_normalize_audit_ip_address_accepts_ipv4_and_ipv6() -> None:
    assert normalize_audit_ip_address(" 127.0.0.1 ") == "127.0.0.1"
    assert normalize_audit_ip_address("2001:0db8::1") == "2001:db8::1"


def test_normalize_audit_ip_address_rejects_symbolic_hosts() -> None:
    assert normalize_audit_ip_address("testclient") is None
    assert normalize_audit_ip_address("") is None
    assert normalize_audit_ip_address(None) is None


def test_build_audit_record_drops_symbolic_host_from_inet_and_metadata() -> None:
    record = build_audit_record(
        module="jobs",
        actor_user_id="00000000-0000-0000-0000-000000000001",
        action="create",
        resource_type="resume",
        resource_id="00000000-0000-0000-0000-000000000002",
        context=AuditContext(ip_address="testclient"),
    )

    assert record["ip_address"] is None
    assert record["metadata"]["context"]["ip_address"] is None


def test_build_audit_record_preserves_valid_network_address() -> None:
    record = build_audit_record(
        module="jobs",
        actor_user_id="00000000-0000-0000-0000-000000000001",
        action="create",
        resource_type="resume",
        resource_id="00000000-0000-0000-0000-000000000002",
        context=AuditContext(ip_address="::1"),
    )

    assert record["ip_address"] == "::1"
    assert record["metadata"]["context"]["ip_address"] == "::1"
