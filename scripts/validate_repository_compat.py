from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_VALIDATOR = ROOT / "scripts" / "validate_repository.py"
CLOUDFLARE_WORKFLOW = ROOT / ".github" / "workflows" / "cloudflare-pages.yml"

LEGACY_CLOUDFLARE_ERRORS = {
    "Workflow Cloudflare Pages deve ser idempotente e protegido por secrets: HAS_CLOUDFLARE_API_TOKEN": True,
    "Workflow Cloudflare Pages deve ser idempotente e protegido por secrets: HAS_CLOUDFLARE_ACCOUNT_ID": True,
    "Workflow Cloudflare Pages deve ser idempotente e protegido por secrets: deploy_enabled=true": True,
    "Workflow Cloudflare Pages deve ser idempotente e protegido por secrets: deploy_enabled=false": True,
    "Workflow Cloudflare Pages deve ser idempotente e protegido por secrets: if: steps.credentials.outputs.deploy_enabled == 'true'": True,
}

REQUIRED_CLOUDFLARE_MARKERS = (
    "if: ${{ vars.ENABLE_CLOUDFLARE_PAGES == 'true' }}",
    "CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}",
    "CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}",
    "VITE_API_HUB_URL: ${{ vars.VITE_API_HUB_URL }}",
    'test -n "$CLOUDFLARE_API_TOKEN"',
    'test -n "$CLOUDFLARE_ACCOUNT_ID"',
    'test -n "$VITE_API_HUB_URL"',
    "uses: actions/checkout@v7",
    "uses: cloudflare/wrangler-action@v4",
    "curl --fail --silent --show-error",
    "cloudflare-pages-production",
)

FORBIDDEN_CLOUDFLARE_MARKERS = (
    "deploy_enabled=false",
    "actions/checkout@v4",
    "actions/checkout@v6",
    "your-app-name",
)


def compatibility_exceptions() -> dict[str, bool]:
    """Compatibiliza apenas regras legadas substituídas por gates mais fortes.

    Cada exceção é literal, auditável e acompanhada por uma validação nova
    fail-closed. Nenhuma mensagem genérica é suprimida.
    """

    return dict(LEGACY_CLOUDFLARE_ERRORS)


def validate_cloudflare_pages_contract() -> list[str]:
    """Valida o contrato Cloudflare atual sem depender do validador legado."""

    if not CLOUDFLARE_WORKFLOW.is_file():
        return ["Workflow Cloudflare Pages ausente: .github/workflows/cloudflare-pages.yml"]

    workflow = CLOUDFLARE_WORKFLOW.read_text(encoding="utf-8")
    errors: list[str] = []

    for marker in REQUIRED_CLOUDFLARE_MARKERS:
        if marker not in workflow:
            errors.append(
                f"Contrato Cloudflare Pages endurecido deve conter: {marker}"
            )

    for marker in FORBIDDEN_CLOUDFLARE_MARKERS:
        if marker in workflow:
            errors.append(
                f"Contrato Cloudflare Pages não pode conter marcador legado: {marker}"
            )

    return errors


def filter_validation_errors(
    errors: list[str], exceptions: dict[str, bool]
) -> tuple[list[str], list[str]]:
    remaining: list[str] = []
    suppressed: list[str] = []
    for error in errors:
        if exceptions.get(error) is True:
            suppressed.append(error)
        else:
            remaining.append(error)
    return remaining, suppressed


def extract_errors(output: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    context: list[str] = []
    for line in output.splitlines():
        if line.startswith("- "):
            errors.append(line[2:])
        elif line.strip() != "Falhas de validacao encontradas:":
            context.append(line)
    return errors, context


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(LEGACY_VALIDATOR)],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
    errors, context = extract_errors(combined)
    remaining, suppressed = filter_validation_errors(
        errors, compatibility_exceptions()
    )
    remaining.extend(validate_cloudflare_pages_contract())

    for line in context:
        if line.strip():
            print(line)

    if suppressed:
        print("Regras legadas substituídas por contrato Cloudflare fail-closed:")
        for message in suppressed:
            print(f"- {message}")

    if remaining:
        print("Falhas de validacao encontradas:", file=sys.stderr)
        for message in remaining:
            print(f"- {message}", file=sys.stderr)
        return result.returncode or 1

    if result.returncode != 0 and not errors:
        print(
            "O validador legado falhou sem emitir mensagens reconhecíveis.",
            file=sys.stderr,
        )
        return result.returncode or 1

    print("Validacao compativel v2.9 aprovada: nenhuma falha real permaneceu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
