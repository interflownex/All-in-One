#!/usr/bin/env python3
"""Coordena o Google Stitch diretamente a partir do Codex.

Este é o único ponto de escrita remota autorizado para a trilha oficial de
templates. As coordenadas e checkpoints permanecem versionados no Git; as
credenciais permanecem fora do repositório.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.stitch_template_project_sync import (  # noqa: E402
    coordinate_digest,
    load_coordinate,
    load_state,
    save_state,
    status_summary,
    sync as sync_template_projects,
)

POLICY_PATH = ROOT / "config" / "autonomy" / "codex_stitch_director_policy.json"


def load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def validate_policy(coordinate: dict[str, Any], state: dict[str, Any]) -> list[str]:
    policy = load_policy()
    errors: list[str] = []

    if policy.get("coordinator") != "codex":
        errors.append("A política não define o Codex como coordenador.")
    if policy.get("mode") != "direct_mcp":
        errors.append("A política não está em modo direct_mcp.")

    expected = {
        item["key"]: str(item["project_id"])
        for item in policy.get("official_projects", [])
    }
    coordinate_projects = {item["id"] for item in coordinate.get("projects", [])}
    if coordinate_projects != set(expected):
        errors.append(
            "Os projetos da coordenada não correspondem aos três agregadores oficiais."
        )

    for key, expected_id in expected.items():
        actual = str(
            state.get("projects", {}).get(key, {}).get("project_id", "")
        )
        if actual and actual != expected_id:
            errors.append(
                f"project_id divergente para {key}: esperado {expected_id}, obtido {actual}."
            )

    return errors


def annotate_director_state(
    state: dict[str, Any], *, actor: str, command: str, summary: dict[str, Any]
) -> None:
    state["last_director"] = {
        "coordinator": "codex",
        "actor": actor,
        "command": command,
        "coordinate_digest": coordinate_digest(),
        "recorded_at": datetime.now(UTC).isoformat(),
        "summary": summary,
    }
    save_state(state)


def require_remote_credentials() -> None:
    if not (os.getenv("STITCH_API_KEY") or os.getenv("STITCH_ACCESS_TOKEN")):
        raise RuntimeError(
            "Coordenação remota exige STITCH_API_KEY ou STITCH_ACCESS_TOKEN fora do Git."
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diretor Codex para coordenação direta dos templates oficiais no Stitch."
    )
    parser.add_argument("command", choices=("plan", "status", "sync"))
    parser.add_argument("--max-operations", type=int, default=8)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--allow-create-missing-projects", action="store_true")
    parser.add_argument(
        "--actor", default=os.getenv("CODEX_AGENT_ID", "codex"), help="Identidade do agente."
    )
    args = parser.parse_args()

    if args.max_operations < 1:
        parser.error("--max-operations deve ser maior que zero")

    coordinate = load_coordinate()
    state = load_state()
    errors = validate_policy(coordinate, state)
    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    missing_projects = [
        project["id"]
        for project in coordinate["projects"]
        if not state.get("projects", {}).get(project["id"], {}).get("project_id")
    ]

    if args.command == "plan":
        print(
            json.dumps(
                {
                    "coordinator": "codex",
                    "mode": "direct_mcp",
                    "coordinate_digest": coordinate_digest(),
                    "official_projects": len(coordinate["projects"]),
                    "screen_groups": sum(
                        len(project["screen_groups"])
                        for project in coordinate["projects"]
                    ),
                    "missing_projects": missing_projects,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "sync":
        require_remote_credentials()
        if missing_projects and not args.allow_create_missing_projects:
            raise RuntimeError(
                "Há projeto oficial sem project_id registrado. A criação remota exige "
                "--allow-create-missing-projects e autorização explícita."
            )
        state = sync_template_projects(args.max_operations)

    summary = status_summary(coordinate, state)
    if args.command == "sync":
        annotate_director_state(
            state,
            actor=args.actor,
            command=args.command,
            summary=summary,
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.require_complete and (
        summary["synced_projects"] != summary["expected_projects"]
        or summary["pending_screen_groups"]
        or summary["stale_screen_groups"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
