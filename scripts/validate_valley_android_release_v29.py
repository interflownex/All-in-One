#!/usr/bin/env python3
"""Adapta contratos legados do release Android às versões atuais."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from scripts import validate_valley_android_release as legacy
except ModuleNotFoundError:  # Execução direta a partir de scripts/.
    import validate_valley_android_release as legacy

ROOT = Path(__file__).resolve().parents[1]
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "valley-android-release.yml"
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"
OBSOLETE_TASKS = "testDebugUnitTest lintDebug assembleDebug"
EXPLICIT_TASKS = (
    "testProductionDebugUnitTest "
    "lintProductionDebug "
    "assembleProductionDebug"
)
OBSOLETE_UPLOAD_ACTION = "actions/upload-artifact@v4"
CURRENT_UPLOAD_ACTION = "actions/upload-artifact@v7"
OBSOLETE_ATTEST_ACTION = "actions/attest-build-provenance@v2"
CURRENT_ATTEST_ACTION = "actions/attest-build-provenance@v4"
OBSOLETE_ERROR = (
    ".github/workflows/security.yml: marcador obrigatorio ausente: "
    f"{OBSOLETE_TASKS}"
)
OBSOLETE_UPLOAD_ERROR = (
    ".github/workflows/valley-android-release.yml: marcador obrigatorio ausente: "
    f"{OBSOLETE_UPLOAD_ACTION}"
)
OBSOLETE_ATTEST_ERROR = (
    ".github/workflows/valley-android-release.yml: marcador obrigatorio ausente: "
    f"{OBSOLETE_ATTEST_ACTION}"
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


def validate_release_workflow(text: str) -> list[str]:
    errors: list[str] = []
    if CURRENT_UPLOAD_ACTION not in text:
        errors.append(
            ".github/workflows/valley-android-release.yml: ação atual de "
            f"publicação ausente: {CURRENT_UPLOAD_ACTION}"
        )
    if OBSOLETE_UPLOAD_ACTION in text:
        errors.append(
            ".github/workflows/valley-android-release.yml: ação obsoleta de "
            f"publicação não é aceita: {OBSOLETE_UPLOAD_ACTION}"
        )
    if CURRENT_ATTEST_ACTION not in text:
        errors.append(
            ".github/workflows/valley-android-release.yml: ação atual de "
            f"atestação ausente: {CURRENT_ATTEST_ACTION}"
        )
    if OBSOLETE_ATTEST_ACTION in text:
        errors.append(
            ".github/workflows/valley-android-release.yml: ação obsoleta de "
            f"atestação não é aceita: {OBSOLETE_ATTEST_ACTION}"
        )
    return errors


def validate() -> list[str]:
    ignored_legacy_errors = {
        OBSOLETE_ERROR,
        OBSOLETE_UPLOAD_ERROR,
        OBSOLETE_ATTEST_ERROR,
    }
    errors = [
        error for error in legacy.validate() if error not in ignored_legacy_errors
    ]
    security_workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")
    release_workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    errors.extend(validate_security_workflow(security_workflow))
    errors.extend(validate_release_workflow(release_workflow))
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