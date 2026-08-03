from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "valley-rider-mapbox.yml"


def test_mapbox_workflow_requires_environment_specific_secrets() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    for secret in (
        "VITE_MAPBOX_ACCESS_TOKEN_STAGING",
        "VITE_MAPBOX_ACCESS_TOKEN_PRODUCTION",
        "MAPBOX_MOBILE_ACCESS_TOKEN_STAGING",
        "MAPBOX_MOBILE_ACCESS_TOKEN_PRODUCTION",
    ):
        assert f"secrets.{secret}" in source

    assert '[[ "$VITE_MAPBOX_ACCESS_TOKEN" == pk.* ]]' in source
    assert '[[ "$MAPBOX_MOBILE_ACCESS_TOKEN" == pk.* ]]' in source


def test_mapbox_workflow_validates_and_packages_valley_rider() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "node scripts/mapbox/validate_valley_rider_mapbox.mjs" in source
    assert "npm run lint" in source
    assert "npm run build" in source
    assert "actions/upload-artifact@v4" in source
    assert "apps/valley_rider/dist" in source
    assert "https://all-in-one-web-7fa.pages.dev" in source
    assert "https://brasildesconto.com.br" in source

