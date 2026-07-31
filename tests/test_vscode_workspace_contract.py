import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FOLDER_SETTINGS = ROOT / ".vscode" / "settings.json"
WORKSPACE = ROOT / "all-in-one.code-workspace"

PYLANCE_EXCLUDES = {
    "**/.*",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.git/**",
    "**/.venv/**",
    "**/venv/**",
}

WATCHER_EXCLUDES = {
    "**/.git/objects/**",
    "**/.venv/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.gradle/**",
    "**/build/**",
    "**/dist/**",
    "**/target/**",
    "**/.gemini/skills/**",
    "**/.github/skills/**",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_python_interpreter_is_configured_in_both_workspace_modes() -> None:
    folder_settings = _load(FOLDER_SETTINGS)
    workspace = _load(WORKSPACE)

    assert folder_settings["python.defaultInterpreterPath"] == (
        "${workspaceFolder}/.venv/bin/python"
    )
    assert workspace["folders"] == [{"name": "all-in-one", "path": "."}]
    assert workspace["settings"]["python.defaultInterpreterPath"] == (
        "${workspaceFolder:all-in-one}/.venv/bin/python"
    )


def test_pylance_excludes_large_generated_trees_in_both_workspace_modes() -> None:
    folder_settings = _load(FOLDER_SETTINGS)
    workspace_settings = _load(WORKSPACE)["settings"]

    for settings in (folder_settings, workspace_settings):
        assert PYLANCE_EXCLUDES <= set(settings["python.analysis.exclude"])


def test_file_watcher_excludes_generated_trees_in_both_workspace_modes() -> None:
    folder_settings = _load(FOLDER_SETTINGS)
    workspace_settings = _load(WORKSPACE)["settings"]

    for settings in (folder_settings, workspace_settings):
        watcher_excludes = settings["files.watcherExclude"]
        assert WATCHER_EXCLUDES <= set(watcher_excludes)
        assert all(watcher_excludes[path] is True for path in WATCHER_EXCLUDES)
