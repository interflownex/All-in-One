from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "apps" / "frontend_journeys.json"

EXPECTED_APPS = {
    "all-in-one-user",
    "all-in-one-business",
    "all-in-one-riders",
    "all-in-one-services",
    "all-in-one-health",
    "all-in-one-mobility",
    "valley",
    "valley-business",
    "valley-rider",
}


def load_contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_frontend_journeys_contract_covers_phase_4_apps() -> None:
    contract = load_contract()
    apps = contract["apps"]

    assert contract["source"] == "docs/EXECUTION_PLAN.md#fase-4---jornadas-e2e-por-app"
    assert {app["slug"] for app in apps} == EXPECTED_APPS
    assert len(apps) == 9

    for app in apps:
        app_dir = ROOT / app["app_dir"]
        assert app_dir.is_dir(), app["slug"]
        assert (app_dir / "README.md").is_file(), app["slug"]

        if app["app_dir"] != app["shell_dir"]:
            assert (app_dir / "STATUS.md").is_file(), app["slug"]

        assert app["persona"], app["slug"]
        assert app["priority_journey"], app["slug"]
        assert app["api_modules"], app["slug"]
        assert app["api_hub_routes"], app["slug"]
        assert app["coverage"], app["slug"]
        assert app["next_e2e"].startswith(("Levar", "Criar", "Ampliar")), app["slug"]


def test_frontend_shell_package_names_match_contract() -> None:
    for app in load_contract()["apps"]:
        shell_dir = app["shell_dir"]
        package_name = app["package_name"]
        if shell_dir is None:
            assert package_name is None, app["slug"]
            assert app["shell_status"] == "contract_defined", app["slug"]
            continue

        package_json = ROOT / shell_dir / "package.json"
        package_lock = ROOT / shell_dir / "package-lock.json"
        assert package_json.is_file(), app["slug"]
        assert package_lock.is_file(), app["slug"]

        package = json.loads(package_json.read_text(encoding="utf-8"))
        lock = json.loads(package_lock.read_text(encoding="utf-8"))

        assert package["name"] == package_name, app["slug"]
        assert lock["name"] == package_name, app["slug"]
        assert lock["packages"][""]["name"] == package_name, app["slug"]
        assert app["shell_status"] in {"generated_react_shell", "functional_react_shell"}, app["slug"]


def test_frontend_contract_links_to_existing_e2e_and_pytest_evidence() -> None:
    e2e_tests = {path.stem.removeprefix("test_") for path in (ROOT / "tests" / "e2e").glob("test_*.py")}
    pytest_tests = {path.stem.removeprefix("test_") for path in (ROOT / "tests").glob("test_*.py")}

    for app in load_contract()["apps"]:
        for evidence in app["coverage"]:
            kind, name = evidence.split(":", 1)
            if kind == "playwright":
                assert name in e2e_tests, evidence
            elif kind == "pytest":
                assert name in pytest_tests, evidence
            else:
                raise AssertionError(f"Tipo de evidencia desconhecido: {evidence}")
