#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "config" / "cloud" / "apigee_api_hub_plan.json"
INVENTORY_PATH = ROOT / "config" / "cloud" / "google_cloud_inventory.json"
WINDOWS_GCLOUD = Path(
    "/mnt/c/Program Files (x86)/Google/Cloud SDK/google-cloud-sdk/bin/gcloud"
)
LINUX_GCLOUD = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"
DEFAULT_TIMEOUT = 20


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_gcloud() -> str | None:
    override = os.getenv("GCLOUD_BIN", "").strip()
    if override:
        return override
    if LINUX_GCLOUD.exists():
        return str(LINUX_GCLOUD)
    from_path = shutil.which("gcloud")
    if from_path and not from_path.startswith("/mnt/c/"):
        return from_path
    if WINDOWS_GCLOUD.exists():
        return str(WINDOWS_GCLOUD)
    if from_path:
        return from_path
    return None


def run_command(command: list[str], timeout: int) -> dict[str, Any]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "timed_out": True,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Comando excedeu {timeout}s.",
        }
    return {
        "ok": result.returncode == 0,
        "timed_out": False,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def service_account(plan: dict[str, Any]) -> str:
    return f"serviceAccount:{plan['service_identity']['email']}"


def expected_commands(plan: dict[str, Any]) -> list[list[str]]:
    project = plan["host_project"]["project_id"]
    principal = service_account(plan)
    kms_key = plan["encryption"]["kms_key_resource"]
    return [
        [
            "gcloud",
            "beta",
            "services",
            "identity",
            "create",
            "--service=apihub.googleapis.com",
            f"--project={project}",
        ],
        [
            "gcloud",
            "kms",
            "keys",
            "add-iam-policy-binding",
            kms_key.rsplit("/", 1)[-1],
            "--keyring=Github",
            "--location=southamerica-east1",
            f"--project={project}",
            f"--member={principal}",
            "--role=roles/cloudkms.cryptoKeyEncrypterDecrypter",
        ],
        [
            "gcloud",
            "projects",
            "add-iam-policy-binding",
            project,
            f"--member={principal}",
            "--role=roles/apihub.admin",
            "--condition=None",
        ],
        [
            "gcloud",
            "projects",
            "add-iam-policy-binding",
            project,
            f"--member={principal}",
            "--role=roles/apihub.runtimeProjectServiceAgent",
            "--condition=None",
        ],
    ]


def validate_plan(plan: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    project = plan.get("host_project", {}).get("project_id")
    project_number = plan.get("host_project", {}).get("project_number")
    kms_key = plan.get("encryption", {}).get("kms_key_resource")
    allowed_keys = set(plan.get("encryption", {}).get("allowed_inventory_keys", []))
    resources = [
        item
        for item in inventory.get("authoritative_resources", [])
        if isinstance(item, dict)
    ]
    inventory_keys = {
        item.get("display_name"): item
        for item in resources
        if item.get("asset_type") == "cloudkms.googleapis.com/CryptoKey"
    }

    if project != "all-in-one-498012" or project_number != "864981916504":
        errors.append("Projeto host inesperado para Apigee API Hub.")
    if not kms_key:
        errors.append("Chave KMS obrigatoria ausente no plano.")
    elif kms_key not in allowed_keys:
        errors.append("Chave KMS nao esta na lista permitida do plano.")
    elif kms_key not in inventory_keys:
        errors.append("Chave KMS selecionada nao existe no inventario autoritativo.")
    elif inventory_keys[kms_key].get("state") != "ENABLED":
        errors.append(
            "Chave KMS selecionada nao esta ENABLED no inventario autoritativo."
        )
    expected_service_identity = (
        "service-864981916504@gcp-sa-apihub.iam.gserviceaccount.com"
    )
    if plan.get("service_identity", {}).get("email") != expected_service_identity:
        errors.append("Service identity do API Hub diverge do projeto host.")
    if plan.get("encryption", {}).get("secret_material_in_git") is not False:
        errors.append("Plano nao pode permitir material criptografico no Git.")
    return errors


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Configura/valida Apigee API Hub com KMS e IAM."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Valida o plano sem chamar gcloud.",
    )
    parser.add_argument(
        "--print-commands",
        action="store_true",
        help="Mostra comandos gcloud esperados.",
    )
    parser.add_argument(
        "--print-status",
        action="store_true",
        help="Sonda gcloud com timeout curto.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Alias de --print-status para diagnostico rapido.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Executa os comandos IAM idempotentes.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("GCLOUD_TIMEOUT_SECONDS", DEFAULT_TIMEOUT)),
    )
    args = parser.parse_args()

    plan = load_json(PLAN_PATH)
    inventory = load_json(INVENTORY_PATH)
    errors = validate_plan(plan, inventory)
    if errors:
        print_json({"ok": False, "errors": errors})
        return 1

    commands = expected_commands(plan)
    if args.print_commands:
        print_json({"ok": True, "commands": commands})
    if args.check:
        print_json(
            {
                "ok": True,
                "plan": str(PLAN_PATH),
                "kms_key": plan["encryption"]["kms_key_resource"],
            }
        )
    if args.status:
        args.print_status = True

    if args.print_status or args.apply:
        gcloud = find_gcloud()
        if not gcloud:
            print_json({"ok": False, "gcloud_found": False})
            return 1 if args.apply else 0
        probes = {
            "active_account": run_command(
                [
                    gcloud,
                    "auth",
                    "list",
                    "--filter=status:ACTIVE",
                    "--format=value(account)",
                ],
                args.timeout,
            ),
            "application_default_credentials": run_command(
                [
                    gcloud,
                    "auth",
                    "application-default",
                    "print-access-token",
                ],
                args.timeout,
            ),
            "project": run_command(
                [gcloud, "config", "get-value", "project"],
                args.timeout,
            ),
        }
        adc_probe = probes["application_default_credentials"]
        if adc_probe["ok"] and adc_probe["stdout"]:
            adc_probe = {**adc_probe, "stdout": "<redacted>"}
            probes["application_default_credentials"] = adc_probe
        if args.print_status:
            print_json(
                {
                    "ok": True,
                    "gcloud": gcloud,
                    "timeout_seconds": args.timeout,
                    "data_agent_ready": bool(
                        probes["active_account"]["ok"]
                        and adc_probe["ok"]
                        and adc_probe["stdout"]
                    ),
                    "application_default_credentials": "ok"
                    if adc_probe["ok"] and adc_probe["stdout"]
                    else "missing_or_unresponsive",
                    "probes": probes,
                    "required_commands": [
                        "gcloud auth login",
                        "gcloud auth application-default login",
                        "gcloud config set project all-in-one-498012",
                    ],
                }
            )
        if args.apply:
            results: list[dict[str, Any]] = []
            for command in commands:
                executable_command = [gcloud, *command[1:]]
                result = run_command(executable_command, args.timeout)
                results.append({"command": command, "result": result})
            all_ok = all(bool(item["result"]["ok"]) for item in results)
            print_json({"ok": all_ok, "results": results})
            return 0 if all_ok else 1
    if not any([args.check, args.print_commands, args.print_status, args.apply]):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
