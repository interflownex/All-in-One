import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "all-in-one" / "src"


def test_home_and_dashboards_cover_the_authoritative_stitch_manifest() -> None:
    manifest = json.loads((ROOT / "config" / "stitch" / "screen_manifest.json").read_text(encoding="utf-8"))
    home = (WEB / "pages" / "Home.tsx").read_text(encoding="utf-8")
    dashboard = (WEB / "components" / "ModuleDashboard.tsx").read_text(encoding="utf-8")

    assert manifest["project_count"] == 25
    assert manifest["screen_count"] == 181
    assert "<strong>181</strong><span>telas Stitch</span>" in home
    for project in manifest["projects"]:
        assert re.search(rf"^\s*{re.escape(project['module'])}: \[", dashboard, re.MULTILINE)


def test_every_navigation_target_has_a_react_route() -> None:
    app = (WEB / "App.tsx").read_text(encoding="utf-8")
    navigation = (WEB / "components" / "Navigation.tsx").read_text(encoding="utf-8")
    routes = set(re.findall(r'<Route path="([^"]+)"', app))
    targets = set(re.findall(r'path: "([^"]+)"', navigation))

    assert len(targets) >= 298
    assert targets <= routes


def test_each_module_has_ten_coherent_demo_records_and_media() -> None:
    demo_data = (WEB / "lib" / "demoData.ts").read_text(encoding="utf-8")
    assets = ROOT / "apps" / "all-in-one" / "public" / "assets" / "demo"

    assert "export const DEMO_RECORD_COUNT = 10" in demo_data
    assert (assets / "platform-overview.mp4").stat().st_size > 100_000
    module_images = list((assets / "modules").glob("*.webp"))
    assert len(module_images) == 25
    assert all(image.stat().st_size > 10_000 for image in module_images)
