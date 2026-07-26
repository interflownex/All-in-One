import json
import subprocess
import sys
from pathlib import Path

from scripts.stitch_orchestrator import (
    MANIFEST_PATH,
    brand_prompt,
    build_manifest,
    load_catalog,
    screen_prompt,
    sync_summary,
    versioned_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_creates_one_project_per_microservice_and_jobs_surfaces() -> None:
    manifest = build_manifest(load_catalog())
    expected_count = len(load_catalog()["modules"])
    assert manifest["project_count"] == expected_count
    assert len({project["module"] for project in manifest["projects"]}) == expected_count
    jobs = next(
        project for project in manifest["projects"] if project["module"] == "jobs"
    )
    assert jobs["integrated_apps"] == ["all-in-one-user", "all-in-one-business"]
    assert {
        "candidate_resume",
        "ctps_import",
        "vacancy_search",
        "recruiter_resume_review",
    }.issubset({screen["key"] for screen in jobs["screens"]})


def test_prompts_never_embed_credentials_or_private_document_content() -> None:
    module = next(item for item in load_catalog()["modules"] if item["slug"] == "jobs")
    prompt = screen_prompt(
        module, "ctps_import", "Importacao documental segura.", ["all-in-one-user"]
    )
    normalized = prompt.lower()
    assert "api key" not in normalized
    assert "chaves" in normalized
    assert "documentos brutos" in normalized
    assert "prontuario" in normalized
    json.dumps(build_manifest(load_catalog()))


def test_prompts_apply_all_in_one_and_valley_official_branding() -> None:
    module = next(
        item for item in load_catalog()["modules"] if item["slug"] == "marketplace"
    )
    prompt = screen_prompt(
        module, "overview", "Catalogo Valley.", ["all-in-one-user", "valley"]
    )
    assert "assets/brand/all-in-one-logo-official.png" in prompt
    assert "assets/brand/valley-logo-official.png" in prompt
    assert "Nao redesenhe, distorca, corte, rotacione ou recolora" in prompt


def test_non_valley_prompt_keeps_platform_brand_without_valley_logo() -> None:
    prompt = brand_prompt(["all-in-one-business"])
    assert "assets/brand/all-in-one-logo-official.png" in prompt
    assert "assets/brand/valley-logo-official.png" not in prompt


def test_versioned_manifest_matches_catalog_generation() -> None:
    stored = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert stored == versioned_manifest(build_manifest(load_catalog()))


def test_sync_summary_reports_remote_gaps_without_credentials() -> None:
    manifest = build_manifest(load_catalog())
    summary = sync_summary(manifest, {"schema_version": 1, "projects": {}})
    assert summary["expected_projects"] == len(load_catalog()["modules"])
    assert summary["synced_projects"] == 0
    assert summary["expected_screens"] == manifest["screen_count"]
    assert summary["synced_screens"] == 0
    assert summary["branding_pending"] == {}
    assert set(summary["missing_projects"]) == {
        project["module"] for project in manifest["projects"]
    }


def test_sync_summary_reports_branding_pending_for_legacy_screens() -> None:
    manifest = build_manifest(load_catalog())
    first = manifest["projects"][0]
    first_screen = first["screens"][0]
    state = {
        "schema_version": 1,
        "projects": {
            first["module"]: {
                "project_id": "123",
                "screens": {
                    first_screen["key"]: {
                        "screen_id": "abc",
                        "name": first_screen["name"],
                    }
                },
            }
        },
    }
    summary = sync_summary(manifest, state)
    assert summary["branding_pending"][first["module"]] == [first_screen["key"]]


def test_stitch_auto_sync_dry_run_is_safe_and_does_not_require_remote_secret() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/stitch_auto_sync.py", "--dry-run"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    summary = json.loads(result.stdout)
    assert summary["expected_projects"] == len(load_catalog()["modules"])
    assert summary["expected_screens"] > 0


def test_stitch_remote_sync_workflow_is_active_and_secret_driven() -> None:
    workflow = (ROOT / ".github" / "workflows" / "stitch-sync.yml").read_text(
        encoding="utf-8"
    )
    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert "branches: [main]" in workflow
    assert "if: ${{ false }}" not in workflow
    assert 'STITCH_REMOTE_SYNC_ENABLED: "true"' in workflow
    assert "secrets.STITCH_API_KEY" in workflow
    assert "python scripts/stitch_auto_sync.py --require-remote" in workflow
    assert "--require-complete" not in workflow
    assert "config/stitch/sync_state.json" in workflow
