from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from urllib import error

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "telegram_activity_reporter.py"


def load_module():
    spec = importlib.util.spec_from_file_location("telegram_activity_reporter", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_policy(tmp_path: Path) -> Path:
    policy = {
        "version": 2,
        "enabled": True,
        "credentials_outside_git": True,
        "activity_notifications": {
            "enabled": True,
            "events": ["activity_started", "activity_completed"],
        },
        "developer_pending_reports": {"enabled": True},
    }
    path = tmp_path / "telegram_policy.json"
    path.write_text(json.dumps(policy), encoding="utf-8")
    return path


def test_activity_started_dry_run_without_credentials(tmp_path, capsys) -> None:
    module = load_module()
    policy = write_policy(tmp_path)

    result = module.main(
        [
            "--policy",
            str(policy),
            "--dry-run",
            "activity-started",
            "--activity-name",
            "Revisar documentação",
            "--technical-description",
            "Cruzar documentos e código",
            "--estimated-completion-time",
            "2 horas",
            "--reported-difficulty",
            "4",
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["event"] == "activity_started"
    assert payload["sent"] is False
    assert "Revisar documentação" in payload["message"]


def test_completed_report_contains_pending_items(tmp_path, capsys) -> None:
    module = load_module()
    policy = write_policy(tmp_path)

    result = module.main(
        [
            "--policy",
            str(policy),
            "--dry-run",
            "activity-completed",
            "--activity-name",
            "Executor Telegram",
            "--status",
            "partial_success",
            "--completion-percent",
            "60",
            "--pending-item",
            "Configurar secrets",
            "--next-step",
            "Executar testes",
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["event"] == "activity_completed"
    assert "Configurar secrets" in payload["message"]
    assert "Executar testes" in payload["message"]


def test_pending_report_accepts_only_four_indices(tmp_path) -> None:
    module = load_module()
    policy = module.load_policy(write_policy(tmp_path))
    parser = module.build_parser()
    args = parser.parse_args(
        [
            "--policy",
            str(write_policy(tmp_path)),
            "--dry-run",
            "pending-report",
            "--report-index",
            "5",
            "--risk-summary",
            "Risco",
            "--eta-summary",
            "Prazo",
        ]
    )

    with pytest.raises(module.ReporterError, match="entre 1 e 4"):
        module.render_event(args, policy)


def test_send_message_retries_transient_error() -> None:
    module = load_module()
    attempts = 0

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return b'{"ok": true}'

    def fake_urlopen(_request, timeout):
        nonlocal attempts
        assert timeout == 3
        attempts += 1
        if attempts == 1:
            raise error.URLError("temporário")
        return Response()

    module.send_message(
        "token-de-teste",
        "chat-de-teste",
        "mensagem",
        timeout=3,
        retries=2,
        urlopen=fake_urlopen,
        sleeper=lambda _seconds: None,
    )

    assert attempts == 2


def test_invalid_policy_never_allows_git_credentials(tmp_path) -> None:
    module = load_module()
    path = tmp_path / "invalid.json"
    path.write_text(
        json.dumps(
            {
                "version": 2,
                "enabled": True,
                "credentials_outside_git": False,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(module.ReporterError, match="fora do Git"):
        module.load_policy(path)
