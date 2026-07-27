#!/usr/bin/env python3
"""Adapta o contrato Android legado à variante explícita productionDebug."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from scripts import validate_valley_android_release as legacy
except ModuleNotFoundError:  # Execução direta a partir de scripts/.
    import validate_valley_android_release as legacy

ROOT = Path(__file__).resolve().parents[1]
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
OBSOLETE_TASKS = "testDebugUnitTest lintDebug assembleDebug"
EXPLICIT_TASKS = (
    "testProductionDebugUnitTest "
    "lintProductionDebug "
    "assembleProductionDebug"
)
OBSOLETE_ERROR = (
    ".github/workflows/security.yml: marcador obrigatorio ausente: "
    f"{OBSOLETE_TASKS}"
)


def validate_security_workflow(text: str) -> list[str]:
    errors: list[str] = []
    if EXPLICIT_TASKS not in text:
        errors.append(
            ".github/workflows/security.yml: tarefas Android explícitas "
            f"ausentes: {EXPLICIT_TASKS}"
        )
    if OBSOLETE_TASKS in text:
        errors.append(
            ".github/workflows/security.yml: tarefas Android genéricas e "
            f"ambíguas não são aceitas: {OBSOLETE_TASKS}"
        )
    return errors


def validate() -> list[str]:
    errors = [error for error in legacy.validate() if error != OBSOLETE_ERROR]
    workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")
    errors.extend(validate_security_workflow(workflow))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Contrato de release Valley v2.9 reprovado:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Contrato de release Valley v2.9 aprovado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
