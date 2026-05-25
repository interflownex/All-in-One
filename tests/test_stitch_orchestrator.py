import json

from scripts.stitch_orchestrator import MANIFEST_PATH, build_manifest, load_catalog, screen_prompt, versioned_manifest


def test_manifest_creates_one_project_per_microservice_and_jobs_surfaces() -> None:
    manifest = build_manifest(load_catalog())
    assert manifest["project_count"] == 25
    assert len({project["module"] for project in manifest["projects"]}) == 25
    jobs = next(project for project in manifest["projects"] if project["module"] == "jobs")
    assert jobs["integrated_apps"] == ["all-in-one-user", "all-in-one-business"]
    assert {"candidate_resume", "ctps_import", "vacancy_search", "recruiter_resume_review"}.issubset(
        {screen["key"] for screen in jobs["screens"]}
    )


def test_prompts_never_embed_credentials_or_private_document_content() -> None:
    module = next(item for item in load_catalog()["modules"] if item["slug"] == "jobs")
    prompt = screen_prompt(module, "ctps_import", "Importacao documental segura.", ["all-in-one-user"])
    normalized = prompt.lower()
    assert "api key" not in normalized
    assert "chaves" in normalized
    assert "documentos brutos" in normalized
    assert "prontuario" in normalized
    json.dumps(build_manifest(load_catalog()))


def test_versioned_manifest_matches_catalog_generation() -> None:
    stored = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert stored == versioned_manifest(build_manifest(load_catalog()))
