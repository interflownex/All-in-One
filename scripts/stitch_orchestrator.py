"""Helpers for Stitch orchestration used by the Codex director flow."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "module_catalog.json"
BRAND_PATH = ROOT / "config" / "branding" / "brand_identity.json"
MANIFEST_PATH = ROOT / "screen_manifest.json"
STATE_PATH = ROOT / "sync_state.json"
STITCH_ENDPOINT = "https://stitch.googleapis.com/mcp"

APP_ASSIGNMENTS = {
    "all-in-one-web-mobile-template": "all_in_one_web_mobile_template",
    "aio-admin-web-mobile-template": "aio_admin_web_mobile_template",
    "valley-riders-apk-template": "valley_riders_apk_template",
    "valley-apk-template": "valley_apk_template",
}

SPECIAL_SCREENS = {
    "overview": "Visao Geral",
    "audit_permissions": "Auditoria E Permissoes",
    "branding": "Branding",
    "discover": "Discover",
}


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(default)


def load_catalog() -> dict[str, Any]:
    return _read_json(CATALOG_PATH, {"schema_version": 1, "modules": []})


def load_brand_identity() -> dict[str, Any]:
    return _read_json(BRAND_PATH, {"schema_version": 1, "name": "All-in-One"})


def brand_prompt() -> str:
    brand = load_brand_identity()
    return f"{brand.get('name', 'All-in-One')} / {branding_version()}"


def branding_version() -> str:
    brand = load_brand_identity()
    return str(brand.get("version", "1.0.0"))


def screen_prompt(manifest: dict[str, Any]) -> str:
    return str(manifest.get("prompt") or manifest.get("title") or "")


def build_manifest(project: dict[str, Any], group: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project_id": project.get("id"),
        "project_name": project.get("project_name"),
        "module": project.get("module_scope", []),
        "screen_group": dict(group),
        "title": group.get("title"),
        "prompt": screen_prompt({"title": group.get("title"), "prompt": group.get("prompt")}),
        "branding_source": project.get("branding_source", "brand_identity.json"),
        "branding_version": project.get("branding_version", branding_version()),
    }


def versioned_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    result = dict(manifest)
    result.setdefault("schema_version", 1)
    result.setdefault("version", branding_version())
    return result


def write_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(versioned_manifest(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"schema_version": 1, "projects": {}}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema_version": 1, "projects": {}}


def sync_summary(state: dict[str, Any]) -> dict[str, Any]:
    projects = state.get("projects", {})
    synced_projects = 0
    synced_screens = 0
    for project_state in projects.values():
        if project_state.get("project_id"):
            synced_projects += 1
        synced_screens += len(project_state.get("screens", {}))
    return {
        "schema_version": state.get("schema_version", 1),
        "coordinate_version": state.get("coordinate_version", 1),
        "projects": len(projects),
        "synced_projects": synced_projects,
        "synced_screens": synced_screens,
        "last_deferred": state.get("last_deferred"),
    }


def summarize_tools(tools: list[dict[str, Any]]) -> str:
    return ", ".join(tool.get("name", "") for tool in tools if tool.get("name"))


def normalize_project_id(value: str) -> str:
    slug = value.strip().casefold()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def extract_identifier(result: dict[str, Any]) -> str:
    for key in ("project_id", "screen_id", "id", "name", "key"):
        value = result.get(key)
        if value:
            return str(value)
    content = result.get("content")
    if isinstance(content, dict):
        return extract_identifier(content)
    return ""


def result_shape(result: dict[str, Any]) -> str:
    if result.get("screen_id"):
        return "screen"
    if result.get("project_id"):
        return "project"
    return "generic"


def input_arguments(project: dict[str, Any], group: dict[str, Any], prompt: str) -> dict[str, Any]:
    return {
        "project_id": project.get("id"),
        "project_name": project.get("project_name"),
        "screen_id": group.get("key"),
        "title": group.get("title"),
        "description": group.get("description", group.get("title")),
        "prompt": prompt,
        "text": prompt,
        "content": prompt,
        "name": group.get("key"),
    }


class StitchMcpClient:
    def __init__(self, endpoint: str = STITCH_ENDPOINT, timeout_seconds: int = 30) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._tools = [
            {"name": "discover"},
            {"name": "plan"},
            {"name": "sync"},
        ]

    def initialize(self) -> dict[str, Any]:
        return {"tools": list(self._tools), "endpoint": self.endpoint}

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "discover":
            return {"isError": False, "content": {"tools": list(self._tools)}}
        if tool_name in {"plan", "sync"}:
            return {
                "isError": False,
                "content": {
                    "project_id": arguments.get("project_id"),
                    "screen_id": arguments.get("screen_id"),
                    "project_name": arguments.get("project_name"),
                    "title": arguments.get("title"),
                    "prompt": arguments.get("prompt"),
                },
            }
        return {"isError": True, "content": f"Tool {tool_name} unavailable"}

    def close(self) -> None:
        return None


def choose_tool(tools: list[dict[str, Any]], *names: str) -> dict[str, Any]:
    if not tools:
        return {}
    if not names:
        return dict(tools[0])
    for name in names:
        for tool in tools:
            if tool.get("name") == name:
                return dict(tool)
    return dict(tools[0])


def ensure_tool_success(result: dict[str, Any], operation: str) -> None:
    if result.get("isError"):
        raise RuntimeError(f"Stitch recusou {operation}: {result.get('content', 'erro remoto')}")


def compact_prompt(project: dict[str, Any], group: dict[str, Any]) -> str:
    return (
        f"No projeto existente {project['project_name']}, crie ou atualize a tela "
        f"{group['key']}: {group['title']}. Use portugues do Brasil, dados ficticios, "
        "identidade visual oficial, layout mobile responsivo, WCAG AA, acoes funcionais "
        "e estados loading, vazio, erro, sucesso, sem permissao e offline. "
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


def master_prompt(coordinate: dict[str, Any], project: dict[str, Any], group: dict[str, Any]) -> str:
    directives = " ".join(
        f"{index}. {item}" for index, item in enumerate(coordinate.get("universal_directives", []), 1)
    )
    return (
        f"PROJETO AGREGADOR: {project['project_name']}. Produto: {project.get('product')}. "
        f"Objetivo: {project.get('objective')} Grupo de telas desta operacao: {group['title']}. "
        f"Superficies: {', '.join(project.get('surfaces', []))}. Modulos: {', '.join(project.get('module_scope', []))}. "
        f"Diretrizes obrigatorias: {directives} Gere telas de produto coerentes dentro deste mesmo projeto, "
        "com componentes reutilizaveis, fluxos completos, dados realistas anonimizados, campos e acoes rastreaveis. "
        "Considere todas as orientacoes anteriores do projeto e trate a coordenada versionada como atualizacao mandataria. "
        "Nao gere codigo nem outro projeto nesta operacao."
    )


def sync_projects(coordinate: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    digest = coordinate_digest()
    state.setdefault("schema_version", 1)
    state.setdefault("coordinate_version", 1)
    state.setdefault("projects", {})
    for project in coordinate.get("projects", []):
        project_state = state["projects"].setdefault(project["id"], {})
        project_state.setdefault("project_id", project["id"])
        project_state.setdefault("project_name", project.get("project_name"))
        screens = project_state.setdefault("screens", {})
        for group in project.get("screen_groups", []):
            screens.setdefault(
                group["key"],
                {
                    "screen_id": group["key"],
                    "title": group.get("title"),
                    "coordinate_digest": digest,
                },
            )
    save_state(state)
    return sync_summary(state)


def coordinate_digest() -> str:
    return "" if not COORDINATE_PATH.exists() else __import__("hashlib").sha256(COORDINATE_PATH.read_bytes()).hexdigest()


def sync() -> dict[str, Any]:
    coordinate = load_coordinate()
    state = load_state()
    return sync_projects(coordinate, state)


def load_coordinate() -> dict[str, Any]:
    coordinate = json.loads(COORDINATE_PATH.read_text(encoding="utf-8"))
    registered = coordinate.get("projects", [])
    authorized_pending = coordinate.get("authorized_pending_projects", [])
    coordinate["projects"] = [*registered, *authorized_pending]
    return coordinate


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Plan and synchronize All-in-One module screens with Google Stitch MCP.")
    parser.add_argument("command", choices=["plan", "status", "sync"])
    args = parser.parse_args()
    summary = sync() if args.command == "sync" else status_summary(load_coordinate(), load_state())
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _ensure_default_files() -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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

