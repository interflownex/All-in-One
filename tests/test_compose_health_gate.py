from __future__ import annotations

import subprocess
from pathlib import Path
import yaml

from scripts import validate_compose_health


ROOT = Path(__file__).resolve().parents[1]


def test_compose_health_gate_tracks_primary_fastapi_services() -> None:
    probes = validate_compose_health.SERVICE_PROBES

    assert len(probes) == 13
    assert {probe.name for probe in probes} == {
        "api-hub",
        "identity",
        "finance",
        "marketplace",
        "delivery",
        "services",
        "mobility",
        "erp",
        "wms",
        "tms",
        "crm",
        "health",
        "jobs",
    }
    assert {probe.port for probe in probes} == set(range(8100, 8113))


def test_compose_postgres_healthcheck_allows_cold_initdb() -> None:
    compose = yaml.safe_load((ROOT / "infra/docker/docker-compose.yml").read_text(encoding="utf-8"))

    postgres_healthcheck = compose["services"]["postgres"]["healthcheck"]

    assert postgres_healthcheck["start_period"] == "120s"
    assert postgres_healthcheck["interval"] == "5s"
    assert postgres_healthcheck["retries"] == 12


def test_compose_health_workflow_runs_python_gate_instead_of_sleep_only() -> None:
    workflow = (ROOT / ".github/workflows/compose-health.yml").read_text(encoding="utf-8")

    assert "timeout-minutes: 30" in workflow
    assert (
        "python3 scripts/validate_compose_health.py --env-file .env.docker-dx --project-name all-in-one-dx "
        "--require-free-ports --down-after --command-timeout-seconds 900 --timeout-seconds 600 --probe-timeout-seconds 1"
    ) in workflow
    assert "sleep 30" not in workflow
    assert "docker compose -f infra/docker/docker-compose.yml up --build -d" not in workflow


def test_compose_health_gate_reports_pending_services(monkeypatch) -> None:
    attempts: list[str] = []

    def fake_is_healthy(probe: validate_compose_health.ServiceProbe, timeout_seconds: float) -> bool:
        attempts.append(probe.name)
        return probe.name == "api-hub"

    monkeypatch.setattr(validate_compose_health, "is_healthy", fake_is_healthy)
    monkeypatch.setattr(validate_compose_health.time, "sleep", lambda seconds: None)

    pending = validate_compose_health.wait_for_health(timeout_seconds=0, probe_timeout_seconds=0.01)

    assert "api-hub" in pending
    assert "identity" in pending
    assert attempts == []


def test_compose_health_gate_times_out_docker_commands(monkeypatch) -> None:
    calls: list[tuple[list[str], int]] = []

    def fake_run(args, cwd, check, timeout):
        calls.append((args, timeout))
        return subprocess.CompletedProcess(args=args, returncode=0)

    monkeypatch.setattr(validate_compose_health.subprocess, "run", fake_run)

    validate_compose_health.run_checked(["docker", "compose", "config", "--quiet"], timeout_seconds=123)

    assert calls == [(["docker", "compose", "config", "--quiet"], 123)]


def test_compose_health_gate_accepts_env_file_and_project_name(monkeypatch, tmp_path) -> None:
    compose_file = tmp_path / "compose.yml"
    env_file = tmp_path / ".env"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    env_file.write_text("COMPOSE_PROJECT_NAME=all-in-one-dx\n", encoding="utf-8")
    calls: list[list[str]] = []

    def fake_run_checked(args: list[str], timeout_seconds: int) -> None:
        calls.append(args)

    monkeypatch.setattr(validate_compose_health, "run_checked", fake_run_checked)
    monkeypatch.setattr(validate_compose_health, "wait_for_health", lambda *args: set())

    result = validate_compose_health.main([
        "--compose-file",
        str(compose_file),
        "--env-file",
        str(env_file),
        "--project-name",
        "all-in-one-dx",
        "--skip-build",
    ])

    assert result == 0
    assert calls[0] == [
        "docker",
        "compose",
        "--env-file",
        str(env_file),
        "--project-name",
        "all-in-one-dx",
        "-f",
        str(compose_file),
        "config",
        "--quiet",
    ]
    assert calls[1][-2:] == ["-d", "--no-build"]


def test_compose_health_gate_can_fail_fast_on_occupied_ports(monkeypatch, tmp_path, capsys) -> None:
    compose_file = tmp_path / "compose.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")
    monkeypatch.setattr(validate_compose_health, "bound_ports", lambda: [8103, 8110])

    result = validate_compose_health.main([
        "--compose-file",
        str(compose_file),
        "--require-free-ports",
        "--skip-build",
    ])

    assert result == 1
    assert "8103, 8110" in capsys.readouterr().err


def test_compose_health_gate_compiles() -> None:
    subprocess.run(
        ["python3", "-m", "py_compile", "scripts/validate_compose_health.py"],
        cwd=ROOT,
        check=True,
    )
