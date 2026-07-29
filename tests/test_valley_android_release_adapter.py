from pathlib import Path

from scripts import validate_valley_android_release_v29 as contract


ROOT = Path(__file__).resolve().parents[1]
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "valley-android-release.yml"
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"


def test_release_workflow_uses_v29_contract_adapter() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert "python scripts/validate_valley_android_release_v29.py" in workflow
    assert "python scripts/validate_valley_android_release.py\n" not in workflow


def test_security_workflow_uses_explicit_production_debug_tasks() -> None:
    workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")

    assert contract.validate_security_workflow(workflow) == []
    assert contract.EXPLICIT_TASKS in workflow
    assert contract.OBSOLETE_TASKS not in workflow


def test_adapter_rejects_legacy_ambiguous_tasks() -> None:
    errors = contract.validate_security_workflow(contract.OBSOLETE_TASKS)

    assert any("genéricas e ambíguas" in error for error in errors)
    assert any("tarefas Android explícitas ausentes" in error for error in errors)
