import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "compliance" / "access_control.v1.json"


def _load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_access_control_contract_is_fail_closed() -> None:
    contract = _load_contract()

    assert contract["default_effect"] == "deny"
    assert contract["database_contract"]["missing_context_denies_access"] is True
    assert contract["database_contract"]["cross_tenant_access_denied"] is True
    assert contract["database_contract"]["force_row_level_security"] is True
    assert contract["privileged_access"]["bypass_rls_allowed"] is False


def test_access_control_contract_requires_complete_session_context() -> None:
    contract = _load_contract()
    context = contract["session_context"]

    assert set(context) == {
        "tenant_id",
        "subject_id",
        "subject_type",
        "purpose",
        "request_id",
    }
    assert all(item["required"] is True for item in context.values())
    assert context["tenant_id"]["setting"] == "app.tenant_id"
    assert context["subject_id"]["setting"] == "app.subject_id"
    assert context["purpose"]["setting"] == "app.processing_purpose"


def test_privileged_access_is_bounded_and_audited() -> None:
    privileged = _load_contract()["privileged_access"]

    assert privileged["support_requires_ticket"] is True
    assert privileged["support_requires_expiry"] is True
    assert privileged["break_glass_requires_incident"] is True
    assert 0 < privileged["break_glass_max_minutes"] <= 60
    assert privileged["audit_event_required"] is True
