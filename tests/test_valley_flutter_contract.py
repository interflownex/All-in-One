from pathlib import Path

from scripts.prepare_valley_flutter_build import FLUTTER_APP


ROOT = Path(__file__).resolve().parents[1]


def test_flutter_app_uses_stitch_and_official_brand_sources() -> None:
    readme = (FLUTTER_APP / "README.md").read_text(encoding="utf-8")
    main = (FLUTTER_APP / "lib" / "main.dart").read_text(encoding="utf-8")

    assert "VALLEY APK - Template Completo" in readme
    assert "config/stitch/template_project_state.json" in readme
    assert "assets/brand/valley-logo-official.png" in main


def test_free_distribution_has_no_google_play_environment() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "valley-android-release.yml"
    ).read_text(encoding="utf-8")

    assert "google-play-production" not in workflow
    assert "VALLEY_PLAY_" not in workflow
    assert "flutter build apk --release" in workflow
    assert "actions/upload-artifact@v4" in workflow
