import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_official_brand_assets_are_versioned_and_declared() -> None:
    brand = json.loads(
        (ROOT / "config" / "branding" / "brand_identity.json").read_text(
            encoding="utf-8"
        )
    )
    assets = [
        brand["platform_brand"]["transparent_logo_asset"],
        brand["platform_brand"]["favicon_assets"]["v1"],
        brand["platform_brand"]["favicon_assets"]["v2"],
        brand["platform_brand"]["favicon_assets"]["v3"],
        brand["valley_brand"]["transparent_logo_asset"],
        brand["valley_brand"]["favicon_assets"]["v1"],
        brand["valley_brand"]["favicon_assets"]["v2"],
        brand["valley_brand"]["favicon_assets"]["v3"],
    ]
    for asset in assets:
        path = ROOT / asset
        assert path.is_file()
        assert path.suffix == ".svg"
        assert 'fill="none"' in path.read_text(encoding="utf-8")


def test_readme_uses_official_all_in_one_project_image() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "![All-in-One](assets/brand/all-in-one-logo-transparent.svg)" in readme


def test_valley_official_logo_is_mandatory_for_valley_apps() -> None:
    brand = json.loads(
        (ROOT / "config" / "branding" / "brand_identity.json").read_text(
            encoding="utf-8"
        )
    )
    assert set(brand["valley_apps"]) == {"valley", "valley-business", "valley-rider"}
    assert (
        brand["valley_brand"]["logo_asset"] == "assets/brand/valley-logo-official.png"
    )
    assert (
        "Every screen generated for valley, valley-business or valley-rider"
        in " ".join(brand["rules"])
    )
