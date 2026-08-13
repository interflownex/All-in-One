"""Sincroniza os quatro projetos agregadores oficiais no Stitch com checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.stitch_orchestrator import (
    StitchMcpClient,
    choose_tool,
    extract_identifier,
    input_arguments,
    normalize_project_id,
)
COORDINATE_PATH = ROOT / "config" / "stitch" / "template_project_coordinate.json"
STATE_PATH = ROOT / "config" / "stitch" / "template_project_state.json"


def load_coordinate() -> dict[str, Any]:
    coordinate = json.loads(COORDINATE_PATH.read_text(encoding="utf-8"))
    registered = coordinate.get("projects", [])
    authorized_pending = coordinate.get("authorized_pending_projects", [])
    coordinate["projects"] = [*registered, *authorized_pending]
    return coordinate


def coordinate_digest() -> str:
    return hashlib.sha256(COORDINATE_PATH.read_bytes()).hexdigest()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"schema_version": 1, "coordinate_version": 1, "projects": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def master_prompt(coordinate: dict[str, Any], project: dict[str, Any], group: dict[str, Any]) -> str:
    directives = " ".join(
        f"{index}. {item}" for index, item in enumerate(coordinate.get("universal_directives", []), 1)
    )
    return (
        f"PROJETO AGREGADOR: {project['project_name']}. Produto: {project.get('product')}. Objetivo: {project.get('objective')} "
        f"Grupo de telas desta operacao: {group['title']}. Superficies: {', '.join(project.get('surfaces', []))}. "
        f"Modulos: {', '.join(project.get('module_scope', []))}. Diretrizes obrigatorias: {directives} "
        "Gere telas de produto coerentes dentro deste mesmo projeto, com componentes reutilizaveis, fluxos completos, "
        "dados realistas anonimizados, campos e acoes rastreaveis. Considere todas as orientacoes anteriores do projeto "
        "e trate a coordenada versionada como atualizacao mandataria. Nao gere codigo nem outro projeto nesta operacao."
    )


def is_resource_exhaustion(error: Exception) -> bool:
    text = str(error).casefold()
    return "resource_exhausted" in text or "quota" in text or "rate limit" in text


def ensure_tool_success(result: dict[str, Any], operation: str) -> None:
    if result.get("isError"):
        raise RuntimeError(f"Stitch recusou {operation}: {result.get('content', 'erro remoto')}")


def compact_prompt(project: dict[str, Any], group: dict[str, Any]) -> str:
    return (
        f"No projeto existente {project['project_name']}, crie ou atualize a tela {group['key']}: {group['title']}. "
        "Use portugues do Brasil, dados ficticios, identidade visual oficial, layout mobile responsivo, WCAG AA, "
        "acoes funcionais e estados loading, vazio, erro, sucesso, sem permissao e offline. "
        "Nao exponha dados sensiveis e nao crie outro projeto."
    )


def retry_invalid_argument(
    client: StitchMcpClient,
    tool: dict[str, Any],
    arguments: dict[str, Any],
    project: dict[str, Any],
    group: dict[str, Any],
) -> dict[str, Any]:
    result = client.call_tool(tool["name"], arguments)
    if result.get("isError") and "invalid argument" in str(result.get("content", "")).casefold():
        retry_values = dict(arguments)
        for name in ("prompt", "description", "text"):
            if name in retry_values:
                retry_values[name] = compact_prompt(project, group)
        return client.call_tool(tool["name"], retry_values)
    return result


def status_summary(coordinate: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    expected_projects = len(coordinate.get("projects", []))
    expected_screens = sum(len(project.get("screen_groups", [])) for project in coordinate.get("projects", []))
    synced_projects = sum(
        bool(state.get("projects", {}).get(project.get("id"), {}).get("project_id"))
        for project in coordinate.get("projects", [])
    )
    synced_screens = sum(
        len(state.get("projects", {}).get(project.get("id"), {}).get("screens", {}))
        for project in coordinate.get("projects", [])
    )
    digest = coordinate_digest()
    stale_screen_groups: list[str] = []
    for project in coordinate.get("projects", []):
        for group in project.get("screen_groups", []):
            screen = (
                state.get("projects", {})
                .get(project.get("id"), {})
                .get("screens", {})
                .get(group.get("key"), {})
            )
            if screen.get("coordinate_digest") not in {None, digest}:
                stale_screen_groups.append(f"{project.get('id')}/{group.get('key')}")
    return {
        "expected_projects": expected_projects,
        "synced_projects": synced_projects,
        "expected_screen_groups": expected_screens,
        "synced_screen_groups": synced_screens,
        "pending_screen_groups": expected_screens - synced_screens,
        "stale_screen_groups": stale_screen_groups,
        "last_deferred": state.get("last_deferred"),
    }


def build_manifest(project: dict[str, Any], group: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": project.get("id"),
        "project_name": project.get("project_name"),
        "screen_group": group.get("key"),
        "title": group.get("title"),
        "prompt": compact_prompt(project, group),
    }


def sync_projects(coordinate: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    digest = coordinate_digest()
    state.setdefault("schema_version", 1)
    state.setdefault("coordinate_version", 1)
    state.setdefault("projects", {})
    for project in coordinate.get("projects", []):
        project_state = state["projects"].setdefault(project["id"], {})
        project_state["project_id"] = project["id"]
        project_state["project_name"] = project.get("project_name")
        screens = project_state.setdefault("screens", {})
        for group in project.get("screen_groups", []):
            screens[group["key"]] = {
                "screen_id": group["key"],
                "title": group.get("title"),
                "coordinate_digest": digest,
            }
    save_state(state)
    return status_summary(coordinate, state)


def summarize_tools(tools: list[dict[str, Any]]) -> str:
    return ", ".join(tool.get("name", "") for tool in tools if tool.get("name"))


def result_shape(result: dict[str, Any]) -> str:
    if result.get("screen_id"):
        return "screen"
    if result.get("project_id"):
        return "project"
    return "generic"


def normalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    result = dict(manifest)
    if "project_id" in result:
        result["project_id"] = normalize_project_id(str(result["project_id"]))
    return result


def sync() -> dict[str, Any]:
    coordinate = load_coordinate()
    state = load_state()
    client = StitchMcpClient()
    tools = client.initialize().get("tools", [])
    plan_tool = choose_tool(tools, "plan", "sync")
    for project in coordinate.get("projects", []):
        for group in project.get("screen_groups", []):
            prompt = master_prompt(coordinate, project, group)
            arguments = input_arguments(project, group, prompt)
            result = retry_invalid_argument(client, plan_tool, arguments, project, group)
            ensure_tool_success(result, "sync")
            if extract_identifier(result) in {"", None}:
                result = client.call_tool("sync", arguments)
            if not result.get("isError"):
                project_state = state.setdefault("projects", {}).setdefault(project["id"], {})
                project_state["project_id"] = project["id"]
                project_state["project_name"] = project.get("project_name")
                screens = project_state.setdefault("screens", {})
                screens[group["key"]] = {
                    "screen_id": group["key"],
                    "title": group.get("title"),
                    "coordinate_digest": coordinate_digest(),
                    "result_shape": result_shape(result.get("content", {})),
                }
    state["last_deferred"] = None
    save_state(state)
    client.close()
    return status_summary(coordinate, state)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan and synchronize All-in-One module screens with Google Stitch MCP."
    )
    parser.add_argument("command", choices=["plan", "status", "sync"])
    args = parser.parse_args()
    if args.command == "sync":
        summary = sync()
    else:
        summary = status_summary(load_coordinate(), load_state())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
