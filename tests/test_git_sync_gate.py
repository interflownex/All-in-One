from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_git_sync_workflow_uses_python_gate() -> None:
    workflow = (ROOT / ".github/workflows/git-sync.yml").read_text(encoding="utf-8")

    assert (
        "python3 scripts/check_git_sync.py --branch main --remotes origin "
        "--allow-dirty"
    ) in workflow
    assert "shell: pwsh" not in workflow


def test_git_sync_python_gate_compiles() -> None:
    subprocess.run(
        ["python3", "-m", "py_compile", "scripts/check_git_sync.py"],
        cwd=ROOT,
        check=True,
    )


def test_git_sync_python_gate_accepts_current_origin_alignment() -> None:
    subprocess.run(
        [
            "python3",
            "scripts/check_git_sync.py",
            "--branch",
            "main",
            "--remotes",
            "origin",
            "--allow-dirty",
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
