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


def test_feature_status_permissions(monkeypatch, headers):
    flag = "primicia.permissions.expiring_delegation"
    monkeypatch.delenv(f"FF_{flag.upper().replace('.', '_')}", raising=False)
    client = client_for("permissions")
    resp = client.get("/delegations/feature-status", headers=headers)
    assert resp.status_code == 200, resp.text
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
