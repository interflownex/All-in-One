import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "all-in-one" / "src"


def load_catalog() -> dict:
    return json.loads((ROOT / "config" / "module_catalog.json").read_text(encoding="utf-8"))


def test_home_and_dashboards_cover_the_authoritative_stitch_manifest() -> None:
    manifest = json.loads(
        (ROOT / "config" / "stitch" / "screen_manifest.json").read_text(encoding="utf-8")
    )
    catalog = load_catalog()
    home = (WEB / "pages" / "Home.tsx").read_text(encoding="utf-8")
    dashboard = (WEB / "components" / "ModuleDashboard.tsx").read_text(encoding="utf-8")

    assert manifest["project_count"] == len(catalog["modules"])
    assert manifest["screen_count"] == sum(project["screen_count"] for project in manifest["projects"])
    assert f"<strong>{manifest['project_count']}</strong>" in home
    assert f"<strong>{manifest['screen_count']}</strong>" in home
    assert "<span>telas Stitch</span>" in home
    for project in manifest["projects"]:
        assert re.search(rf"^\s*{re.escape(project['module'])}: \[", dashboard, re.MULTILINE)


def test_every_navigation_target_has_a_react_route() -> None:
    app = (WEB / "App.tsx").read_text(encoding="utf-8")
    navigation = (WEB / "components" / "Navigation.tsx").read_text(encoding="utf-8")
    routes = set(re.findall(r'<Route\s+path="([^"]+)"', app))
    targets = set(re.findall(r'path: "([^"]+)"', navigation))

    assert targets
    assert targets <= routes


def test_each_module_has_ten_coherent_demo_records_and_media() -> None:
    demo_data = (WEB / "lib" / "demoData.ts").read_text(encoding="utf-8")
    assets = ROOT / "apps" / "all-in-one" / "public" / "assets" / "demo"
    catalog_slugs = {module["slug"] for module in load_catalog()["modules"]}

    assert "export const DEMO_RECORD_COUNT = 10" in demo_data
    assert (assets / "platform-overview.mp4").stat().st_size > 100_000
    module_images = {image.stem: image for image in (assets / "modules").glob("*.webp")}
    assert set(module_images) == catalog_slugs
    assert all(image.stat().st_size > 10_000 for image in module_images.values())


def test_mobile_shell_has_an_accessible_drawer_and_responsive_operations() -> None:
    navigation = (WEB / "components" / "Navigation.tsx").read_text(encoding="utf-8")
    smart_crud = (WEB / "components" / "SmartCRUD.tsx").read_text(encoding="utf-8")
    styles = (WEB / "index.css").read_text(encoding="utf-8")

    assert 'className="mobile-nav-toggle"' in navigation
    assert "aria-expanded={mobileOpen}" in navigation
    assert re.search(r'<button\s+type="button"\s+className=\{`module-link', navigation)
    assert "aria-expanded={openModule === mod.slug}" in navigation
    assert 'className="search-row search-row-crud"' in smart_crud
    assert "@media (max-width: 700px)" in styles
    assert re.search(r"\.side-nav\.mobile-open\s*\{\s*transform:\s*translateX\(0\);\s*\}", styles)
    assert re.search(r"\.data-card\s*\{[^}]*grid-template-columns:\s*1fr;[^}]*gap:\s*14px;", styles, re.S)


def test_smartcrud_save_uses_the_shared_backend_contract() -> None:
    smart_crud = (WEB / "components" / "SmartCRUD.tsx").read_text(encoding="utf-8")

    assert re.search(r'method:\s*isEditing\s*\?\s*["\']PATCH["\']\s*:\s*["\']POST["\']', smart_crud)
    assert "isEditing ? { payload } : { user_id: actorId, payload }" in smart_crud
    assert re.search(r'["\']X-Idempotency-Key["\']:\s*crypto\.randomUUID\(\)', smart_crud)
    assert re.search(r'["\']X-Correlation-Id["\']:\s*crypto\.randomUUID\(\)', smart_crud)
    assert "method: editingRecord?.id ? 'PUT' : 'POST'" not in smart_crud
