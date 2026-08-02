from __future__ import annotations

import subprocess

from scripts import configure_data_agent_kit


def test_runtime_status_tolerates_slow_gcloud(tmp_path, monkeypatch) -> None:
    observed: dict[str, int] = {}
    gcloud = tmp_path / "gcloud"
    gcloud.touch()
    monkeypatch.setattr(configure_data_agent_kit, "LINUX_GCLOUD", gcloud)

    def fake_run(*args, **kwargs):
        observed["timeout"] = kwargs["timeout"]
        return subprocess.CompletedProcess(args[0], 0)

    monkeypatch.setattr(configure_data_agent_kit.subprocess, "run", fake_run)

    status = configure_data_agent_kit.runtime_status()

    assert status["enabled"] is False
    assert status["application_default_credentials_available"] is True
    assert status["runtime_warning"] is None
    assert (
        observed["timeout"] == configure_data_agent_kit.GCLOUD_RUNTIME_TIMEOUT_SECONDS
    )
    assert observed["timeout"] >= 30


def test_runtime_status_reports_configured_timeout(tmp_path, monkeypatch) -> None:
    gcloud = tmp_path / "gcloud"
    gcloud.touch()
    monkeypatch.setattr(configure_data_agent_kit, "LINUX_GCLOUD", gcloud)

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(configure_data_agent_kit.subprocess, "run", fake_run)

    status = configure_data_agent_kit.runtime_status(timeout_seconds=7)

    assert status["application_default_credentials_available"] is False
    assert status["runtime_warning"] == (
        "gcloud excedeu 7s ao verificar Application Default Credentials."
    )
