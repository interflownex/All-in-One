from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_NAME = "aio-mcp-gateway"
REVISION_PATTERN = re.compile(r"^aio-mcp-gateway-[a-z0-9][a-z0-9-]{0,40}$")
PROJECT_PATTERN = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
REGION_PATTERN = re.compile(r"^[a-z]+-[a-z]+[0-9]$")


class RollbackConfigurationError(RuntimeError):
    """Raised when rollback input is unsafe or incomplete."""


def validate_revision(revision: str) -> str:
    normalized = revision.strip().casefold()
    if not REVISION_PATTERN.fullmatch(normalized):
        raise RollbackConfigurationError(
            "revisão deve pertencer ao serviço aio-mcp-gateway"
        )
    return normalized


def validate_project(project: str) -> str:
    normalized = project.strip().casefold()
    if not PROJECT_PATTERN.fullmatch(normalized):
        raise RollbackConfigurationError("project id inválido")
    return normalized


def validate_region(region: str) -> str:
    normalized = region.strip().casefold()
    if not REGION_PATTERN.fullmatch(normalized):
        raise RollbackConfigurationError("região Cloud Run inválida")
    return normalized


def rollback_command(
    *,
    revision: str,
    project: str,
    region: str,
) -> list[str]:
    return [
        "gcloud",
        "run",
        "services",
        "update-traffic",
        SERVICE_NAME,
        "--to-revisions",
        f"{validate_revision(revision)}=100",
        "--project",
        validate_project(project),
        "--region",
        validate_region(region),
        "--quiet",
    ]


def describe_command(
    *,
    revision: str,
    project: str,
    region: str,
) -> list[str]:
    return [
        "gcloud",
        "run",
        "revisions",
        "describe",
        validate_revision(revision),
        "--project",
        validate_project(project),
        "--region",
        validate_region(region),
        "--format=value(metadata.name)",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Valida ou aplica rollback do AIO MCP Gateway para "
            "uma revisão Cloud Run existente."
        )
    )
    parser.add_argument("--revision", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-service", default="")
    args = parser.parse_args()

    revision = validate_revision(args.revision)
    describe = describe_command(
        revision=revision,
        project=args.project,
        region=args.region,
    )
    command = rollback_command(
        revision=revision,
        project=args.project,
        region=args.region,
    )

    if not args.apply:
        print("CHECK: " + " ".join(describe))
        print("ROLLBACK: " + " ".join(command))
        return 0

    if args.confirm_service != SERVICE_NAME:
        raise RollbackConfigurationError(
            f"--confirm-service {SERVICE_NAME} é obrigatório para aplicar"
        )
    if shutil.which("gcloud") is None:
        raise RollbackConfigurationError("gcloud não está disponível no PATH")

    subprocess.run(describe, check=True, cwd=ROOT)
    subprocess.run(command, check=True, cwd=ROOT)
    print(f"Rollback aplicado: {SERVICE_NAME} -> {revision} com 100% do tráfego")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erro rollback MCP: {exc}", file=sys.stderr)
        raise SystemExit(1)
