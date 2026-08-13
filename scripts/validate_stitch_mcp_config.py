"""Valida a configuracao obrigatoria do MCP Stitch."""

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
POLICY_PATH = ROOT / "config" / "autonomy" / "stitch_mcp_policy.json"
DEFAULT_CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
EXPECTED_SERVER = "stitch"
EXPECTED_ENDPOINT = "https://stitch.googleapis.com/mcp"
EXPECTED_HEADER = "X-Goog-Api-Key"
EXPECTED_ENV_VAR = "STITCH_API_KEY"
EXPECTED_ACCEPT = "application/json"
SECRET_ASSIGNMENT_PATTERNS = [
    re.compile(r"['\"]X-Goog-Api-Key['\"]\s*=\s*['\"][^'\"]+['\"]"),
    re.compile(r"AIza[0-9A-Za-z\-_]{10,}"),
]
SECRET_SCAN_PATHS = [".", "config", "scripts", "docs", ".github"]
SECRET_SCAN_EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_tmp", "node_modules", "dist", "build", ".venv"}


def load_policy(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("enabled") is not True:
        errors.append("A politica Stitch precisa estar habilitada.")
    if policy.get("server") != EXPECTED_SERVER:
        errors.append(f"A politica Stitch precisa apontar para {EXPECTED_SERVER}.")
    if policy.get("endpoint") != EXPECTED_ENDPOINT:
        errors.append(f"A politica Stitch precisa usar {EXPECTED_ENDPOINT}.")
    return errors


def is_stitch_enabled(root: Path) -> bool:
    try:
        return load_policy(root / "config" / "autonomy" / "stitch_mcp_policy.json").get("enabled") is True
    except (OSError, ValueError, json.JSONDecodeError):
        return False


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


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
        errors.append(
            f"Servidor Stitch deve mapear {EXPECTED_HEADER} para {EXPECTED_ENV_VAR} em env_http_headers."
        )

    literal_headers = {**stitch.get("headers", {}), **stitch.get("http_headers", {})}
    literal_key = literal_headers.get(EXPECTED_HEADER)
    if literal_key and literal_key != f"${{{EXPECTED_ENV_VAR}}}":
        errors.append(f"Servidor Stitch nao pode gravar {EXPECTED_HEADER} literal em {config_path}.")

    if stitch.get("command") or stitch.get("args"):
        errors.append("Servidor Stitch deve usar transporte HTTP nativo por url/env_http_headers, sem command/args.")
    return errors


def untracked_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    return [root / line for line in result.stdout.splitlines() if line.strip()]


def stitch_secret_candidate_files(root: Path) -> list[Path]:
    candidates: set[Path] = set()
    for relative in SECRET_SCAN_PATHS:
        path = root / relative
        if path.is_dir():
            paths = path.rglob("*")
        else:
            paths = [path]
        for candidate in paths:
            if any(part in SECRET_SCAN_EXCLUDED_DIRS for part in candidate.relative_to(root).parts):
                continue
            if not candidate.is_file():
                continue
            try:
                content = candidate.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "STITCH_API_KEY" not in content and EXPECTED_HEADER not in content:
                continue
            candidates.add(candidate)
    return sorted(candidates)


def validate_no_versioned_secret(root: Path) -> list[str]:
    errors: list[str] = []
    for path in stitch_secret_candidate_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_ASSIGNMENT_PATTERNS:
            match = pattern.search(content)
            if not match:
                continue
            relative = path.relative_to(root)
            errors.append(
                f"Possivel segredo Stitch versionado em {relative}: {match.group(0).strip()}"
            )
            break
    return errors


def validate_stitch_mcp_config(
    config_path: Path,
    require_secret: bool = False,
    root: Path | None = None,
    require_codex_config: bool = False,
) -> list[str]:
    root = root or ROOT
    errors: list[str] = []

    try:
        policy_path = root / "config" / "autonomy" / "stitch_mcp_policy.json"
        if policy_path.exists():
            errors.extend(validate_policy(load_policy(policy_path)))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))

    if config_path.exists():
        try:
            config = load_toml(config_path)
            errors.extend(validate_codex_config(config, config_path))
        except ValueError as exc:
            errors.append(str(exc))
    elif require_codex_config:
        errors.append(f"Arquivo de configuracao ausente: {config_path}")

    errors.extend(validate_no_versioned_secret(root))

    if require_secret and is_stitch_enabled(root) and not os.getenv(EXPECTED_ENV_VAR):
        errors.append(f"Variavel obrigatoria ausente no ambiente: {EXPECTED_ENV_VAR}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida a configuracao obrigatoria do MCP Stitch.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CODEX_CONFIG, help="Arquivo config.toml do Codex.")
    parser.add_argument("--require-secret", action="store_true", help="Exige STITCH_API_KEY no ambiente.")
    args = parser.parse_args()

    errors = validate_stitch_mcp_config(args.config, args.require_secret, ROOT)
    if errors:
        print("\nFalhas de validacao do MCP Stitch:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nMCP Stitch validado com sucesso: configuracao persistente e politica versionada em conformidade.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
