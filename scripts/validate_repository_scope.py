#!/usr/bin/env python3
"""Valida a fonte única do projeto All-in-One + Valley.

Este gate impede que um repositório externo descartado volte a ser tratado como
fonte oficial e confirma que Vision permanece fora do catálogo ativo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "autonomy" / "repository_scope_policy.json"
AUTHORITATIVE_FILES = (
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "tarefas.md",
    ROOT / "docs" / "Pendências Do desenvolvedor.md",
)


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AssertionError(f"Arquivo obrigatório ausente: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise AssertionError(f"JSON inválido em {path.relative_to(ROOT)}: {exc}") from exc


def validate() -> list[str]:
    errors: list[str] = []
    policy = _load_json(POLICY_PATH)

    if policy.get("official_repository") != "interflownex/All-in-One":
        errors.append("O repositório oficial deve ser interflownex/All-in-One.")
    if policy.get("default_branch") != "main":
        errors.append("A branch padrão oficial deve ser main.")

    forbidden = tuple(str(value).lower() for value in policy.get("forbidden_repository_sources", []))
    if not forbidden:
        errors.append("A política deve declarar ao menos uma fonte de repositório proibida.")

    for path in AUTHORITATIVE_FILES:
        if not path.exists():
            errors.append(f"Documento autoritativo ausente: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token and token in text:
                errors.append(
                    f"Fonte descartada localizada em documento autoritativo: "
                    f"{path.relative_to(ROOT)}"
                )

    catalog = _load_json(ROOT / "config" / "module_catalog.json")
    serialized_catalog = json.dumps(catalog, ensure_ascii=False).lower()
    if '"vision"' in serialized_catalog:
        errors.append("Vision reapareceu no catálogo ativo.")

    tasks = (ROOT / "tarefas.md").read_text(encoding="utf-8")
    stale_markers = (
        "codex/corrigir-pendencias-relacionais-v42-20260730",
        "Pull Request central desta atividade: pendente de abertura",
        "O Pull Request `#50` permanece em rascunho e sem merge",
    )
    for marker in stale_markers:
        if marker in tasks:
            errors.append(f"Marcador de estado obsoleto localizado em tarefas.md: {marker}")

    pending = (ROOT / "docs" / "Pendências Do desenvolvedor.md").read_text(encoding="utf-8")
    for marker in stale_markers:
        if marker in pending:
            errors.append(
                "Marcador de estado obsoleto localizado em "
                f"docs/Pendências Do desenvolvedor.md: {marker}"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Falha na validação do escopo oficial:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Escopo oficial validado: interflownex/All-in-One; Valley interno; Vision inativo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
