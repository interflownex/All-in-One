from __future__ import annotations

import json
from pathlib import Path

from scripts.configure_apigee_api_hub import expected_commands, validate_plan


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config" / "cloud" / "apigee_api_hub_plan.json"
INVENTORY = ROOT / "config" / "cloud" / "google_cloud_inventory.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_apigee_api_hub_plan_uses_enabled_kms_key_from_inventory() -> None:
    plan = load_json(PLAN)
    inventory = load_json(INVENTORY)

    assert validate_plan(plan, inventory) == []
    assert plan["encryption"]["kms_key_resource"].endswith("/cryptoKeys/Software")
    assert plan["encryption"]["secret_material_in_git"] is False


def test_apigee_api_hub_commands_include_expected_service_identity_and_roles() -> None:
    plan = load_json(PLAN)
    commands = expected_commands(plan)
    flat_commands = [" ".join(command) for command in commands]

    assert any("services identity create" in command for command in flat_commands)
    assert all("all-in-one-498012" in command for command in flat_commands)
    assert all("service-864981916504@gcp-sa-apihub.iam.gserviceaccount.com" in command for command in flat_commands[1:])
    assert any("roles/cloudkms.cryptoKeyEncrypterDecrypter" in command for command in flat_commands)
    assert any("roles/apihub.admin" in command for command in flat_commands)
    assert any("roles/apihub.runtimeProjectServiceAgent" in command for command in flat_commands)
