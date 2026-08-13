"""Coordena o Google Stitch diretamente a partir do Codex."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.stitch_template_project_sync import (
    coordinate_digest,
    load_coordinate,
    load_state,
    save_state,
    status_summary,
    sync,
)

POLICY_PATH = ROOT / "config" / "autonomy" / "codex_stitch_director_policy.json"


def load_policy() -> dict[str, Any]:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def validate_policy(coordinate: dict[str, Any], state: dict[str, Any]) -> list[str]:
    policy = load_policy()
    errors: list[str] = []

    if policy.get("coordinator") != "codex":
        errors.append("A politica nao define o Codex como coordenador.")
    if policy.get("mode") != "direct_mcp":
        errors.append("A politica nao esta em modo direct_mcp.")

    official_projects = policy.get("official_projects", [])
    expected = {item.get("key"): item.get("project_id") for item in official_projects}
    coordinate_projects = {item.get("id") for item in coordinate.get("projects", [])}

    if coordinate_projects != set(expected):
        errors.append("Os projetos da coordenada nao correspondem aos quatro agregadores oficiais.")
    if len(expected) != 4:
        errors.append("A politica deve declarar exatamente quatro projetos oficiais.")
    if "aio_admin_web_mobile_template" not in expected:
        errors.append("O projeto oficial separado AIO Admin nao foi declarado.")

    for key, expected_id in expected.items():
        actual = str(state.get("projects", {}).get(key, {}).get("project_id", ""))
        if expected_id not in (None, "") and actual and actual != str(expected_id):
            errors.append(f"project_id divergente para {key}: esperado {expected_id}, obtido {actual}.")

    if '"vision"' in json.dumps(coordinate, ensure_ascii=False).casefold():
        errors.append("O modulo Vision esta inativo e nao pode constar na coordenada oficial.")

    return errors


def annotate_director_state(state: dict[str, Any], actor: str, command: str, summary: dict[str, Any]) -> None:
    state.setdefault("director", [])
    state["director"].append(
        {
            "actor": actor,
            "command": command,
            "summary": summary,
            "coordinate_digest": coordinate_digest(),
        }
    )
    save_state(state)


def require_remote_credentials() -> None:
    raise RuntimeError("sincronizacao remota legada por modulo foi desativada")


def _plan_payload(coordinate: dict[str, Any], state: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    expected_projects = [item.get("id") for item in coordinate.get("projects", [])]
    missing_projects = [
        key
        for key in expected_projects
        if not state.get("projects", {}).get(key, {}).get("project_id")
    ]
    expected_screen_groups = [
        group.get("key")
        for project in coordinate.get("projects", [])
        for group in project.get("screen_groups", [])
    ]
    pending_screen_groups = summary.get("pending_screen_groups", 0)
    return {
        "status": "complete" if not missing_projects and not pending_screen_groups else "pending",
        "expected_projects": expected_projects,
        "missing_projects": missing_projects,
        "expected_screen_groups": expected_screen_groups,
        "pending_screen_groups": pending_screen_groups,
        "synced_projects": summary.get("synced_projects", 0),
        "synced_screen_groups": summary.get("synced_screen_groups", 0),
        "stale_screen_groups": summary.get("stale_screen_groups", []),
        "coordinate_digest": coordinate_digest(),
    }


def _status_payload(coordinate: dict[str, Any], state: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    payload = dict(summary)
    payload.update(
        {
            "status": "complete"
            if summary.get("pending_screen_groups", 0) == 0 and not summary.get("stale_screen_groups")
            else "pending",
            "coordinate_digest": coordinate_digest(),
            "expected_projects": [item.get("id") for item in coordinate.get("projects", [])],
            "projects": state.get("projects", {}),
        }
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Coordena o Google Stitch diretamente a partir do Codex.")
    parser.add_argument("command", choices=["plan", "status"])
    parser.add_argument("--actor", default="codex")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-remote", action="store_true")
    args = parser.parse_args()

    if args.require_remote:
        try:
            require_remote_credentials()
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1

    coordinate = load_coordinate()
    state = load_state()
    errors = validate_policy(coordinate, state)
    summary = status_summary(coordinate, state)

    payload = _plan_payload(coordinate, state, summary) if args.command == "plan" else _status_payload(coordinate, state, summary)
    annotate_director_state(state, args.actor, args.command, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)

    if args.require_complete and (errors or payload.get("status") != "complete"):
        return 1
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
