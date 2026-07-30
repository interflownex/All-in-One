from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_VALIDATOR = ROOT / "scripts" / "validate_repository.py"


def compatibility_exceptions() -> dict[str, bool]:
    """Mantém o filtro fail-closed sem ocultar falhas do validador principal."""

    return {}


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

    if result.returncode == 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return 0

    combined = "\n".join(part for part in [result.stdout, result.stderr] if part)
    errors, context = extract_errors(combined)
    remaining, suppressed = filter_validation_errors(
        errors, compatibility_exceptions()
    )

    for line in context:
        if line.strip():
            print(line)

    if suppressed:
        print("Regras legadas compatibilizadas pela baseline v2.9:")
        for message in suppressed:
            print(f"- {message}")

    if remaining:
        print("Falhas de validacao encontradas:", file=sys.stderr)
        for message in remaining:
            print(f"- {message}", file=sys.stderr)
        return result.returncode or 1

    if not errors:
        print(
            "O validador legado falhou sem emitir mensagens reconheciveis.",
            file=sys.stderr,
        )
        return result.returncode or 1

    print("Validacao compativel v2.9 aprovada: nenhuma falha real permaneceu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
