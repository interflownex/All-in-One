#!/usr/bin/env python3
"""Materializa configuracao persistente de Docker DX para desenvolvimento local."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "autonomy" / "docker_dx_policy.json"
USER_PLUGIN_DIR = Path.home() / ".docker" / "cli-plugins"
SYSTEM_PLUGIN_DIRS = (
    Path("/usr/libexec/docker/cli-plugins"),
    Path("/usr/lib/docker/cli-plugins"),
)
REQUIRED_CLI_PLUGINS = ("compose", "buildx")
DOCKER_CAPABILITY_TIMEOUT_SECONDS = 45


def load_policy() -> dict[str, object]:
    with POLICY_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def render_env(policy: dict[str, object]) -> str:
    defaults = policy["environment_defaults"]
    if not isinstance(defaults, dict):
        raise RuntimeError("environment_defaults deve ser um objeto JSON.")
    lines = [
        "# Gerado por scripts/configure_docker_dx.py.",
        "# Nao inclua segredos neste arquivo; use variaveis locais/secret stores.",
    ]
    for key in sorted(defaults):
        lines.append(f"{key}={defaults[key]}")
    return "\n".join(lines) + "\n"


def write_if_changed(path: Path, content: str, dry_run: bool) -> bool:
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    if previous == content:
        return False
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def plugin_binary(plugin: str) -> Path | None:
    binary_name = f"docker-{plugin}"
    for directory in SYSTEM_PLUGIN_DIRS:
        candidate = directory / binary_name
        if candidate.is_file() and candidate.stat().st_mode & stat.S_IXUSR:
            return candidate
    return None


def ensure_user_cli_plugin_links(dry_run: bool) -> list[str]:
    """Prioriza plugins locais validos quando symlinks do Docker Desktop quebram o CLI."""
    changed: list[str] = []
    for plugin in REQUIRED_CLI_PLUGINS:
        source = plugin_binary(plugin)
        if source is None:
            continue
        target = USER_PLUGIN_DIR / f"docker-{plugin}"
        if target.is_symlink() and target.resolve(strict=False) == source:
            continue
        if target.exists() and not target.is_symlink():
            continue
        changed.append(plugin)
        if not dry_run:
            USER_PLUGIN_DIR.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                target.unlink()
            target.symlink_to(source)
    return changed


def docker_subcommand_exists(
    *args: str,
    timeout_seconds: int = DOCKER_CAPABILITY_TIMEOUT_SECONDS,
) -> bool:
    if not command_exists("docker"):
        return False
    try:
        result = subprocess.run(
            ["docker", *args],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=timeout_seconds,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def docker_socket_is_safe() -> bool:
    socket_path = Path("/var/run/docker.sock")
    if not socket_path.exists():
        return True
    mode = stat.S_IMODE(socket_path.stat().st_mode)
    return not (mode & stat.S_IWOTH)


def validate_policy(policy: dict[str, object]) -> list[str]:
    errors: list[str] = []
    compose_file = ROOT / str(policy.get("compose_file", ""))
    if not compose_file.is_file():
        errors.append(f"Compose ausente: {compose_file.relative_to(ROOT)}")

    env_defaults = policy.get("environment_defaults")
    if not isinstance(env_defaults, dict):
        errors.append("environment_defaults ausente ou invalido.")
    elif env_defaults.get("DOCKER_BUILDKIT") != "1":
        errors.append("DOCKER_BUILDKIT deve ficar ativo por padrao.")

    dockerignore = ROOT / ".dockerignore"
    if not dockerignore.is_file():
        errors.append(".dockerignore ausente.")
    else:
        dockerignore_lines = set(dockerignore.read_text(encoding="utf-8").splitlines())
        required = (
            policy.get("build", {})
            .get("context_hygiene", {})
            .get("required_exclusions", [])
        )
        missing = sorted(set(required) - dockerignore_lines)
        if missing:
            errors.append(f".dockerignore sem entradas obrigatorias: {', '.join(missing)}")

    if not docker_socket_is_safe():
        errors.append("/var/run/docker.sock esta world-writable; nao use chmod 666.")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Valida sem gravar arquivos.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que mudaria sem gravar.")
    parser.add_argument("--print-status", action="store_true", help="Mostra capacidades Docker detectadas.")
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    policy = load_policy()
    errors = validate_policy(policy)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    env_path = ROOT / str(policy["env_file"])
    env_changed = write_if_changed(env_path, render_env(policy), dry_run=args.check or args.dry_run)
    plugin_links_changed = ensure_user_cli_plugin_links(dry_run=args.check or args.dry_run)

    if args.print_status:
        status = {
            "docker": command_exists("docker"),
            "compose": docker_subcommand_exists("compose", "version"),
            "buildx": docker_subcommand_exists("buildx", "version"),
            "docker_mcp": docker_subcommand_exists("mcp", "--help"),
            "env_file": str(env_path.relative_to(ROOT)),
            "env_changed": env_changed,
            "user_plugin_links_changed": plugin_links_changed,
        }
        print(json.dumps(status, indent=2, sort_keys=True))
    elif args.check:
        print("Docker DX validado.")
    else:
        verb = "seria atualizado" if args.dry_run else "atualizado"
        print(f"Docker DX {verb}: {env_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
