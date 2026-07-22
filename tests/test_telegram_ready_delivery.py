from __future__ import annotations

import json
from pathlib import Path

from scripts import send_ready_artifact_to_telegram as delivery

ROOT = Path(__file__).resolve().parents[1]


def test_policy_covers_web_and_app_without_credentials() -> None:
    policy = json.loads(
        (ROOT / "config/autonomy/telegram_delivery_policy.json").read_text(
            encoding="utf-8"
        )
    )
    assert policy["enabled"] is True
    assert set(policy["targets"]) == {"web", "app"}
    assert policy["credentials_outside_git"] is True
    assert set(policy["required_secrets"]) == {"TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"}


def test_delivery_requires_verified_gate(capsys) -> None:
    result = delivery.main(
        [
            "--kind",
            "web",
            "--version",
            "abc123",
            "--url",
            "https://all-in-one-web.pages.dev",
            "--telegram-token",
            "token-local",
            "--telegram-chat-id",
            "chat-local",
        ]
    )
    assert result == 2
    assert "--verified" in capsys.readouterr().err


def test_web_delivery_requires_https(capsys) -> None:
    result = delivery.main(
        [
            "--kind",
            "web",
            "--version",
            "abc123",
            "--url",
            "http://localhost:5173",
            "--verified",
            "--telegram-token",
            "token-local",
            "--telegram-chat-id",
            "chat-local",
        ]
    )
    assert result == 2
    assert "HTTPS" in capsys.readouterr().err


def test_app_delivery_requires_existing_apk(capsys, tmp_path) -> None:
    result = delivery.main(
        [
            "--kind",
            "app",
            "--version",
            "1.0.0",
            "--artifact",
            str(tmp_path / "missing.apk"),
            "--verified",
            "--telegram-token",
            "token-local",
            "--telegram-chat-id",
            "chat-local",
        ]
    )
    assert result == 2
    assert "APK instalavel nao encontrado" in capsys.readouterr().err


def test_web_identity_rejects_wrong_site(monkeypatch) -> None:
    class WrongSiteResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self) -> bytes:
            return b"<title>AIO Bot - Telegram File Bot</title>"

    monkeypatch.setattr(
        delivery.request, "urlopen", lambda *_args, **_kwargs: WrongSiteResponse()
    )
    try:
        delivery.verify_web_identity("https://example.pages.dev", "All-in-One")
    except RuntimeError as exc:
        assert "Identidade web invalida" in str(exc)
    else:
        raise AssertionError("Site incorreto nao pode ser tratado como ambiente pronto")
