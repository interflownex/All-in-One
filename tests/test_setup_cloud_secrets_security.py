from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts import setup_cloud_secrets

ROOT = Path(__file__).resolve().parents[1]


def test_setup_script_contains_no_literal_credentials() -> None:
    source = (ROOT / "scripts/setup_cloud_secrets.py").read_text(encoding="utf-8")

    assert "result.stderr" not in source
    assert re.search(r"postgres(?:ql)?://[^\s\"']+:[^@\s\"']+@", source) is None
    assert set(setup_cloud_secrets.SECRET_ENV_BY_ID.values()) == {
        "AIO_IDENTITY_DSN",
        "AIO_JWT_SECRET",
        "AIO_DOCUMENT_ENCRYPTION_KEY",
    }


def test_configuration_requires_project_and_all_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GCP_PROJECT_ID",
        "AIO_IDENTITY_DSN",
        "AIO_JWT_SECRET",
        "AIO_DOCUMENT_ENCRYPTION_KEY",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(ValueError) as exc_info:
        setup_cloud_secrets._load_configuration()

    message = str(exc_info.value)
    assert "GCP_PROJECT_ID" in message
    assert "AIO_IDENTITY_DSN" in message
    assert "AIO_JWT_SECRET" in message
    assert "AIO_DOCUMENT_ENCRYPTION_KEY" in message


def test_configuration_loads_payloads_only_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GCP_PROJECT_ID", "project-test")
    monkeypatch.setenv("AIO_IDENTITY_DSN", "dsn-from-env")
    monkeypatch.setenv("AIO_JWT_SECRET", "jwt-from-env")
    monkeypatch.setenv("AIO_DOCUMENT_ENCRYPTION_KEY", "key-from-env")

    project_id, payloads = setup_cloud_secrets._load_configuration()

    assert project_id == "project-test"
    assert payloads == {
        "identity-dsn": "dsn-from-env",
        "jwt-secret": "jwt-from-env",
        "document-encryption-key": "key-from-env",
    }


def test_secret_creation_and_versioning_emit_no_sensitive_metadata(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: list[tuple[list[str], str | None]] = []
    return_codes = iter([1, 0, 0])

    def fake_run(command: list[str], *, input_text: str | None = None) -> int:
        calls.append((command, input_text))
        return next(return_codes)

    monkeypatch.setattr(setup_cloud_secrets, "_run_quiet", fake_run)
    payload = "payload-that-must-not-appear"
    secret_id = "jwt-secret"

    setup_cloud_secrets.configure_secret("project-test", secret_id, payload)

    output = capsys.readouterr()
    assert payload not in output.out
    assert payload not in output.err
    assert secret_id not in output.out
    assert secret_id not in output.err
    assert output.out.strip() == "Segredo configurado com nova versão."
    assert [call[0][2] for call in calls] == ["describe", "create", "versions"]
    assert calls[-1][1] == payload
