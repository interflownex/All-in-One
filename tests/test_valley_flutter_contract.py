from pathlib import Path

from scripts.audit_valley_flutter_apks import find_apksigner
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
    assert 'flutter_project="$(mktemp -d)"' in workflow
    assert 'cp -R "$flutter_project/android" apps/valley-flutter/android' in workflow
    assert "--project-name valley_consumer\n          ." not in workflow


def test_apksigner_is_resolved_from_android_home(
    tmp_path: Path, monkeypatch
) -> None:
    executable = tmp_path / "build-tools" / "36.0.0" / "apksigner"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("ANDROID_HOME", str(tmp_path))
    monkeypatch.delenv("ANDROID_SDK_ROOT", raising=False)

    assert find_apksigner() == str(executable)
