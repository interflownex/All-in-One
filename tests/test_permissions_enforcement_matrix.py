from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from modules.shared.domain_rules import (
    MODULE_ENTITIES,
    SENSITIVE_PERMISSION_MODULES,
    SENSITIVE_PERMISSION_ROLE_RULES,
    SENSITIVE_ROLES,
    rule_for,
)
from modules.shared.runtime import PERMISSIONS_MFA_RESOURCES, PERMISSIONS_WRITE_ROLES
from platform_test_support import client_for

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "security" / "permissions_enforcement_matrix.json"
SENSITIVE_REVIEW_PATH = (
    ROOT / "config" / "security" / "sensitive_permissions_review.json"
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return cast(dict[str, Any], payload)


def load_matrix() -> dict[str, Any]:
    return load_json(MATRIX_PATH)


def load_sensitive_review() -> dict[str, Any]:
    return load_json(SENSITIVE_REVIEW_PATH)


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


def test_permissions_matrix_links_domain_consumers_to_sensitive_runtime() -> None:
    matrix = load_matrix()
    sensitive_review = load_sensitive_review()
    domain_consumers = matrix["domain_consumers"]
    assert isinstance(domain_consumers, dict)
    modules = domain_consumers["modules"]
    assert isinstance(modules, dict)

    assert set(modules) == SENSITIVE_PERMISSION_MODULES
    assert set(modules) == set(sensitive_review["modules"])
    assert domain_consumers["source_review"] == (
        "config/security/sensitive_permissions_review.json"
    )
    assert "modules.shared.runtime._expose" in domain_consumers["runtime_entrypoints"]
    assert (
        "modules.shared.domain_rules.can_read_sensitive"
        in domain_consumers["runtime_entrypoints"]
    )

    for module_name, raw_consumer in modules.items():
        consumer = cast(dict[str, Any], raw_consumer)
        reviewed = cast(dict[str, Any], sensitive_review["modules"][module_name])
        assert consumer["runtime_rule"] == SENSITIVE_PERMISSION_ROLE_RULES[module_name]
        assert consumer["runtime_rule"] == reviewed["runtime_rule"]
        assert set(consumer["sensitive_resources"]) == set(
            reviewed["sensitive_resources"]
        )
        for resource in consumer["sensitive_resources"]:
            if resource not in MODULE_ENTITIES[module_name]:
                continue
            rule = rule_for(module_name, resource)
            assert rule.sensitive is True or rule.immutable is True


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


def test_domain_endpoint_denies_third_party_finance_read() -> None:
    client = client_for("finance")
    owner = str(uuid4())
    intruder = str(uuid4())

    created = client.post(
        "/resources/wallets",
        headers=headers(owner),
        json={"user_id": owner, "payload": {"wallet_type": "consumer"}},
    )
    assert created.status_code == 201

    denied = client.get(
        f"/resources/wallets/{created.json()['id']}",
        headers=headers(intruder),
    )
    allowed = client.get(
        f"/resources/wallets/{created.json()['id']}",
        headers=headers(intruder, "auditor"),
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_domain_endpoint_denies_third_party_identity_read() -> None:
    client = client_for("identity")
    owner = str(uuid4())
    intruder = str(uuid4())

    created = client.post(
        "/resources/users",
        headers=headers(owner),
        json={
            "user_id": owner,
            "payload": {
                "full_name": "Usuario Sensivel",
                "email": f"{uuid4().hex}@example.test",
                "password_hash": "hash-local",
            },
        },
    )
    assert created.status_code == 201

    denied = client.get(
        f"/resources/users/{created.json()['id']}",
        headers=headers(intruder),
    )
    allowed = client.get(
        f"/resources/users/{created.json()['id']}",
        headers=headers(intruder, "auditor"),
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_domain_endpoint_uses_medical_roles_for_health_sensitive_read() -> None:
    client = client_for("health")
    patient = str(uuid4())
    clinician = str(uuid4())
    auditor = str(uuid4())

    created = client.post(
        "/resources/patients",
        headers=headers(patient),
        json={"user_id": patient, "payload": {"health_identifier": uuid4().hex}},
    )
    assert created.status_code == 201

    denied = client.get(
        f"/resources/patients/{created.json()['id']}",
        headers=headers(auditor, "auditor"),
    )
    allowed = client.get(
        f"/resources/patients/{created.json()['id']}",
        headers=headers(clinician, "doctor"),
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
