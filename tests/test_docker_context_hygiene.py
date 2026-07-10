from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dockerignore_keeps_runtime_build_context_small() -> None:
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")

    required_entries = {
        ".git",
        ".venv",
        ".pytest_cache",
        ".pytest_tmp",
        "node_modules",
        ".env",
        ".env.*",
        "!.env.example",
        "tests",
        "apps",
        "docs",
        "reports",
        "*.pdf",
    }

    assert required_entries <= set(dockerignore.splitlines())


def test_compose_builds_from_repo_root_where_dockerignore_applies() -> None:
    compose = (ROOT / "infra/docker/docker-compose.yml").read_text(encoding="utf-8")

    assert "context: ../.." in compose
    assert (ROOT / ".dockerignore").is_file()
