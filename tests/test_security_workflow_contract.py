from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"

REQUIRED_JAVASCRIPT_AUDIT_TARGETS = {
    "apps/all-in-one",
    "apps/all-in-one-business",
    "apps/all-in-one-health",
    "apps/all-in-one-mobility",
    "apps/all-in-one-riders",
    "apps/all-in-one-services",
    "apps/valley",
    "apps/valley_business",
    "apps/valley_rider",
    "desktop/valley-erp",
}


def test_security_workflow_keeps_python_and_javascript_scans_blocking() -> None:
    workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")

    assert "pip-audit -r requirements-dev.txt" in workflow
    assert "pip-audit --local" not in workflow
    assert "bandit -r modules/shared scripts workers -q -ll" in workflow
    assert "javascript-security:" in workflow
    assert "npm audit --omit=dev --audit-level=critical" in workflow
    assert "fail-fast: false" in workflow

    for target in REQUIRED_JAVASCRIPT_AUDIT_TARGETS:
        assert f"- {target}" in workflow
        assert (ROOT / target / "package-lock.json").is_file()


def test_codeql_analyzes_pull_requests_without_duplicate_sarif_upload() -> None:
    workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")

    assert "github/codeql-action/init@v4" in workflow
    assert "github/codeql-action/analyze@v4" in workflow
    assert "build-mode: manual" in workflow
    assert "testProductionDebugUnitTest lintProductionDebug assembleProductionDebug" in workflow
    assert "upload: ${{ github.event_name == 'pull_request' && 'never' || 'always' }}" in workflow
    assert "output: codeql-results" in workflow
    assert "post-processed-sarif-path" not in workflow
    assert "name: valley-android-codeql-sarif" in workflow
    assert "if-no-files-found: error" in workflow
