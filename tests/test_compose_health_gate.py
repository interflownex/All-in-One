from __future__ import annotations

import subprocess
from pathlib import Path

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


def test_compose_health_workflow_runs_python_gate_instead_of_sleep_only() -> None:
    workflow = (ROOT / ".github/workflows/compose-health.yml").read_text(encoding="utf-8")

    assert (
        "python3 scripts/validate_compose_health.py --down-after --timeout-seconds 600 "
        "--probe-timeout-seconds 1"
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


def test_compose_health_gate_compiles() -> None:
    subprocess.run(
        ["python3", "-m", "py_compile", "scripts/validate_compose_health.py"],
        cwd=ROOT,
        check=True,
    )
