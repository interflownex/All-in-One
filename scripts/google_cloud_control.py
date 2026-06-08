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


def load_profile() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def find_gcloud() -> str:
    discovered = shutil.which("gcloud")
    if discovered:
        return discovered
    if LINUX_GCLOUD.is_file():
        return str(LINUX_GCLOUD)
    if WINDOWS_GCLOUD.is_file():
        return str(WINDOWS_GCLOUD)
    raise RuntimeError("Google Cloud SDK nao encontrado.")


def run_gcloud(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        [find_gcloud(), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(detail or f"gcloud retornou codigo {result.returncode}.")
    return result.stdout.strip()


def active_account() -> str:
    return run_gcloud("auth", "list", "--filter=status:ACTIVE", "--format=value(account)", check=False)


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
    return {
        "authenticated": bool(active_account()),
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
    parser.add_argument("command", choices=("status", "activate"))
    parser.add_argument("--project")
    args = parser.parse_args()
    profile = load_profile()
    project = selected_project(args.project, profile)
    try:
        result = status(project) if args.command == "status" else activate(project, profile)
    except RuntimeError as exc:
        print(f"Falha Google Cloud: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
