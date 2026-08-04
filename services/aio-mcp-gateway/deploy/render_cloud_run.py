from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "deploy" / "cloud-run-service.template.yaml"
SERVICE_NAME = "aio-mcp-gateway"
IMAGE_DIGEST_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9._/-]*@sha256:[0-9a-f]{64}$"
)
PROJECT_PATTERN = re.compile(r"^[a-z][a-z0-9-]{4,28}[a-z0-9]$")
REGION_PATTERN = re.compile(r"^[a-z]+-[a-z]+[0-9]$")
SERVICE_ACCOUNT_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9-]{4,28}[a-z0-9]@"
    r"[a-z][a-z0-9-]{4,28}[a-z0-9]\.iam\.gserviceaccount\.com$"
)
REVISION_SUFFIX_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,20}$")


class DeployConfigurationError(RuntimeError):
    """Raised when deployment input is unsafe or incomplete."""


def validate_image_digest(image: str) -> str:
    normalized = image.strip().casefold()
    if not IMAGE_DIGEST_PATTERN.fullmatch(normalized):
        raise DeployConfigurationError(
            "image deve usar referência imutável no formato "
            "registry/path@sha256:<64 hex>"
        )
    return normalized


def validate_project(project: str) -> str:
    normalized = project.strip().casefold()
    if not PROJECT_PATTERN.fullmatch(normalized):
        raise DeployConfigurationError("project id inválido")
    return normalized


def validate_region(region: str) -> str:
    normalized = region.strip().casefold()
    if not REGION_PATTERN.fullmatch(normalized):
        raise DeployConfigurationError("região Cloud Run inválida")
    return normalized


def validate_service_account(value: str) -> str:
    normalized = value.strip().casefold()
    if not SERVICE_ACCOUNT_PATTERN.fullmatch(normalized):
        raise DeployConfigurationError("conta de serviço inválida")
    return normalized


def revision_name(image_digest: str, suffix: str | None) -> str:
    digest = image_digest.rsplit(":", maxsplit=1)[1]
    selected = suffix.strip().casefold() if suffix else digest[:12]
    if not REVISION_SUFFIX_PATTERN.fullmatch(selected):
        raise DeployConfigurationError("sufixo de revisão inválido")
    result = f"{SERVICE_NAME}-{selected}"
    if len(result) > 63:
        raise DeployConfigurationError("nome de revisão excede 63 caracteres")
    return result


def render_manifest(
    *,
    image_digest: str,
    service_account: str,
    revision: str,
) -> str:
    content = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "${IMAGE_DIGEST}": validate_image_digest(image_digest),
        "${SERVICE_ACCOUNT}": validate_service_account(service_account),
        "${REVISION_NAME}": revision,
    }
    for token, value in replacements.items():
        content = content.replace(token, value)
    unresolved = sorted(set(re.findall(r"\$\{[A-Z0-9_]+\}", content)))
    if unresolved:
        raise DeployConfigurationError(
            f"template contém variáveis não resolvidas: {', '.join(unresolved)}"
        )
    return content


def gcloud_command(
    *,
    manifest: Path,
    project: str,
    region: str,
) -> list[str]:
    return [
        "gcloud",
        "run",
        "services",
        "replace",
        str(manifest),
        "--project",
        validate_project(project),
        "--region",
        validate_region(region),
        "--quiet",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Renderiza o manifesto Cloud Run do AIO MCP Gateway e, "
            "opcionalmente, aplica com confirmação explícita."
        )
    )
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--service-account", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--revision-suffix")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/aio-mcp-gateway-cloud-run.yaml"),
    )
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-service", default="")
    args = parser.parse_args()

    image = validate_image_digest(args.image_digest)
    revision = revision_name(image, args.revision_suffix)
    manifest = render_manifest(
        image_digest=image,
        service_account=args.service_account,
        revision=revision,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(manifest, encoding="utf-8")
    print(f"Manifesto renderizado: {args.output}")
    print(f"Revisão: {revision}")

    command = gcloud_command(
        manifest=args.output,
        project=args.project,
        region=args.region,
    )
    if not args.apply:
        print("CHECK: " + " ".join(command))
        return 0

    if args.confirm_service != SERVICE_NAME:
        raise DeployConfigurationError(
            f"--confirm-service {SERVICE_NAME} é obrigatório para aplicar"
        )
    if shutil.which("gcloud") is None:
        raise DeployConfigurationError("gcloud não está disponível no PATH")
    subprocess.run(command, check=True, cwd=ROOT)
    print(f"Cloud Run aplicado: {SERVICE_NAME} revisão {revision}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Erro deploy MCP: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
