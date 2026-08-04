from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DART_BRIDGE = (
    ROOT / "apps" / "valley-flutter" / "lib" / "company_launcher_shortcut.dart"
)
ANDROID_TEMPLATE = ROOT / "scripts" / "templates" / "valley" / "MainActivity.kt.tpl"
ANDROID_CONFIGURATOR = ROOT / "scripts" / "configure_valley_flutter_android.py"


def test_flutter_bridge_preserves_default_icon_fallback() -> None:
    text = DART_BRIDGE.read_text(encoding="utf-8")
    for marker in (
        "CompanyLauncherShortcut",
        "isSupported",
        "ValleyBrandVariant",
        "supported: false, requested: false",
        "_maxCompanyLogoBytes",
        "assets/brand/valley-shortcut-frame.png",
        "assets/brand/valley-rider-shortcut-frame.png",
        "createWithAdaptiveBitmap",
    ):
        assert marker in text


def test_android_template_uses_official_pinned_shortcut_api() -> None:
    text = ANDROID_TEMPLATE.read_text(encoding="utf-8")
    for marker in (
        "ShortcutManager",
        "isRequestPinShortcutSupported",
        "requestPinShortcut",
        "Icon.createWithAdaptiveBitmap",
        "companyId",
        "initialCompanyId",
    ):
        assert marker in text
    assert "setComponentEnabledSetting" not in text


def test_android_configurator_materializes_and_validates_bridge() -> None:
    text = ANDROID_CONFIGURATOR.read_text(encoding="utf-8")
    for marker in (
        "_install_company_shortcut_bridge",
        "MainActivity.kt.tpl",
        "com.allinone.valley/company_shortcut",
        "requestPinShortcut",
    ):
        assert marker in text
