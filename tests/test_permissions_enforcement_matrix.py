from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from modules.shared.domain_rules import MODULE_ENTITIES, SENSITIVE_ROLES
from modules.shared.runtime import PERMISSIONS_MFA_RESOURCES, PERMISSIONS_WRITE_ROLES
from platform_test_support import client_for

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "security" / "permissions_enforcement_matrix.json"


def load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def headers(
    user_id: str,
    roles: str = "",
    *,
    mfa_verified: bool = False,
) -> dict[str, str]:
    return {
        "X-Actor-User-Id": user_id,
        "X-Actor-Roles": roles,
        "X-MFA-Verified": "true" if mfa_verified else "false",
    }


def role_payload(user_id: str, name: str) -> dict:
    return {
        "user_id": user_id,
        "payload": {
            "name": f"{name}_{uuid4().hex}",
            "description": "papel criado por teste de matriz RBAC",
        },
    }


def approval_limit_payload(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "payload": {
            "scope": "finance.approve.transfer",
            "limit_brl": "1000.00",
        },
    }


def test_permissions_enforcement_matrix_matches_runtime_constants() -> None:
    matrix = load_matrix()

    assert matrix["version"] == "2026-07-15"
    assert matrix["module"] == "permissions"
    assert matrix["deny_by_default"] is True
    assert set(matrix["resources"]) == set(MODULE_ENTITIES["permissions"])
    assert set(matrix["read_roles"]) == set(SENSITIVE_ROLES)
    assert set(matrix["write_roles"]) == set(PERMISSIONS_WRITE_ROLES)
    assert set(matrix["mfa_required_for_resources"]) == set(PERMISSIONS_MFA_RESOURCES)
    assert "common_user_cannot_create_role" in matrix["negative_tests"]
    assert (
        "administrator_with_mfa_can_create_approval_limit"
        in matrix["positive_tests"]
    )


def test_permissions_runtime_denies_common_user_role_management() -> None:
    client = client_for("permissions")
    actor = str(uuid4())

    denied_create = client.post(
        "/resources/roles",
        headers=headers(actor),
        json=role_payload(actor, "operador_negado"),
    )
    denied_list = client.get("/resources/roles", headers=headers(actor))

    assert denied_create.status_code == 403
    assert denied_list.status_code == 403


def test_permissions_runtime_allows_auditor_read_but_denies_write() -> None:
    client = client_for("permissions")
    admin = str(uuid4())
    auditor = str(uuid4())

    created = client.post(
        "/resources/roles",
        headers=headers(admin, "administrator"),
        json=role_payload(admin, "auditoria_readonly"),
    )
    listed = client.get("/resources/roles", headers=headers(auditor, "auditor"))
    denied_write = client.post(
        "/resources/roles",
        headers=headers(auditor, "auditor"),
        json=role_payload(auditor, "auditor_nao_escreve"),
    )

    assert created.status_code == 201
    assert listed.status_code == 200
    assert denied_write.status_code == 403


def test_permissions_approval_limits_require_mfa_for_write() -> None:
    client = client_for("permissions")
    actor = str(uuid4())

    denied = client.post(
        "/resources/approval_limits",
        headers=headers(actor, "administrator"),
        json=approval_limit_payload(actor),
    )
    allowed = client.post(
        "/resources/approval_limits",
        headers=headers(actor, "administrator", mfa_verified=True),
        json=approval_limit_payload(actor),
    )

    assert denied.status_code == 403
    assert allowed.status_code == 201
