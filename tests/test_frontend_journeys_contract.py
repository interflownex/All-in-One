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
        assert app["next_e2e"].startswith(("Levar", "Criar", "Ampliar", "Executar")), app["slug"]


def test_frontend_shell_package_names_match_contract() -> None:
    for app in load_contract()["apps"]:
        shell_dir = app["shell_dir"]
        package_name = app["package_name"]
        package_json = ROOT / shell_dir / "package.json"
        package_lock = ROOT / shell_dir / "package-lock.json"
        app_entry = ROOT / shell_dir / "src" / "App.tsx"
        eslint_config = ROOT / shell_dir / "eslint.config.js"
        html_entry = ROOT / shell_dir / "index.html"
        assert package_json.is_file(), app["slug"]
        assert package_lock.is_file(), app["slug"]
        assert app_entry.is_file(), app["slug"]
        assert eslint_config.is_file(), app["slug"]
        assert html_entry.is_file(), app["slug"]

        package = json.loads(package_json.read_text(encoding="utf-8"))
        lock = json.loads(package_lock.read_text(encoding="utf-8"))

        assert package["name"] == package_name, app["slug"]
        assert lock["name"] == package_name, app["slug"]
        assert lock["packages"][""]["name"] == package_name, app["slug"]
        assert app["shell_status"] in {
            "api_hub_live_actions",
            "api_hub_connected_shell",
            "generated_react_shell",
            "functional_react_shell",
            "journey_react_shell",
        }, app["slug"]


def test_phase_4_shells_are_wired_to_declared_api_hub_routes() -> None:
    connected_shells = {
        "all-in-one-riders",
        "all-in-one-services",
        "all-in-one-health",
        "all-in-one-mobility",
    }

    for app in load_contract()["apps"]:
        if app["slug"] not in connected_shells:
            continue

        shell_dir = ROOT / app["shell_dir"]
        app_source = (shell_dir / "src" / "App.tsx").read_text(encoding="utf-8")
        vite_config = (shell_dir / "vite.config.ts").read_text(encoding="utf-8")

        assert app["shell_status"] == "api_hub_connected_shell", app["slug"]
        assert "VITE_API_HUB_URL" in app_source, app["slug"]
        assert "fetch(" in app_source, app["slug"]

        for route in app["api_hub_routes"]:
            assert route in app_source, f"{app['slug']} nao usa {route}"
            proxy_prefix = "/" + route.strip("/").split("/", 1)[0]
            assert proxy_prefix in vite_config, f"{app['slug']} sem proxy {proxy_prefix}"


def test_phase_4_shells_have_playwright_coverage_declared() -> None:
    connected_shells = {
        "all-in-one-riders",
        "all-in-one-services",
        "all-in-one-health",
        "all-in-one-mobility",
    }

    for app in load_contract()["apps"]:
        if app["slug"] in connected_shells:
            assert "playwright:all_in_one_phase4_shells" in app["coverage"], app["slug"]


def test_phase_4_live_shells_do_not_keep_obsolete_next_steps() -> None:
    connected_shells = {
        "all-in-one-riders",
        "all-in-one-services",
        "all-in-one-health",
        "all-in-one-mobility",
    }
    obsolete_fragments = (
        "evoluir para API Hub vivo",
        "ambiente com dependencias Node",
    )

    for app in load_contract()["apps"]:
        if app["slug"] not in connected_shells:
            continue

        assert app["next_e2e"].startswith("Ampliar interface funcional"), app["slug"]
        for fragment in obsolete_fragments:
            assert fragment not in app["next_e2e"], app["slug"]


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
