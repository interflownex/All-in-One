"""Teste de integração leve para primícias habilitadas por módulo."""

from uuid import uuid4

import pytest

from platform_test_support import client_for


@pytest.fixture
def headers() -> dict[str, str]:
    return {
        "X-Actor-User-Id": str(uuid4()),
        "X-Actor-Roles": "administrator",
        "X-MFA-Verified": "true",
    }


def test_feature_status_all_modules(monkeypatch):
    modules = [
        ("identity", "primicia.identity.minimum_proofs"),
        ("business", "primicia.business.flash_consortium"),
        ("permissions", "primicia.permissions.expiring_delegation"),
        ("finance", "primicia.finance.earmarked_money"),
        ("marketplace", "primicia.marketplace.local_buying_coalition"),
        ("delivery", "primicia.delivery.route_capacity"),
        ("riders", "primicia.riders.evidence_passport"),
        ("services", "primicia.services.outcome_contract"),
        ("mobility", "primicia.mobility.intention_route_premium"),
        ("jobs", "primicia.jobs.reverse_availability"),
        ("erp", "primicia.erp.continuous_close"),
        ("wms", "primicia.wms.inventory_confidence"),
        ("tms", "primicia.tms.blind_capacity_exchange"),
        ("crm", "primicia.crm.customer_promises"),
        ("bpm", "primicia.bpm.process_laboratory"),
        ("document", "primicia.document.living_obligations"),
        ("hr", "primicia.hr.fair_affinity_schedule"),
        ("health", "primicia.health.continuity_capsule"),
        ("legal", "primicia.legal.impact_radar"),
        ("property", "primicia.property.shared_capacity"),
        ("bi", "primicia.bi.unasked_questions"),
        ("ai_core", "primicia.ai.memory_receipt"),
        ("api_hub", "primicia.api.adaptive_contract"),
    ]

    for module_name, flag in modules:
        monkeypatch.delenv(f"FF_{flag.upper().replace('.', '_')}", raising=False)
        client = client_for(module_name)
        resp = client.get("/feature-status")
        assert resp.status_code == 200, f"{module_name}: {resp.text}"
        data = resp.json()
        assert data["flag"] == flag
        assert data["enabled"] is False


def test_permissions_delegation_flow(headers, monkeypatch):
    monkeypatch.setenv("FF_PRIMICIA_PERMISSIONS_EXPIRING_DELEGATION", "true")
    client = client_for("permissions")

    create = client.post(
        "/delegations",
        headers=headers,
        json={
            "grantee_id": str(uuid4()),
            "purpose": "Teste integrado",
            "constraints": {
                "max_amount": 1000.0,
                "allowed_actions": ["approve_payment"],
            },
        },
    )
    assert create.status_code == 201, create.text
    payload = create.json()
    delegation_id = payload.get("delegation_id") or payload.get("id")
    assert delegation_id

    get_resp = client.get(f"/delegations/{delegation_id}", headers=headers)
    assert get_resp.status_code == 200, get_resp.text
