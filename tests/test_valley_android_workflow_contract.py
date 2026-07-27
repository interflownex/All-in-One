from scripts.validate_valley_android_release_v29 import (
    EXPLICIT_TASKS,
    OBSOLETE_TASKS,
    validate_security_workflow,
)


def test_explicit_production_debug_tasks_are_accepted() -> None:
    assert validate_security_workflow(EXPLICIT_TASKS) == []


def test_generic_debug_tasks_are_rejected() -> None:
    errors = validate_security_workflow(OBSOLETE_TASKS)

    assert errors
    assert any("ambíguas" in error for error in errors)
    assert any(EXPLICIT_TASKS in error for error in errors)
