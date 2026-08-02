#!/usr/bin/env python3
"""Sincroniza o perfil MCP confiavel do Antigravity sem gravar segredos."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "autonomy" / "antigravity_trust_policy.json"
CONTRACT_PATH = ROOT / ".agents" / "antigravity.json"
SECRET_MARKERS = ("AQ.", "eyJ", "sk-", "AIza", "-----BEGIN")


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def posix_target(path: str) -> bool:
    return path.startswith("/")


def filesystem_paths(policy: dict, target_path: str) -> list[str]:
    trusted = policy["trusted_workspaces"]
    if posix_target(target_path):
        return [trusted["wsl"], str(Path.home() / ".codex")]
    return [trusted["windows"], "C:\\Users\\ereta\\.codex"]


def build_mcp_config(policy: dict, target_path: str) -> dict:
    docker = policy["docker_mcp"]
    filesystem_args = [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        *filesystem_paths(policy, target_path),
    ]
    return {
        "mcpServers": {
            "filesystem-all-in-one": {
                "command": "npx",
                "args": filesystem_args,
            },
            "context7": {
                "command": "npx",
                "args": ["-y", "mcp-remote", "https://mcp.context7.com/mcp"],
            },
            "cloudflare-docs": {
                "command": "npx",
                "args": ["-y", "mcp-remote", "https://docs.mcp.cloudflare.com/mcp"],
            },
            "cloudflare-api": {
                "command": "npx",
                "args": [
                    "-y",
                    "mcp-remote",
                    "https://mcp.cloudflare.com/mcp",
                    "--header",
                    "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}",
                ],
            },
            "docker": {
                "command": docker["command"],
                "args": docker["args"],
            },
            "stitch": {
                "command": "npx",
                "args": [
                    "-y",
                    "mcp-remote",
                    "https://stitch.googleapis.com/mcp",
                    "--header",
                    "X-Goog-Api-Key: ${STITCH_API_KEY}",
                ],
            },
        }
    }


def serialize(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def contains_secret_marker(text: str) -> bool:
    return any(marker in text for marker in SECRET_MARKERS)


def backup_existing(path: Path) -> Path | None:
    if not path.exists():
        return None
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    backup = path.with_name(f"{path.name}.bak-{timestamp}")
    shutil.copy2(path, backup)
    return backup


def write_target(path: Path, content: str, dry_run: bool) -> tuple[bool, Path | None]:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == content:
        return False, None
    if dry_run:
        return True, None
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = backup_existing(path)
    path.write_text(content, encoding="utf-8")
    return True, backup


def validate_contract(policy: dict, contract: dict) -> list[str]:
    errors: list[str] = []
    essential = set(policy["essential_mcp_servers"])
    declared = set(contract.get("mcp_servers", []))
    disabled = {item["name"] for item in contract.get("disabled_mcp_servers", [])}
    if contract.get("name") != "antigravity":
        errors.append(".agents/antigravity.json deve declarar name=antigravity.")
    if essential != declared:
        errors.append(
            "Contrato Antigravity deve declarar exatamente os MCPs essenciais: "
            + ", ".join(sorted(essential))
        )
    missing_disabled = set(policy["disabled_mcp_servers"]) - disabled
    if missing_disabled:
        errors.append(
            "Contrato Antigravity deve justificar MCPs desativados: "
            + ", ".join(sorted(missing_disabled))
        )
    return errors


def validate_target(path: Path, policy: dict) -> list[str]:
    errors: list[str] = []
    expected = build_mcp_config(policy, str(path))
    expected_text = serialize(expected)
    if not path.is_file():
        errors.append(f"Config Antigravity ausente: {path}")
        return errors
    text = path.read_text(encoding="utf-8")
    if text != expected_text:
        errors.append(f"Config Antigravity diverge da politica: {path}")
    if contains_secret_marker(text):
        errors.append(f"Config Antigravity contem marcador de segredo: {path}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        errors.append(f"Config Antigravity nao e JSON valido: {path}")
        return errors
    servers = set((data.get("mcpServers") or {}).keys())
    if servers != set(policy["essential_mcp_servers"]):
        errors.append(f"Config Antigravity contem servidores fora da lista essencial: {path}")
    serialized = json.dumps(data)
    for env_var in policy["secret_environment_variables"]:
        pattern = re.compile(rf"{re.escape(env_var)}[A-Za-z0-9_]*[\"']?\s*:\s*[\"'][^$]")
        if pattern.search(serialized):
            errors.append(f"Config Antigravity parece gravar valor literal de {env_var}: {path}")
    return errors


def validate(policy: dict) -> list[str]:
    errors = validate_contract(policy, load_contract())
    for target in policy["config_targets"]:
        errors.extend(validate_target(Path(target), policy))
    return errors


def apply(policy: dict, dry_run: bool) -> list[str]:
    changed: list[str] = []
    backups: list[str] = []
    for target in policy["config_targets"]:
        path = Path(target)
        content = serialize(build_mcp_config(policy, target))
        if contains_secret_marker(content):
            raise RuntimeError("Config gerada contem marcador de segredo.")
        did_change, backup = write_target(path, content, dry_run=dry_run)
        if did_change:
            changed.append(str(path))
        if backup is not None:
            backups.append(str(backup))
    if backups:
        print("Backups Antigravity criados fora do Git: " + ", ".join(backups))
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Grava os mcp_config.json locais.")
    parser.add_argument("--check", action="store_true", help="Valida os arquivos locais.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra divergencias sem gravar.")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    policy = load_policy()
    if args.apply or args.dry_run:
        changed = apply(policy, dry_run=args.dry_run)
        action = "seria sincronizado" if args.dry_run else "sincronizado"
        print(
            f"Antigravity {action}: "
            + (", ".join(changed) if changed else "sem alteracoes")
        )

    errors = validate(policy)
    if errors:
        print("Antigravity invalido:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Antigravity validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
