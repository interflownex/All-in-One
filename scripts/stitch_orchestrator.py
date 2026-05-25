from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config" / "module_catalog.json"
MANIFEST_PATH = ROOT / "config" / "stitch" / "screen_manifest.json"
STATE_PATH = ROOT / "config" / "stitch" / "sync_state.json"
STITCH_ENDPOINT = "https://stitch.googleapis.com/mcp"

APP_ASSIGNMENTS = {
    "identity": ["all-in-one-user", "all-in-one-business", "all-in-one-riders", "all-in-one-services", "all-in-one-health", "all-in-one-mobility"],
    "business": ["all-in-one-business"],
    "permissions": ["all-in-one-business"],
    "finance": ["all-in-one-user", "all-in-one-business", "all-in-one-riders", "all-in-one-services", "all-in-one-mobility"],
    "marketplace": ["all-in-one-user", "all-in-one-business"],
    "stock": ["all-in-one-business"],
    "delivery": ["all-in-one-user", "all-in-one-business", "all-in-one-riders"],
    "riders": ["all-in-one-riders"],
    "services": ["all-in-one-user", "all-in-one-services"],
    "mobility": ["all-in-one-user", "all-in-one-riders", "all-in-one-mobility"],
    "jobs": ["all-in-one-user", "all-in-one-business"],
    "erp": ["all-in-one-business"],
    "wms": ["all-in-one-business"],
    "tms": ["all-in-one-business"],
    "crm": ["all-in-one-business"],
    "bpm": ["all-in-one-business"],
    "document": ["all-in-one-business"],
    "hr": ["all-in-one-business"],
    "health": ["all-in-one-user", "all-in-one-health"],
    "vision": ["all-in-one-business"],
    "legal": ["all-in-one-business"],
    "property": ["all-in-one-business"],
    "bi": ["all-in-one-business"],
    "ai_core": ["all-in-one-business"],
    "api_hub": ["all-in-one-business"],
}

SPECIAL_SCREENS = {
    "jobs": [
        ("candidate_resume", "Curriculo do candidato com origem CTPS validada e itens autodeclarados visualmente distintos."),
        ("ctps_import", "Importacao segura de PDF CTPS Digital com estados de processamento e explicacao de procedencia."),
        ("vacancy_search", "Busca e detalhes de vagas para usuario final com candidatura."),
        ("recruiter_resume_review", "Triagem Business com acesso auditado, filtros e selo de procedencia de cada experiencia."),
    ],
    "identity": [
        ("registration_kyc", "Cadastro All-in-One ID, consentimento LGPD e jornada de verificacao de identidade."),
    ],
    "finance": [
        ("wallet_ledger", "Wallet e extrato imutavel com BRL, NEX, transacoes e seguranca."),
    ],
}


def load_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def screen_prompt(module: dict[str, Any], name: str, purpose: str, apps: list[str]) -> str:
    return (
        f"Crie uma tela de produto profissional para All-in-One, modulo {module['title']}. "
        f"Objetivo: {purpose} "
        f"Contexto do dominio: {module['description']} "
        f"Superficies consumidoras: {', '.join(apps)}. "
        "Use portugues do Brasil, layout responsivo web/mobile, identidade visual consistente entre modulos, "
        "hierarquia limpa, acessibilidade WCAG AA, estados vazio/carregando/erro e acoes principais claras. "
        "Nao exponha biometria, documentos brutos, tokens, chaves, prontuario ou dados sensiveis em exemplos. "
        f"Identificador da tela: {name}."
    )


def build_manifest(catalog: dict[str, Any]) -> dict[str, Any]:
    projects: list[dict[str, Any]] = []
    for module in catalog["modules"]:
        slug = module["slug"]
        apps = APP_ASSIGNMENTS[slug]
        screens = [
            {
                "key": "overview",
                "name": f"{module['title']} - Visao Geral",
                "purpose": f"Painel inicial e navegacao operacional de {module['title']}.",
            }
        ]
        for entity in module["entities"]:
            label = entity.replace("_", " ").title()
            screens.append(
                {
                    "key": f"entity_{entity}",
                    "name": f"{module['title']} - {label}",
                    "purpose": f"Listagem, detalhe e operacoes autorizadas para {label}.",
                }
            )
        for key, purpose in SPECIAL_SCREENS.get(slug, []):
            screens.append(
                {
                    "key": key,
                    "name": f"{module['title']} - {key.replace('_', ' ').title()}",
                    "purpose": purpose,
                }
            )
        screens.append(
            {
                "key": "audit_permissions",
                "name": f"{module['title']} - Auditoria E Permissoes",
                "purpose": "Auditoria de eventos, status, permissoes e historico de decisoes sem dados sensiveis.",
            }
        )
        projects.append(
            {
                "module": slug,
                "project_name": f"All-in-One - {module['title']}",
                "description": module["description"],
                "integrated_apps": apps,
                "screens": screens,
            }
        )
    return {
        "schema_version": 1,
        "strategy": "one_stitch_project_per_microservice",
        "source": "config/module_catalog.json",
        "project_count": len(projects),
        "screen_count": sum(len(project["screens"]) for project in projects),
        "projects": projects,
    }


def versioned_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifest["schema_version"],
        "strategy": manifest["strategy"],
        "source": manifest["source"],
        "project_count": manifest["project_count"],
        "screen_count": manifest["screen_count"],
        "screen_generation": {
            "standard": ["overview", "one_screen_per_entity", "audit_permissions"],
            "special_defined_in": "scripts/stitch_orchestrator.py:SPECIAL_SCREENS",
        },
        "projects": [
            {
                "module": project["module"],
                "project_name": project["project_name"],
                "screen_count": len(project["screens"]),
                "special_screens": [
                    screen["key"]
                    for screen in project["screens"]
                    if screen["key"] not in {"overview", "audit_permissions"}
                    and not screen["key"].startswith("entity_")
                ],
            }
            for project in manifest["projects"]
        ],
    }


def write_manifest() -> dict[str, Any]:
    manifest = build_manifest(load_catalog())
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(versioned_manifest(manifest), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    if not STATE_PATH.exists():
        STATE_PATH.write_text('{\n  "schema_version": 1,\n  "projects": {}\n}\n', encoding="utf-8")
    return manifest


class StitchMcpClient:
    def __init__(self, endpoint: str = STITCH_ENDPOINT) -> None:
        import httpx

        api_key = os.getenv("STITCH_API_KEY")
        access_token = os.getenv("STITCH_ACCESS_TOKEN")
        if not api_key and not access_token:
            raise RuntimeError("Configure STITCH_API_KEY ou STITCH_ACCESS_TOKEN em secret local antes da sincronizacao.")
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if api_key:
            headers["X-Goog-Api-Key"] = api_key
        else:
            headers["Authorization"] = f"Bearer {access_token}"
        self.endpoint = endpoint
        self.client = httpx.Client(headers=headers, timeout=60)
        self.session_id: str | None = None
        self.request_id = 0

    def close(self) -> None:
        self.client.close()

    def _decode(self, response: Any) -> dict[str, Any]:
        response.raise_for_status()
        if response.headers.get("Mcp-Session-Id"):
            self.session_id = response.headers["Mcp-Session-Id"]
        if "text/event-stream" not in response.headers.get("content-type", ""):
            return response.json() if response.content else {}
        for line in response.text.splitlines():
            if line.startswith("data:"):
                payload = json.loads(line.removeprefix("data:").strip())
                if payload.get("id") == self.request_id:
                    return payload
        raise RuntimeError("STITCH MCP nao retornou resposta JSON-RPC para a requisicao.")

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self.request_id += 1
        headers = {"Mcp-Session-Id": self.session_id} if self.session_id else {}
        response = self.client.post(
            self.endpoint,
            headers=headers,
            json={"jsonrpc": "2.0", "id": self.request_id, "method": method, "params": params or {}},
        )
        result = self._decode(response)
        if result.get("error"):
            raise RuntimeError(f"STITCH MCP retornou erro: {result['error']}")
        return result.get("result", {})

    def initialize(self) -> None:
        self.request(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "all-in-one-stitch-orchestrator", "version": "1.0.0"},
            },
        )
        headers = {"Mcp-Session-Id": self.session_id} if self.session_id else {}
        self.client.post(
            self.endpoint,
            headers=headers,
            json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        ).raise_for_status()

    def tools(self) -> list[dict[str, Any]]:
        return self.request("tools/list").get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.request("tools/call", {"name": name, "arguments": arguments})


def choose_tool(tools: list[dict[str, Any]], candidates: tuple[str, ...]) -> dict[str, Any]:
    normalized = {tool["name"].lower(): tool for tool in tools}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    for tool in tools:
        tool_name = tool["name"].lower()
        if all(fragment in tool_name for fragment in candidates[0].split("_")):
            return tool
    raise RuntimeError(f"Tool STITCH nao localizado para {candidates[0]}; execute discover para revisar capacidades.")


def input_arguments(tool: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    properties = tool.get("inputSchema", {}).get("properties", {})
    arguments: dict[str, Any] = {}
    for canonical_name, aliases in {
        "name": ("name", "title", "project_name", "projectName"),
        "project_id": ("project_id", "projectId", "project"),
        "prompt": ("prompt", "description", "text"),
    }.items():
        for alias in aliases:
            if alias in properties and canonical_name in values:
                arguments[alias] = values[canonical_name]
                break
    if "prompt" in values and not any(alias in arguments for alias in ("prompt", "description", "text")):
        raise RuntimeError(f"Schema da tool {tool['name']} nao oferece argumento de prompt reconhecido.")
    return arguments


def extract_identifier(result: Any) -> str | None:
    if isinstance(result, dict):
        for key in ("projectId", "project_id", "screenId", "screen_id", "id"):
            if key in result and isinstance(result[key], str):
                return result[key]
        for value in result.values():
            identifier = extract_identifier(value)
            if identifier:
                return identifier
    if isinstance(result, list):
        for value in result:
            identifier = extract_identifier(value)
            if identifier:
                return identifier
    if isinstance(result, str):
        try:
            return extract_identifier(json.loads(result))
        except json.JSONDecodeError:
            return None
    return None


def sync_projects(manifest: dict[str, Any]) -> dict[str, Any]:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {"schema_version": 1, "projects": {}}
    modules = {module["slug"]: module for module in load_catalog()["modules"]}
    client = StitchMcpClient()
    try:
        client.initialize()
        tools = client.tools()
        create_project = choose_tool(tools, ("create_project", "new_project"))
        generate_screen = choose_tool(tools, ("generate_screen", "create_screen"))
        for project in manifest["projects"]:
            project_state = state["projects"].setdefault(project["module"], {"screens": {}})
            if "project_id" not in project_state:
                result = client.call_tool(create_project["name"], input_arguments(create_project, {"name": project["project_name"]}))
                project_state["project_id"] = extract_identifier(result)
                if not project_state["project_id"]:
                    raise RuntimeError(f"STITCH nao retornou project_id para {project['module']}.")
            for screen in project["screens"]:
                if screen["key"] in project_state["screens"]:
                    continue
                result = client.call_tool(
                    generate_screen["name"],
                    input_arguments(
                        generate_screen,
                        {
                            "project_id": project_state["project_id"],
                            "prompt": screen_prompt(
                                modules[project["module"]],
                                screen["key"],
                                screen["purpose"],
                                project["integrated_apps"],
                            ),
                        },
                    ),
                )
                screen_id = extract_identifier(result)
                if not screen_id:
                    raise RuntimeError(f"STITCH nao retornou screen_id para {project['module']}/{screen['key']}.")
                project_state["screens"][screen["key"]] = {"screen_id": screen_id, "name": screen["name"]}
                STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        return state
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan and synchronize All-in-One module screens with Google Stitch MCP.")
    parser.add_argument("command", choices=("plan", "discover", "sync"))
    args = parser.parse_args()
    manifest = write_manifest()
    if args.command == "plan":
        print(f"STITCH plan: {manifest['project_count']} projetos e {manifest['screen_count']} telas materializados.")
        return 0
    client = StitchMcpClient()
    if args.command == "discover":
        try:
            client.initialize()
            print(json.dumps(client.tools(), indent=2, ensure_ascii=True))
            return 0
        finally:
            client.close()
    state = sync_projects(manifest)
    print(f"STITCH sync: {len(state['projects'])} projetos registrados em estado local.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
