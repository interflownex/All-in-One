import zipfile
from pathlib import Path

import pytest

from scripts.audit_valley_flutter_apks import (
    INDEX_PATH,
    _audit_web_bundle,
    _resolve_archive_reference,
    find_apksigner,
)
from scripts.configure_valley_flutter_android import _materialize_manifest
from scripts.prepare_valley_flutter_build import FLUTTER_APP


ROOT = Path(__file__).resolve().parents[1]


def test_flutter_app_uses_stitch_and_official_brand_sources() -> None:
    readme = (FLUTTER_APP / "README.md").read_text(encoding="utf-8")
    main = (FLUTTER_APP / "lib" / "main.dart").read_text(encoding="utf-8")
    prepare = (ROOT / "scripts" / "prepare_valley_flutter_build.py").read_text(encoding="utf-8")
    assert "VALLEY APK - Template Completo" in readme
    assert "config/stitch/template_project_state.json" in readme
    assert "assets/brand/valley-logo-official.png" in main
    assert "CANONICAL_BRANDS" in prepare
    assert "_sync_pubspec_assets" in prepare


def test_release_is_server_bound_without_demo_fallback() -> None:
    workflow = (ROOT / ".github" / "workflows" / "valley-android-release.yml").read_text(encoding="utf-8")
    app = (ROOT / "apps" / "valley" / "src" / "App.tsx").read_text(encoding="utf-8")
    api = (ROOT / "apps" / "valley" / "src" / "lib" / "api.ts").read_text(encoding="utf-8")
    bridge = (ROOT / "apps" / "valley" / "src" / "lib" / "nativeBridge.ts").read_text(encoding="utf-8")
    assert "VITE_API_HUB_URL: https://all-in-one-api-hub.web.app" in workflow
    assert 'VITE_VALLEY_ALLOW_DEMO: "true"' not in workflow
    assert "configure_valley_flutter_android.py --check" in workflow
    assert "validate_valley_functional_completeness.py" in workflow
    assert "flutter build apk --release" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "https://all-in-one-api-hub.web.app" in bridge
    assert "ValleyNative" in bridge
    assert "verifyCriticalResponse" in bridge
    assert "export type ViewKey = 'home' | 'commerce' | 'services' | 'delivery' | 'mobility' | 'life' | 'account' | 'settings'" in api
    assert "AuthScreen" in app


def test_android_configuration_requires_network_and_official_icon() -> None:
    configure = (ROOT / "scripts" / "configure_valley_flutter_android.py").read_text(encoding="utf-8")
    assert "android.permission.INTERNET" in configure
    assert "android.permission.ACCESS_NETWORK_STATE" in configure
    assert "@drawable/valley_logo" in configure
    assert "ICON.read_bytes() != OFFICIAL_LOGO.read_bytes()" in configure
    assert '"usesCleartextTraffic": "false"' in configure
    assert '"allowBackup": "false"' in configure
    assert "xml.etree" not in configure


def test_android_manifest_materialization_is_idempotent() -> None:
    source = '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application android:label="${applicationName}"></application></manifest>'
    configured = _materialize_manifest(source)
    repeated = _materialize_manifest(configured)
    assert configured == repeated
    assert configured.count("android.permission.INTERNET") == 1
    assert configured.count("android.permission.ACCESS_NETWORK_STATE") == 1
    assert 'android:label="Valley"' in configured
    assert 'android:icon="@drawable/valley_logo"' in configured
    assert 'android:roundIcon="@drawable/valley_logo"' in configured
    assert 'android:usesCleartextTraffic="false"' in configured
    assert 'android:allowBackup="false"' in configured


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
    index = '<div id="root"></div><script src="./assets/app.js"></script><link rel="stylesheet" href="./assets/app.css">'
    with zipfile.ZipFile(apk, "w") as archive:
        archive.writestr(INDEX_PATH, index)
        archive.writestr("assets/flutter_assets/assets/valley/assets/app.js", "console.log('Valley carregado com sucesso');")
        archive.writestr("assets/flutter_assets/assets/valley/assets/app.css", "body { min-height: 100vh; background: white; }")
    errors: list[str] = []
    with zipfile.ZipFile(apk) as archive:
        _audit_web_bundle(apk.name, archive, errors)
    assert errors == []


def test_absolute_asset_reference_is_rejected() -> None:
    with pytest.raises(ValueError, match="referência absoluta"):
        _resolve_archive_reference("/assets/app.js")


def test_apksigner_is_resolved_from_android_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    executable = tmp_path / "build-tools" / "36.0.0" / "apksigner"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("ANDROID_HOME", str(tmp_path))
    monkeypatch.delenv("ANDROID_SDK_ROOT", raising=False)
    assert find_apksigner() == str(executable)
