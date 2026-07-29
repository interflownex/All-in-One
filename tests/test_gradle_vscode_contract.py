import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VSCODE_SETTINGS = ROOT / ".vscode" / "settings.json"
WORKSPACE_SETTINGS = ROOT / "all-in-one.code-workspace"
VSCODE_TASKS = ROOT / ".vscode" / "tasks.json"
GITIGNORE = ROOT / ".gitignore"
WRAPPER_PROPERTIES = (
    ROOT
    / "apps"
    / "valley-android"
    / "gradle"
    / "wrapper"
    / "gradle-wrapper.properties"
)

REQUIRED_GRADLE_SETTINGS = {
    "gradle.autoDetect": "off",
    "gradle.nestedProjects": ["apps/valley-android"],
    "java.import.gradle.enabled": True,
    "java.import.gradle.wrapper.enabled": True,
    "java.configuration.updateBuildConfiguration": "interactive",
    "java.gradle.buildServer.enabled": "off",
}

REQUIRED_PYLANCE_EXCLUSIONS = {
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.git/**",
    "**/.venv/**",
    "**/venv/**",
    "**/.pytest_cache/**",
    "**/.mypy_cache/**",
    "**/.ruff_cache/**",
    "**/dist/**",
    "**/build/**",
    "**/testcontainers-cloud-java-example/**",
}

REQUIRED_JAVA_IMPORT_EXCLUSIONS = {
    "**/node_modules/**",
    "**/.git/**",
    "**/testcontainers-cloud-java-example/**",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_gradle_server_is_not_started_automatically() -> None:
    folder_settings = _load_json(VSCODE_SETTINGS)
    workspace_settings = _load_json(WORKSPACE_SETTINGS)["settings"]

    for key, expected in REQUIRED_GRADLE_SETTINGS.items():
        assert folder_settings[key] == expected
        assert workspace_settings[key] == expected


def test_local_sample_is_excluded_from_analysis_and_import() -> None:
    folder_settings = _load_json(VSCODE_SETTINGS)
    workspace_settings = _load_json(WORKSPACE_SETTINGS)["settings"]

    for settings in (folder_settings, workspace_settings):
        assert REQUIRED_PYLANCE_EXCLUSIONS <= set(
            settings["python.analysis.exclude"]
        )
        assert REQUIRED_JAVA_IMPORT_EXCLUSIONS <= set(
            settings["java.import.exclusions"]
        )


def test_local_sample_is_not_versioned() -> None:
    patterns = {
        line.strip()
        for line in GITIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "/testcontainers-cloud-java-example/" in patterns


def test_gradle_wrapper_tasks_do_not_depend_on_json_rpc_server() -> None:
    tasks = _load_json(VSCODE_TASKS)["tasks"]
    task_by_label = {task["label"]: task for task in tasks}

    for label in (
        "gradle: verificar wrapper Valley Android",
        "gradle: parar daemons Valley Android",
        "gradle: validar Valley Android sem servidor",
    ):
        task = task_by_label[label]
        assert task["type"] == "shell"
        assert task["options"]["cwd"] == "${workspaceFolder}/apps/valley-android"
        assert task["windows"]["command"] == "gradlew.bat"
        assert task["linux"]["command"] == "./gradlew"
        assert task["osx"]["command"] == "./gradlew"

    validation_args = task_by_label[
        "gradle: validar Valley Android sem servidor"
    ]["args"]
    assert "--no-daemon" in validation_args
    assert "--stacktrace" in validation_args


def test_gradle_wrapper_network_timeout_is_resilient() -> None:
    properties = WRAPPER_PROPERTIES.read_text(encoding="utf-8")
    timeout_line = next(
        line for line in properties.splitlines() if line.startswith("networkTimeout=")
    )
    timeout_ms = int(timeout_line.split("=", maxsplit=1)[1])

    assert timeout_ms >= 60_000
