import json
import subprocess
import sys
from pathlib import Path

from scripts.codex_stitch_director import validate_policy
from scripts.stitch_template_project_sync import load_coordinate, load_state

ROOT = Path(__file__).resolve().parents[1]


def run_director(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/codex_stitch_director.py", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_policy_declares_four_official_projects_and_excludes_vision() -> None:
    coordinate = load_coordinate()
    state = load_state()
    assert validate_policy(coordinate, state) == []
    assert len(coordinate["projects"]) == 4
    assert {project["id"] for project in coordinate["projects"]} == {
        "valley_apk_template",
        "all_in_one_web_mobile_template",
        "valley_riders_apk_template",
        "aio_admin_web_mobile_template",
    }
    assert '"vision"' not in json.dumps(coordinate, ensure_ascii=False).casefold()


def test_plan_reports_aio_admin_as_authorized_missing_project() -> None:
    result = run_director("plan")
    assert result.returncode == 0, result.stderr
    plan = json.loads(result.stdout)
    assert plan["coordinator"] == "codex"
    assert plan["official_projects"] == 4
    assert plan["screen_groups"] == 32
    assert plan["missing_projects"] == ["aio_admin_web_mobile_template"]


def test_status_reports_checkpoint_gaps_without_failing_validation_job() -> None:
    result = run_director("status", "--actor", "pytest")
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["expected_projects"] == 4
    assert summary["synced_projects"] == 3
    assert summary["expected_screen_groups"] == 32
    assert summary["synced_screen_groups"] == 24
    assert summary["pending_screen_groups"] == 8


def test_require_complete_rejects_unsynchronized_remote_checkpoint() -> None:
    result = run_director("status", "--require-complete", "--actor", "pytest")
    assert result.returncode == 1
    summary = json.loads(result.stdout)
    assert summary["pending_screen_groups"] == 8


def test_legacy_remote_writer_is_blocked() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/stitch_auto_sync.py", "--require-remote"],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 2
    assert "sincronizacao remota legada por modulo foi desativada" in result.stdout


def test_governance_files_do_not_contain_literal_secret_assignments() -> None:
    paths = [
        ROOT / "config" / "autonomy" / "codex_stitch_director_policy.json",
        ROOT / "config" / "autonomy" / "google_integrations_policy.json",
        ROOT / ".github" / "workflows" / "stitch-sync.yml",
    ]
    forbidden = (
        "AIza",
        "-----BEGIN PRIVATE KEY-----",
        "ghp_",
        "github_pat_",
        "sk-proj-",
    )
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert not any(token in combined for token in forbidden)
