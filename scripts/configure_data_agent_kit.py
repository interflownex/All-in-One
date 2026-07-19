#!/usr/bin/env python3
"""Valida e prepara a configuracao persistente do Google Cloud Data Agent Kit."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/autonomy/data_agent_kit_policy.json"
PROFILE = ROOT / "config/cloud/google_cloud_profile.json"
EXTENSIONS = ROOT / ".vscode/extensions.json"
SETTINGS = ROOT / ".vscode/settings.json"
LINUX_GCLOUD = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    policy = load_json(POLICY)
    profile = load_json(PROFILE)
    extensions = load_json(EXTENSIONS)
    settings = load_json(SETTINGS)

    if not policy.get("enabled"):
        errors.append("Data Agent Kit deve permanecer habilitado.")
    starter = policy.get("starter_pack", {})
    if starter.get("version") != "0.6.1":
        errors.append("Versao homologada do starter pack deve ser 0.6.1.")
    if starter.get("vscode_extension") not in extensions.get("recommendations", []):
        errors.append("Extensao oficial do Data Agent Kit ausente das recomendacoes do VS Code.")
    defaults = policy.get("defaults", {})
    expected_settings = {
        "google.cloud.project": defaults.get("project_id"),
        "google.cloud.billingQuotaProject": defaults.get("project_id"),
        "google.cloud.region": defaults.get("region"),
        "google.datacloud.bigqueryRegion": defaults.get("bigquery_location"),
        "google.datacloud.composer.project": defaults.get("project_id"),
        "google.datacloud.composer.region": defaults.get("region"),
        "google.datacloud.agent.skills.autoUpdate": True,
        "google.datacloud.agent.skills.installLocation": "workspace",
        "google.datacloud.executeCellToolForNotebookMCP": False,
        "google.datacloud.executeCellToolConsent": True,
    }
    for key, expected in expected_settings.items():
        if settings.get(key) != expected:
            errors.append(f"Configuracao persistente invalida para {key}: esperado {expected!r}.")
    expected_environment = {
        "DATA_AGENT_KIT_ENABLED": "true",
        defaults.get("project_environment_variable"): defaults.get("project_id"),
        defaults.get("region_environment_variable"): defaults.get("region"),
        defaults.get("bigquery_location_environment_variable"): defaults.get("bigquery_location"),
    }
    for terminal_key in ("terminal.integrated.env.linux", "terminal.integrated.env.windows"):
        environment = settings.get(terminal_key, {})
        for key, expected in expected_environment.items():
            if environment.get(key) != expected:
                errors.append(f"Variavel persistente ausente ou invalida em {terminal_key}: {key}.")
    missing_apis = sorted(set(policy.get("required_apis", [])) - set(profile.get("required_apis", [])))
    if missing_apis:
        errors.append("APIs do Data Agent Kit ausentes do perfil Google Cloud: " + ", ".join(missing_apis))
    security = policy.get("security", {})
    if not security.get("credentials_outside_git") or security.get("allow_destructive_data_operations"):
        errors.append("Politica de seguranca do Data Agent Kit invalida.")
    return errors


def runtime_status() -> dict:
    policy = load_json(POLICY)
    defaults = policy["defaults"]
    project = os.environ.get(defaults["project_environment_variable"], defaults["project_id"])
    region = os.environ.get(defaults["region_environment_variable"], defaults["region"])
    location = os.environ.get(defaults["bigquery_location_environment_variable"], defaults["bigquery_location"])
    gcloud = str(LINUX_GCLOUD) if LINUX_GCLOUD.is_file() else shutil.which("gcloud")
    adc = False
    runtime_warning = None
    if gcloud:
        try:
            result = subprocess.run(
                [gcloud, "auth", "application-default", "print-access-token"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=20,
            )
            adc = result.returncode == 0
        except subprocess.TimeoutExpired:
            runtime_warning = "gcloud excedeu 20s ao verificar Application Default Credentials."
    return {
        "enabled": policy["enabled"],
        "version": policy["starter_pack"]["version"],
        "project": project,
        "region": region,
        "bigquery_location": location,
        "gcloud_available": bool(gcloud),
        "gcloud_path": gcloud,
        "application_default_credentials_available": adc,
        "runtime_warning": runtime_warning,
        "vscode_extension": policy["starter_pack"]["vscode_extension"],
        "codex_plugin": policy["starter_pack"]["codex_plugin"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-runtime", action="store_true", help="Inclui diagnostico local de gcloud e ADC.")
    args = parser.parse_args()
    errors = validate()
    if errors:
        print("Falhas na configuracao do Data Agent Kit:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Configuracao persistente do Data Agent Kit validada.")
    if args.check_runtime:
        print(json.dumps(runtime_status(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
