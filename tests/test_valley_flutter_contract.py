import zipfile
from pathlib import Path

import pytest

from scripts.audit_valley_flutter_apks import (
    INDEX_PATH,
    _audit_web_bundle,
    _resolve_archive_reference,
    find_apksigner,
)
from scripts.prepare_valley_flutter_build import FLUTTER_APP


ROOT = Path(__file__).resolve().parents[1]


def test_flutter_app_uses_stitch_and_official_brand_sources() -> None:
    readme = (FLUTTER_APP / "README.md").read_text(encoding="utf-8")
    main = (FLUTTER_APP / "lib" / "main.dart").read_text(encoding="utf-8")
    prepare = (ROOT / "scripts" / "prepare_valley_flutter_build.py").read_text(
        encoding="utf-8"
    )

    assert "VALLEY APK - Template Completo" in readme
    assert "config/stitch/template_project_state.json" in readme
    assert "assets/brand/valley-logo-official.png" in main
    assert "CANONICAL_BRANDS" in prepare
    assert "_sync_pubspec_assets" in prepare


def test_free_distribution_has_runtime_bundle_gates() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "valley-android-release.yml"
    ).read_text(encoding="utf-8")

    assert "google-play-production" not in workflow
    assert "VALLEY_PLAY_" not in workflow
    assert 'VITE_VALLEY_ALLOW_DEMO: "true"' in workflow
    assert "prepare_valley_flutter_build.py --check" in workflow
    assert "flutter build apk --release" in workflow
    assert "scripts/audit_valley_flutter_apks.py" in workflow
    assert "actions/upload-artifact@v4" in workflow


def test_pubspec_has_generated_asset_block() -> None:
    pubspec = (FLUTTER_APP / "pubspec.yaml").read_text(encoding="utf-8")

    assert "# BEGIN GENERATED VALLEY WEB ASSETS" in pubspec
    assert "- assets/valley/" in pubspec
    assert "# END GENERATED VALLEY WEB ASSETS" in pubspec


def test_apk_bundle_audit_rejects_missing_javascript_and_css(tmp_path: Path) -> None:
    apk = tmp_path / "broken.apk"
    with zipfile.ZipFile(apk, "w") as archive:
        archive.writestr(INDEX_PATH, '<div id="root"></div>')

    errors: list[str] = []
    with zipfile.ZipFile(apk) as archive:
        _audit_web_bundle(apk.name, archive, errors)

    assert any("não referencia JavaScript" in error for error in errors)
    assert any("não referencia CSS" in error for error in errors)


def test_apk_bundle_audit_accepts_packaged_local_references(tmp_path: Path) -> None:
    apk = tmp_path / "working.apk"
    index = (
        '<div id="root"></div>'
        '<script src="./assets/app.js"></script>'
        '<link rel="stylesheet" href="./assets/app.css">'
    )
    with zipfile.ZipFile(apk, "w") as archive:
        archive.writestr(INDEX_PATH, index)
        archive.writestr(
            "assets/flutter_assets/assets/valley/assets/app.js",
            "console.log('Valley carregado com sucesso');",
        )
        archive.writestr(
            "assets/flutter_assets/assets/valley/assets/app.css",
            "body { min-height: 100vh; background: white; }",
        )

    errors: list[str] = []
    with zipfile.ZipFile(apk) as archive:
        _audit_web_bundle(apk.name, archive, errors)

    assert errors == []


def test_absolute_asset_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="referência absoluta"):
        _resolve_archive_reference("/assets/app.js")


def test_apksigner_is_resolved_from_android_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable = tmp_path / "build-tools" / "36.0.0" / "apksigner"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("ANDROID_HOME", str(tmp_path))
    monkeypatch.delenv("ANDROID_SDK_ROOT", raising=False)

    assert find_apksigner() == str(executable)
