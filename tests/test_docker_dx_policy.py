from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts import configure_docker_dx


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "autonomy" / "docker_dx_policy.json"


def load_policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def test_docker_dx_policy_persists_expected_contract() -> None:
    policy = load_policy()

    assert policy["compose_file"] == "infra/docker/docker-compose.yml"
    assert policy["env_file"] == ".env.docker-dx"
    assert policy["runtime"]["preferred_engine"] == "wsl_docker_engine"
    assert policy["runtime"]["require_compose_plugin"] is True
    assert policy["runtime"]["require_buildx_plugin"] is True
    assert policy["runtime"]["forbid_world_writable_socket"] is True


def test_docker_dx_defaults_are_secret_safe_and_keep_google_off_locally() -> None:
    defaults = load_policy()["environment_defaults"]

    assert defaults["DOCKER_BUILDKIT"] == "1"
    assert defaults["COMPOSE_DOCKER_CLI_BUILD"] == "1"
    assert defaults["COMPOSE_PROJECT_NAME"] == "all-in-one-dx"
    assert defaults["GOOGLE_INTEGRATIONS_ENABLED"] == "false"
    assert defaults["GOOGLE_CLOUD_ENABLED"] == "false"
    assert defaults["ALLOYDB_ENABLED"] == "false"
    assert defaults["STITCH_REMOTE_SYNC_ENABLED"] == "false"
    assert all("KEY" not in key and "SECRET" not in key and "TOKEN" not in key for key in defaults)


def test_docker_dx_context_hygiene_matches_dockerignore() -> None:
    policy = load_policy()
    required = set(policy["build"]["context_hygiene"]["required_exclusions"])
    dockerignore = set((ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines())

    assert required <= dockerignore


def test_docker_dx_script_check_is_idempotent() -> None:
    result = subprocess.run(
        ["python3", "scripts/configure_docker_dx.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "Docker DX validado." in result.stdout


def test_docker_dx_capability_probe_does_not_hang(monkeypatch) -> None:
    monkeypatch.setattr(configure_docker_dx, "command_exists", lambda command: command == "docker")

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=kwargs.get("timeout", 0))

    monkeypatch.setattr(configure_docker_dx.subprocess, "run", fake_run)

    assert configure_docker_dx.docker_subcommand_exists("compose", "version", timeout_seconds=1) is False


def test_docker_dx_repairs_user_plugin_links_without_sudo(tmp_path, monkeypatch) -> None:
    system_plugins = tmp_path / "usr" / "libexec" / "docker" / "cli-plugins"
    user_plugins = tmp_path / "home" / ".docker" / "cli-plugins"
    system_plugins.mkdir(parents=True)
    for plugin in ("compose", "buildx"):
        binary = system_plugins / f"docker-{plugin}"
        binary.write_text("#!/bin/sh\n", encoding="utf-8")
        binary.chmod(0o755)

    monkeypatch.setattr(configure_docker_dx, "SYSTEM_PLUGIN_DIRS", (system_plugins,))
    monkeypatch.setattr(configure_docker_dx, "USER_PLUGIN_DIR", user_plugins)

    assert configure_docker_dx.ensure_user_cli_plugin_links(dry_run=False) == ["compose", "buildx"]
    assert (user_plugins / "docker-compose").resolve() == system_plugins / "docker-compose"
    assert (user_plugins / "docker-buildx").resolve() == system_plugins / "docker-buildx"
    assert configure_docker_dx.ensure_user_cli_plugin_links(dry_run=False) == []
