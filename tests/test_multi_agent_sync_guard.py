from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from scripts import multi_agent_sync_guard as guard


def test_lock_blocks_a_second_agent(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "agent.lock"
    monkeypatch.setattr(guard, "lock_path", lambda scope="workspace": path)

    acquired = guard.acquire_lock("codex_cli", "catalogo Valley", 120)

    assert acquired["agent"] == "codex_cli"
    with pytest.raises(RuntimeError, match="Escopo 'workspace' em uso"):
        guard.acquire_lock("antigravity", "outra atividade", 120)


def test_stale_lock_can_be_replaced(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "agent.lock"
    path.write_text(
        (
            '{"agent":"agente_antigo","pid":1,'
            f'"acquired_at":"{(datetime.now(UTC) - timedelta(hours=3)).isoformat()}"'
            "}"
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(guard, "lock_path", lambda scope="workspace": path)

    acquired = guard.acquire_lock("codex_cli", "retomada segura", 120)

    assert acquired["agent"] == "codex_cli"
    assert guard.read_lock(path)["activity"] == "retomada segura"


def test_release_refuses_another_agent(monkeypatch, tmp_path: Path) -> None:
    path = tmp_path / "agent.lock"
    monkeypatch.setattr(guard, "lock_path", lambda scope="workspace": path)
    guard.acquire_lock("codex_cli", "catalogo Valley", 120)

    with pytest.raises(RuntimeError, match="Lock pertence"):
        guard.release_lock("gemini_code")

    guard.release_lock("codex_cli")
    assert not path.exists()


def test_same_agent_renews_lock_from_another_process(
    monkeypatch, tmp_path: Path
) -> None:
    path = tmp_path / "agent.lock"
    monkeypatch.setattr(guard, "lock_path", lambda scope="workspace": path)
    original = guard.acquire_lock("codex_cli", "primeira etapa", 120)
    renewed = guard.acquire_lock("codex_cli", "segunda etapa", 120)

    assert renewed["activity"] == "segunda etapa"
    assert renewed["acquired_at"] >= original["acquired_at"]


def test_scoped_locks_allow_independent_activities(monkeypatch, tmp_path: Path) -> None:
    def scoped_path(scope: str = "workspace") -> Path:
        return tmp_path / f"{scope}.lock"

    monkeypatch.setattr(guard, "lock_path", scoped_path)

    guard.acquire_lock("codex_cli", "scripts", 120, "scripts")
    acquired = guard.acquire_lock("antigravity", "frontend", 120, "frontend")

    assert acquired["scope"] == "frontend"
