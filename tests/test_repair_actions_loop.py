from __future__ import annotations

from pathlib import Path

from scripts.repair_actions_loop import (
    build_repair_bundle,
    current_workflow_failures,
    extract_run_id,
    latest_workflow_runs,
)


ROOT = Path(__file__).resolve().parents[1]


def test_extract_run_id_from_actions_url() -> None:
    url = "https://github.com/interflownex/All-In-One/actions/runs/28706839124/job/85134556557"
    assert extract_run_id(url) == "28706839124"


def test_latest_workflow_runs_prefers_most_recent_result() -> None:
    runs = [
        {
            "workflowName": "Continuous Integration",
            "conclusion": "failure",
            "createdAt": "2026-07-04T12:53:16Z",
            "databaseId": 1,
            "url": "https://github.com/interflownex/All-In-One/actions/runs/1",
        },
        {
            "workflowName": "Continuous Integration",
            "conclusion": "success",
            "createdAt": "2026-07-04T13:04:53Z",
            "databaseId": 2,
            "url": "https://github.com/interflownex/All-In-One/actions/runs/2",
        },
        {
            "workflowName": "Security",
            "conclusion": "failure",
            "createdAt": "2026-07-04T13:00:00Z",
            "databaseId": 3,
            "url": "https://github.com/interflownex/All-In-One/actions/runs/3",
        },
    ]

    latest = latest_workflow_runs(runs)
    assert [run["workflowName"] for run in latest] == ["Continuous Integration", "Security"]

    failures = current_workflow_failures(runs)
    assert [run["workflowName"] for run in failures] == ["Security"]


def test_build_repair_bundle_uses_given_python_executable() -> None:
    bundle = build_repair_bundle("/venv/bin/python")
    assert bundle[0] == ("/venv/bin/python", "scripts/scaffold_modules.py")
    assert bundle[1] == ("/venv/bin/python", "scripts/generate_domain_event_fixtures.py")
    assert bundle[2] == ("/venv/bin/python", "scripts/check_generated_artifacts.py")
    assert bundle[3] == ("/venv/bin/python", "scripts/validate_openapi.py")
    assert bundle[4] == ("/venv/bin/python", "scripts/validate_repository.py")
    assert bundle[5][:4] == ("/venv/bin/python", "-m", "pytest", "-q")


def test_repair_loop_workflow_contains_pr_push_triggers() -> None:
    workflow = (ROOT / ".github" / "workflows" / "repair-loop.yml").read_text(encoding="utf-8")
    for needle in [
        "workflow_dispatch:",
        "push:",
        "pull_request:",
        "schedule:",
        "scripts/repair_actions_loop.py",
        "GH_TOKEN: ${{ github.token }}",
        "--continuous",
        "--max-cycles 1",
    ]:
        assert needle in workflow
