from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.check_git_sync import parse_commit_parents

ROOT = Path(__file__).resolve().parents[1]


def test_git_sync_workflow_uses_python_gate() -> None:
    workflow = (ROOT / ".github/workflows/git-sync.yml").read_text(encoding="utf-8")

    assert (
        "python3 scripts/check_git_sync.py --branch main --remotes origin --allow-dirty"
    ) in workflow
    assert "shell: pwsh" not in workflow


def test_git_sync_python_gate_compiles() -> None:
    subprocess.run(
        ["python3", "-m", "py_compile", "scripts/check_git_sync.py"],
        cwd=ROOT,
        check=True,
    )


def test_parse_commit_parents_reads_shallow_merge_headers() -> None:
    first = "1" * 40
    second = "2" * 40
    commit = (
        f"tree {'a' * 40}\n"
        f"parent {first}\n"
        f"parent {second}\n"
        "author Example <example@example.test> 0 +0000\n\nmessage\n"
    )

    assert parse_commit_parents(commit) == (first, second)


def test_parse_commit_parents_rejects_invalid_identifiers() -> None:
    assert parse_commit_parents("parent not-a-sha\nparent ABCD\n") == ()


def test_git_sync_python_gate_accepts_an_ahead_explicit_branch_when_allowed() -> None:
    subprocess.run(
        [
            "python3",
            "scripts/check_git_sync.py",
            "--branch",
            "main",
            "--remotes",
            "origin",
            "--allow-dirty",
            "--allow-ahead",
            "--no-fetch",
        ],
        cwd=ROOT,
        check=True,
    )


def test_git_sync_python_gate_uses_upstream_branch_by_default() -> None:
    subprocess.run(
        [
            "python3",
            "scripts/check_git_sync.py",
            "--remotes",
            "origin",
            "--allow-dirty",
            "--no-fetch",
        ],
        cwd=ROOT,
        check=True,
    )
