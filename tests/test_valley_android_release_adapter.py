from pathlib import Path

from scripts import validate_valley_android_release_v29 as contract


ROOT = Path(__file__).resolve().parents[1]
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "valley-android-release.yml"
SECURITY_WORKFLOW = ROOT / ".github" / "workflows" / "security.yml"


def test_release_workflow_uses_v29_contract_adapter() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert "python scripts/validate_valley_android_release_v29.py" in workflow
    assert "python scripts/validate_valley_android_release.py\n" not in workflow


def test_release_workflow_uses_current_actions() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert contract.validate_release_workflow(workflow) == []
    assert contract.CURRENT_UPLOAD_ACTION in workflow
    assert contract.OBSOLETE_UPLOAD_ACTION not in workflow
    assert contract.CURRENT_ATTEST_ACTION in workflow
    assert contract.OBSOLETE_ATTEST_ACTION not in workflow


def test_security_workflow_uses_explicit_production_debug_tasks() -> None:
    workflow = SECURITY_WORKFLOW.read_text(encoding="utf-8")

    assert contract.validate_security_workflow(workflow) == []
    assert contract.EXPLICIT_TASKS in workflow
    assert contract.OBSOLETE_TASKS not in workflow


def test_adapter_rejects_legacy_ambiguous_tasks() -> None:
    errors = contract.validate_security_workflow(contract.OBSOLETE_TASKS)

    assert any("genéricas e ambíguas" in error for error in errors)
    assert any("tarefas Android explícitas ausentes" in error for error in errors)


def test_adapter_rejects_legacy_upload_action() -> None:
    errors = contract.validate_release_workflow(contract.OBSOLETE_UPLOAD_ACTION)

    assert any("ação obsoleta de publicação" in error for error in errors)
    assert any("ação atual de publicação" in error for error in errors)


def test_adapter_rejects_legacy_attestation_action() -> None:
    errors = contract.validate_release_workflow(contract.OBSOLETE_ATTEST_ACTION)

    assert any("ação obsoleta de atestação" in error for error in errors)
    assert any("ação atual de atestação" in error for error in errors)
