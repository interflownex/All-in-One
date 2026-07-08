from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "autonomy" / "stitch_mcp_policy.json"
DEFAULT_CODEX_CONFIG = Path(os.getenv("CODEX_CONFIG_FILE", Path.home() / ".codex" / "config.toml"))
EXPECTED_SERVER = "stitch"
EXPECTED_ENDPOINT = "https://stitch.googleapis.com/mcp"
EXPECTED_HEADER = "X-Goog-Api-Key"
EXPECTED_ENV_VAR = "STITCH_API_KEY"
EXPECTED_ACCEPT = "application/json"

SECRET_ASSIGNMENT_PATTERNS = (
    re.compile(r"(?im)^\s*STITCH_API_KEY\s*=\s*['\"]?[^'\"\s#][^'\"\n#]*"),
    re.compile(r"(?im)X-Goog-Api-Key\s*[:=]\s*(?!\$\{STITCH_API_KEY\}|STITCH_API_KEY\b)['\"]?[A-Za-z0-9_\-]{12,}"),
)
SECRET_SCAN_PATHS = [
    ".agents",
    ".env.example",
    ".github",
    ".vscode",
    "AGENTS.md",
    "GEMINI.md",
    "README.md",
    "config",
    "docs",
    "infra",
    "scripts",
]


def load_policy(policy_path: Path = POLICY_PATH) -> dict[str, Any]:
    if not policy_path.is_file():
        raise ValueError(f"Politica Stitch ausente: {policy_path}")
    try:
        return json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Politica Stitch invalida: {exc}") from exc


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_auth = policy.get("required_auth", {})
    required_headers = policy.get("required_headers", {})
    if policy.get("enabled") is not True:
        if policy.get("disabled_until") != "segunda_ordem_explicita_do_usuario":
            errors.append("Politica Stitch desativada deve declarar disabled_until=segunda_ordem_explicita_do_usuario.")
        if not policy.get("disabled_reason"):
            errors.append("Politica Stitch desativada deve declarar disabled_reason.")
    if policy.get("server_name") != EXPECTED_SERVER:
        errors.append("Politica Stitch deve declarar server_name stitch.")
    if policy.get("endpoint") != EXPECTED_ENDPOINT:
        errors.append(f"Politica Stitch deve usar endpoint {EXPECTED_ENDPOINT}.")
    if required_auth.get("type") != "env_http_header":
        errors.append("Politica Stitch deve exigir autenticacao por env_http_header.")
    if required_auth.get("header") != EXPECTED_HEADER:
        errors.append(f"Politica Stitch deve exigir header {EXPECTED_HEADER}.")
    if required_auth.get("environment_variable") != EXPECTED_ENV_VAR:
        errors.append(f"Politica Stitch deve exigir variavel {EXPECTED_ENV_VAR}.")
    if required_headers.get("Accept") != EXPECTED_ACCEPT:
        errors.append(f"Politica Stitch deve exigir Accept {EXPECTED_ACCEPT}.")
    return errors


def is_stitch_enabled(root: Path = ROOT) -> bool:
    try:
        return load_policy(root / "config" / "autonomy" / "stitch_mcp_policy.json").get("enabled") is True
    except ValueError:
        return False


def load_toml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Config Codex ausente: {path}")
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Config Codex invalida em {path}: {exc}") from exc


def validate_codex_config(config: dict[str, Any], config_path: Path) -> list[str]:
    errors: list[str] = []
    stitch = config.get("mcp_servers", {}).get(EXPECTED_SERVER)
    if not isinstance(stitch, dict):
        return [f"Servidor MCP obrigatorio ausente em {config_path}: [mcp_servers.stitch]"]
    if stitch.get("url") != EXPECTED_ENDPOINT:
        errors.append(f"Servidor Stitch deve usar url {EXPECTED_ENDPOINT}.")
    if stitch.get("http_headers", {}).get("Accept") != EXPECTED_ACCEPT:
        errors.append(f"Servidor Stitch deve declarar http_headers.Accept = {EXPECTED_ACCEPT}.")
    env_headers = stitch.get("env_http_headers", {})
    if env_headers.get(EXPECTED_HEADER) != EXPECTED_ENV_VAR:
        errors.append(f"Servidor Stitch deve mapear {EXPECTED_HEADER} para {EXPECTED_ENV_VAR} em env_http_headers.")
    literal_headers = stitch.get("headers", {}) | stitch.get("http_headers", {})
    literal_key = literal_headers.get(EXPECTED_HEADER)
    if literal_key and literal_key != f"${{{EXPECTED_ENV_VAR}}}":
        errors.append(f"Servidor Stitch nao pode gravar {EXPECTED_HEADER} literal em {config_path}.")
    if stitch.get("command") or stitch.get("args"):
        errors.append("Servidor Stitch deve usar transporte HTTP nativo por url/env_http_headers, sem command/args.")
    return errors


def untracked_files(root: Path = ROOT) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10,
    )
    return [root / line for line in result.stdout.splitlines() if line]


def stitch_secret_candidate_files(root: Path = ROOT) -> list[Path]:
    if shutil.which("rg"):
        result = subprocess.run(
            [
                "rg",
                "-l",
                "-F",
                "-e",
                "STITCH_API_KEY",
                "-e",
                EXPECTED_HEADER,
                "--glob",
                "!.git/**",
                "--glob",
                "!.venv/**",
                "--glob",
                "!node_modules/**",
                *SECRET_SCAN_PATHS,
            ],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr.strip() or "Falha ao buscar candidatos a segredo Stitch.")
        return [root / line for line in result.stdout.splitlines() if line]

    result = subprocess.run(
        ["git", "grep", "-Il", "-e", "STITCH_API_KEY", "-e", EXPECTED_HEADER, "--"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=10,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "Falha ao buscar candidatos a segredo Stitch.")
    candidates = {root / line for line in result.stdout.splitlines() if line}
    for path in untracked_files(root):
        if path in candidates or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "STITCH_API_KEY" in content or EXPECTED_HEADER in content:
            candidates.add(path)
    return sorted(candidates)


def validate_no_versioned_secret(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in stitch_secret_candidate_files(root):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_ASSIGNMENT_PATTERNS:
            match = pattern.search(content)
            if match:
                relative = path.relative_to(root)
                errors.append(f"Possivel segredo Stitch versionado em {relative}: {match.group(0).strip()}")
                break
    return errors


def validate_stitch_mcp_config(
    config_path: Path = DEFAULT_CODEX_CONFIG,
    require_secret: bool = False,
    root: Path = ROOT,
    require_codex_config: bool = True,
) -> list[str]:
    errors: list[str] = []
    try:
        errors.extend(validate_policy(load_policy(root / "config" / "autonomy" / "stitch_mcp_policy.json")))
    except ValueError as exc:
        errors.append(str(exc))
    should_validate_config = require_codex_config and (
        is_stitch_enabled(root) or config_path != DEFAULT_CODEX_CONFIG
    )
    if should_validate_config:
        try:
            errors.extend(validate_codex_config(load_toml(config_path), config_path))
        except ValueError as exc:
            errors.append(str(exc))
    errors.extend(validate_no_versioned_secret(root))
    if require_secret and is_stitch_enabled(root) and not os.getenv(EXPECTED_ENV_VAR):
        errors.append(f"Variavel obrigatoria ausente no ambiente: {EXPECTED_ENV_VAR}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a configuracao obrigatoria do MCP Stitch.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CODEX_CONFIG, help="Arquivo config.toml do Codex.")
    parser.add_argument("--require-secret", action="store_true", help="Exige STITCH_API_KEY no ambiente.")
    args = parser.parse_args()

    errors = validate_stitch_mcp_config(config_path=args.config, require_secret=args.require_secret)
    if errors:
        print("\nFalhas de validacao do MCP Stitch:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nMCP Stitch validado com sucesso: configuracao persistente e politica versionada em conformidade.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
