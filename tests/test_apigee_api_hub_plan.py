from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from scripts.configure_apigee_api_hub import expected_commands, validate_plan

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config" / "cloud" / "apigee_api_hub_plan.json"
INVENTORY = ROOT / "config" / "cloud" / "google_cloud_inventory.json"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return cast(dict[str, Any], payload)


def json_section(payload: dict[str, Any], key: str) -> dict[str, Any]:
    section = payload[key]
    assert isinstance(section, dict)
    return cast(dict[str, Any], section)


def test_apigee_api_hub_plan_uses_enabled_kms_key_from_inventory() -> None:
    plan = load_json(PLAN)
    inventory = load_json(INVENTORY)
    encryption = json_section(plan, "encryption")
    kms_key_resource = encryption["kms_key_resource"]

    assert validate_plan(plan, inventory) == []
    assert isinstance(kms_key_resource, str)
    assert kms_key_resource.endswith("/cryptoKeys/Software")
    assert encryption["secret_material_in_git"] is False


def test_apigee_api_hub_commands_include_expected_service_identity_and_roles() -> None:
    plan = load_json(PLAN)
    commands = expected_commands(plan)
    flat_commands = [" ".join(command) for command in commands]

    assert any("services identity create" in command for command in flat_commands)
    assert all("all-in-one-498012" in command for command in flat_commands)
    assert all(
        "service-864981916504@gcp-sa-apihub.iam.gserviceaccount.com" in command
        for command in flat_commands[1:]
    )
    assert any(
        "roles/cloudkms.cryptoKeyEncrypterDecrypter" in command
        for command in flat_commands
    )
    assert any("roles/apihub.admin" in command for command in flat_commands)
    assert any(
        "roles/apihub.runtimeProjectServiceAgent" in command
        for command in flat_commands
    )
    project_bindings = [
        command
        for command in flat_commands
        if "projects add-iam-policy-binding" in command
    ]
    assert project_bindings
    assert all("--condition=None" in command for command in project_bindings)
