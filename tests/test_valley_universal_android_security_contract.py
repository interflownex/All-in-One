from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVITY = (
    ROOT
    / "apps"
    / "valley-android"
    / "universal"
    / "src"
    / "main"
    / "java"
    / "br"
    / "com"
    / "allinone"
    / "valley"
    / "universal"
    / "UniversalActivity.java"
)
MANIFEST = (
    ROOT
    / "apps"
    / "valley-android"
    / "universal"
    / "src"
    / "main"
    / "AndroidManifest.xml"
)


def test_external_navigation_requires_explicit_user_gesture() -> None:
    source = ACTIVITY.read_text(encoding="utf-8")

    assert "request.hasGesture()" in source
    assert "!hasUserGesture" in source
    assert "Intent.CATEGORY_BROWSABLE" in source
    assert "urlPolicy.isSafeExternal(candidateUrl)" in source


def test_webview_disables_local_and_mixed_content_access() -> None:
    source = ACTIVITY.read_text(encoding="utf-8")

    assert "setAllowFileAccess(false)" in source
    assert "setAllowContentAccess(false)" in source
    assert "setAllowFileAccessFromFileURLs(false)" in source
    assert "setAllowUniversalAccessFromFileURLs(false)" in source
    assert "WebSettings.MIXED_CONTENT_NEVER_ALLOW" in source
    assert "setSafeBrowsingEnabled(true)" in source


def test_android_manifest_blocks_cleartext_and_backup() -> None:
    manifest = MANIFEST.read_text(encoding="utf-8")

    assert 'android:usesCleartextTraffic="false"' in manifest
    assert 'android:allowBackup="false"' in manifest
    assert 'android:exported="true"' in manifest
