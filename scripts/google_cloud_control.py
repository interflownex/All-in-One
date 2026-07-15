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
PROFILE_PATH = ROOT / "config" / "cloud" / "google_cloud_profile.json"
WINDOWS_GCLOUD = Path("/mnt/c/Program Files (x86)/Google/Cloud SDK/google-cloud-sdk/bin/gcloud")
LINUX_GCLOUD = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"
DEFAULT_GCLOUD_TIMEOUT_SECONDS = 20


def load_profile() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def find_gcloud() -> str:
    override = os.getenv("GCLOUD_BIN", "").strip()
    if override:
        return override
    if LINUX_GCLOUD.is_file():
        return str(LINUX_GCLOUD)
    discovered = shutil.which("gcloud")
    if discovered and not discovered.startswith("/mnt/c/"):
        return discovered
    if WINDOWS_GCLOUD.is_file():
        return str(WINDOWS_GCLOUD)
    if discovered:
        return discovered
    raise RuntimeError("Google Cloud SDK nao encontrado.")


def gcloud_timeout_seconds() -> int:
    return int(os.getenv("GCLOUD_TIMEOUT_SECONDS", str(DEFAULT_GCLOUD_TIMEOUT_SECONDS)))


def run_gcloud_result(*args: str) -> subprocess.CompletedProcess[str] | None:
    timeout = gcloud_timeout_seconds()
    try:
        return subprocess.run(
            [find_gcloud(), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None


def run_gcloud(*args: str, check: bool = True) -> str:
    timeout = int(os.getenv("GCLOUD_TIMEOUT_SECONDS", str(DEFAULT_GCLOUD_TIMEOUT_SECONDS)))
    result = run_gcloud_result(*args)
    if result is None:
        if not check:
            return ""
        raise RuntimeError(f"gcloud excedeu {timeout}s ao executar: {' '.join(args)}")
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or f"gcloud retornou codigo {result.returncode}.")
    return result.stdout.strip()


def active_account() -> str:
    return run_gcloud("auth", "list", "--filter=status:ACTIVE", "--format=value(account)", check=False)


def adc_authenticated() -> bool:
    result = run_gcloud_result("auth", "application-default", "print-access-token")
    return bool(result and result.returncode == 0 and result.stdout.strip())


def auth_status(project: str) -> dict[str, Any]:
    try:
        gcloud_path = find_gcloud()
    except RuntimeError as exc:
        return {
            "data_agent_ready": False,
            "gcloud_found": False,
            "project": project or None,
            "warning": str(exc),
            "required_commands": [
                "gcloud auth login",
                "gcloud auth application-default login",
            ],
        }

    version_probe = run_gcloud_result("--version")
    cli_responsive = bool(version_probe and version_probe.returncode == 0)
    account = active_account() if cli_responsive else ""
    adc_ok = adc_authenticated() if cli_responsive else False
    warnings: list[str] = []
    if gcloud_path.startswith("/mnt/c/"):
        warnings.append(
            "gcloud encontrado no SDK Windows montado em /mnt/c; neste WSL ele pode exceder timeout. "
            "Prefira SDK Linux em ~/google-cloud-sdk/bin/gcloud ou defina GCLOUD_BIN."
        )
    if not cli_responsive:
        warnings.append(f"gcloud nao respondeu dentro de {gcloud_timeout_seconds()}s.")
    if cli_responsive and not account:
        warnings.append("Conta Google Cloud CLI ausente; execute gcloud auth login legitimamente.")
    if cli_responsive and not adc_ok:
        warnings.append(
            "Application Default Credentials ausente ou expirado; execute gcloud auth application-default login."
        )

    return {
        "data_agent_ready": bool(account and adc_ok),
        "gcloud_found": True,
        "gcloud_path": gcloud_path,
        "cli_responsive": cli_responsive,
        "active_account": account or None,
        "application_default_credentials": "ok" if adc_ok else "missing_or_unresponsive",
        "project": project or None,
        "warnings": warnings,
        "required_commands": [
            "gcloud auth login",
            "gcloud auth application-default login",
            "gcloud config set project all-in-one-498012",
        ],
    }


def selected_project(explicit_project: str | None, profile: dict[str, Any]) -> str:
    if explicit_project:
        return explicit_project
    environment_name = str(profile["project_environment_variable"])
    from_environment = os.getenv(environment_name, "").strip()
    if from_environment:
        return from_environment
    return run_gcloud("config", "get-value", "project", check=False).strip().replace("(unset)", "")


def resource_list(command: list[str], project: str) -> list[dict[str, Any]]:
    raw = run_gcloud(*command, f"--project={project}", "--format=json", check=False)
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return value if isinstance(value, list) else []


def status(project: str) -> dict[str, Any]:
    authenticated = bool(active_account())
    if not authenticated:
        return {
            "authenticated": False,
            "project": project or None,
            "warning": "gcloud sem conta ativa responsiva dentro do timeout.",
            "compute_terminated": [],
            "cloud_sql_stopped": [],
            "alloydb_clusters": [],
            "cloud_run_services": [],
            "gke_clusters": [],
        }
    return {
        "authenticated": authenticated,
        "project": project or None,
        "compute_terminated": resource_list(
            ["compute", "instances", "list", "--filter=status=TERMINATED"],
            project,
        )
        if project
        else [],
        "cloud_sql_stopped": resource_list(
            ["sql", "instances", "list", "--filter=settings.activationPolicy=NEVER"],
            project,
        )
        if project
        else [],
        "alloydb_clusters": resource_list(["alloydb", "clusters", "list"], project) if project else [],
        "cloud_run_services": resource_list(["run", "services", "list"], project) if project else [],
        "gke_clusters": resource_list(["container", "clusters", "list"], project) if project else [],
    }


def activate(project: str, profile: dict[str, Any]) -> dict[str, Any]:
    if not active_account():
        raise RuntimeError("gcloud sem conta ativa. Execute gcloud auth login legitimamente.")
    if not project:
        raise RuntimeError("Projeto Google Cloud ausente. Defina GOOGLE_CLOUD_PROJECT ou use --project.")

    run_gcloud("config", "set", "project", project)
    run_gcloud("config", "set", "compute/region", str(profile["default_region"]))
    run_gcloud("config", "set", "compute/zone", str(profile["default_zone"]))
    run_gcloud("services", "enable", *profile["required_apis"], f"--project={project}")

    before = status(project)
    started_compute: list[str] = []
    for instance in before["compute_terminated"]:
        name = instance.get("name")
        zone = str(instance.get("zone", "")).rsplit("/", 1)[-1]
        if name and zone:
            run_gcloud("compute", "instances", "start", str(name), f"--zone={zone}", f"--project={project}")
            started_compute.append(str(name))

    resumed_sql: list[str] = []
    for instance in before["cloud_sql_stopped"]:
        name = instance.get("name")
        if name:
            run_gcloud(
                "sql",
                "instances",
                "patch",
                str(name),
                "--activation-policy=ALWAYS",
                "--quiet",
                f"--project={project}",
            )
            resumed_sql.append(str(name))

    return {
        "project": project,
        "apis_enabled": profile["required_apis"],
        "compute_started": started_compute,
        "cloud_sql_resumed": resumed_sql,
        "alloydb_clusters_detected": len(before["alloydb_clusters"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnostica e reativa recursos Google Cloud permitidos.")
    parser.add_argument("command", choices=("status", "activate", "auth"))
    parser.add_argument("--project")
    args = parser.parse_args()
    profile = load_profile()
    if args.command == "auth":
        project = (
            args.project
            or os.getenv(str(profile["project_environment_variable"]), "").strip()
            or str(profile["authoritative_project"])
        )
    else:
        project = selected_project(args.project, profile)
    try:
        if args.command == "auth":
            result = auth_status(project)
        elif args.command == "status":
            result = status(project)
        else:
            result = activate(project, profile)
    except RuntimeError as exc:
        print(f"Falha Google Cloud: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
