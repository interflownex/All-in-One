"""Testes das primícias – Recurso 3: Procuração Operacional Expirável."""

from uuid import uuid4

import pytest


def _headers(roles: str = "administrator", mfa: str = "true") -> dict[str, str]:
    return {
        "X-Actor-User-Id": str(uuid4()),
        "X-Actor-Roles": roles,
        "X-MFA-Verified": mfa,
    }


@pytest.fixture(autouse=True)
def enable_flag(monkeypatch):
    monkeypatch.setenv("FF_PRIMICIA_PERMISSIONS_EXPIRING_DELEGATION", "true")


def test_flag_off_returns_402(monkeypatch):
    """Feature flag desligada retorna 402."""
    monkeypatch.delenv("FF_PRIMICIA_PERMISSIONS_EXPIRING_DELEGATION", raising=False)
    from platform_test_support import client_for

    client = client_for("permissions")
    headers = _headers()
    resp = client.post(
        "/delegations",
        headers=headers,
        json={"grantee_id": str(uuid4()), "purpose": "teste"},
    )
    assert resp.status_code == 402, resp.text
    data = resp.json()
    assert data["detail"]["code"] == "FEATURE_NOT_ENABLED"


def test_create_delegation_success():
    """Cria procuração com restrições válidas."""
    from platform_test_support import client_for

    client = client_for("permissions")
    grantor = str(uuid4())
    grantee = str(uuid4())
    headers = {
        "X-Actor-User-Id": grantor,
        "X-Actor-Roles": "administrator",
        "X-MFA-Verified": "true",
    }
    resp = client.post(
        "/delegations",
        headers=headers,
        json={
            "grantee_id": grantee,
            "purpose": "Aprovação de pagamentos até R$ 1.000",
            "constraints": {
                "max_amount": 1000.0,
                "allowed_actions": ["approve_payment"],
                "single_use": False,
            },
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] in {"pending", "draft", "active"}


def test_create_delegation_requires_fields():
    """Campos obrigatórios ausentes retornam 422."""
    from platform_test_support import client_for

    client = client_for("permissions")
    headers = _headers()
    resp = client.post("/delegations", headers=headers, json={"purpose": "sem grantee"})
    assert resp.status_code == 422, resp.text


def test_max_amount_must_be_positive():
    """max_amount negativo retorna 422."""
    from platform_test_support import client_for

    client = client_for("permissions")
    headers = _headers()
    resp = client.post(
        "/delegations",
        headers=headers,
        json={
            "grantee_id": str(uuid4()),
            "purpose": "teste",
            "constraints": {"max_amount": -100.0},
        },
    )
    assert resp.status_code == 422, resp.text


def test_valid_until_before_valid_from_rejected():
    """Período inválido retorna 422."""
    from platform_test_support import client_for

    client = client_for("permissions")
    headers = _headers()
    resp = client.post(
        "/delegations",
        headers=headers,
        json={
            "grantee_id": str(uuid4()),
            "purpose": "teste",
            "constraints": {
                "valid_from": "2026-12-31T00:00:00Z",
                "valid_until": "2026-01-01T00:00:00Z",
            },
        },
    )
    assert resp.status_code == 422, resp.text


def test_feature_status_endpoint():
    """Endpoint de status da feature retorna dados corretos."""
    from platform_test_support import client_for

    client = client_for("permissions")
    headers = _headers()
    resp = client.get("/delegations/feature-status", headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["flag"] == "primicia.permissions.expiring_delegation"
    assert data["enabled"] is True
