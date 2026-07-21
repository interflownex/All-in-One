#!/usr/bin/env python3
"""Sincroniza os três projetos agregadores de template no Stitch com checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
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
    return json.loads(COORDINATE_PATH.read_text(encoding="utf-8"))


def coordinate_digest() -> str:
    return hashlib.sha256(COORDINATE_PATH.read_bytes()).hexdigest()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"schema_version": 1, "coordinate_version": 1, "projects": {}}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def master_prompt(coordinate: dict[str, Any], project: dict[str, Any], group: dict[str, str]) -> str:
    directives = " ".join(f"{index}. {item}" for index, item in enumerate(coordinate["universal_directives"], 1))
    return (
        f"PROJETO AGREGADOR: {project['project_name']}. Produto: {project['product']}. "
        f"Objetivo: {project['objective']} Grupo de telas desta operacao: {group['title']}. "
        f"Superficies: {', '.join(project['surfaces'])}. Modulos: {', '.join(project['module_scope'])}. "
        f"Diretrizes obrigatorias: {directives} "
        "Gere telas de produto coerentes dentro deste mesmo projeto, com componentes reutilizaveis, fluxos completos, "
        "dados realistas anonimizados, campos e acoes rastreaveis. Considere todas as orientacoes anteriores do projeto "
        "e trate a coordenada versionada como atualizacao mandataria. Nao gere codigo nem outro projeto nesta operacao."
    )


def is_resource_exhaustion(error: Exception) -> bool:
    return bool(re.search(r"resource.?exhausted|quota|rate.?limit|token|too many requests|429", str(error), re.I))


def ensure_tool_success(result: dict[str, Any], operation: str) -> None:
    if result.get("isError"):
        raise RuntimeError(f"Stitch recusou {operation}: {result.get('content', 'erro remoto')}")


def compact_prompt(project: dict[str, Any], group: dict[str, str]) -> str:
    return (
        f"No projeto existente {project['project_name']}, crie ou atualize a tela {group['key']}: {group['title']}. "
        "Use português do Brasil, dados fictícios, identidade visual oficial, layout mobile responsivo, WCAG AA, "
        "ações funcionais e estados loading, vazio, erro, sucesso, sem permissão e offline. "
        "Não exponha dados sensíveis e não crie outro projeto."
    )


def retry_invalid_argument(client: StitchMcpClient, tool: dict[str, Any], arguments: dict[str, Any], project: dict[str, Any], group: dict[str, str]) -> dict[str, Any]:
    result = client.call_tool(tool["name"], arguments)
    if result.get("isError") and "invalid argument" in str(result.get("content", "")).casefold():
        retry_values = dict(arguments)
        for name in ("prompt", "description", "text"):
            if name in retry_values:
                retry_values[name] = compact_prompt(project, group)
                break
        return client.call_tool(tool["name"], retry_values)
    return result


def status_summary(coordinate: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    expected_projects = len(coordinate["projects"])
    expected_screens = sum(len(project["screen_groups"]) for project in coordinate["projects"])
    synced_projects = sum(bool(state.get("projects", {}).get(project["id"], {}).get("project_id")) for project in coordinate["projects"])
    synced_screens = sum(
        len(state.get("projects", {}).get(project["id"], {}).get("screens", {}))
        for project in coordinate["projects"]
    )
    digest = coordinate_digest()
    stale = [
        f"{project['id']}/{group['key']}"
        for project in coordinate["projects"]
        for group in project["screen_groups"]
        if state.get("projects", {}).get(project["id"], {}).get("screens", {}).get(group["key"], {}).get("coordinate_digest") not in {None, digest}
    ]
    return {
        "expected_projects": expected_projects, "synced_projects": synced_projects,
        "expected_screen_groups": expected_screens, "synced_screen_groups": synced_screens,
        "pending_screen_groups": expected_screens - synced_screens, "stale_screen_groups": stale,
        "last_deferred": state.get("last_deferred"),
    }


def sync(max_operations: int) -> dict[str, Any]:
    coordinate = load_coordinate()
    state = load_state()
    digest = coordinate_digest()
    operations = 0
    client = StitchMcpClient()
    try:
        client.initialize()
        tools = client.tools()
        create_project = choose_tool(tools, ("create_project", "new_project"))
        generate_screen = choose_tool(tools, ("generate_screen", "create_screen"))
        edit_screen = choose_tool(tools, ("edit_screens", "edit_screen"))
        for project in coordinate["projects"]:
            project_state = state["projects"].setdefault(project["id"], {"screens": {}})
            if not project_state.get("project_id"):
                result = client.call_tool(create_project["name"], input_arguments(create_project, {"name": project["project_name"]}))
                ensure_tool_success(result, f"criação de {project['id']}")
                identifier = extract_identifier(result, ("projectId", "project_id", "name", "id"))
                if not identifier:
                    raise RuntimeError(f"Stitch não retornou project_id para {project['id']}.")
                project_state["project_id"] = normalize_project_id(identifier)
                project_state["project_name"] = project["project_name"]
                save_state(state)
                operations += 1
                if operations >= max_operations:
                    return state
            for group in project["screen_groups"]:
                screen_state = project_state["screens"].get(group["key"])
                prompt = master_prompt(coordinate, project, group)
                if screen_state and screen_state.get("coordinate_digest") == digest:
                    continue
                if screen_state:
                    edit_arguments = input_arguments(edit_screen, {"project_id": project_state["project_id"], "prompt": prompt, "selected_screen_ids": [screen_state["screen_id"]]})
                    result = retry_invalid_argument(client, edit_screen, edit_arguments, project, group)
                    ensure_tool_success(result, f"atualização de {project['id']}/{group['key']}")
                else:
                    generate_arguments = input_arguments(generate_screen, {"project_id": project_state["project_id"], "prompt": prompt})
                    result = retry_invalid_argument(client, generate_screen, generate_arguments, project, group)
                    ensure_tool_success(result, f"geração de {project['id']}/{group['key']}")
                    screen_id = extract_identifier(result, ("screenId", "screen_id", "name", "sessionId", "session_id", "id"))
                    if not screen_id:
                        raise RuntimeError(f"Stitch não retornou screen_id para {project['id']}/{group['key']}.")
                    screen_state = {"screen_id": screen_id}
                    project_state["screens"][group["key"]] = screen_state
                screen_state.update({"title": group["title"], "coordinate_digest": digest, "updated_at": datetime.now(timezone.utc).isoformat()})
                state.pop("last_deferred", None)
                save_state(state)
                operations += 1
                if operations >= max_operations:
                    return state
        return state
    except Exception as error:
        if not is_resource_exhaustion(error):
            raise
        state["last_deferred"] = {
            "reason": "resource_exhausted", "recorded_at": datetime.now(timezone.utc).isoformat(),
            "resume": "próxima execução agendada", "message_redacted": type(error).__name__,
        }
        save_state(state)
        return state
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza três projetos agregadores de template no Stitch.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-remote", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--max-operations", type=int, default=8)
    args = parser.parse_args()
    if args.max_operations < 1:
        parser.error("--max-operations deve ser maior que zero")
    if args.require_remote and not (os.getenv("STITCH_API_KEY") or os.getenv("STITCH_ACCESS_TOKEN")):
        raise RuntimeError("STITCH_API_KEY ou STITCH_ACCESS_TOKEN é obrigatório para sincronização remota.")
    coordinate = load_coordinate()
    state = load_state() if args.dry_run else sync(args.max_operations)
    summary = status_summary(coordinate, state)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.require_complete and (summary["synced_projects"] != summary["expected_projects"] or summary["pending_screen_groups"] or summary["stale_screen_groups"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
