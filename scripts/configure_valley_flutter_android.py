#!/usr/bin/env python3
"""Configura a plataforma Android efêmera do Valley Flutter de modo determinístico."""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLUTTER_APP = ROOT / "apps" / "valley-flutter"
MANIFEST = FLUTTER_APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
OFFICIAL_LOGO = ROOT / "assets" / "brand" / "valley-logo-official.png"
DRAWABLE = FLUTTER_APP / "android" / "app" / "src" / "main" / "res" / "drawable-nodpi"
ICON = DRAWABLE / "valley_logo.png"
SHORTCUT_TEMPLATE = ROOT / "scripts" / "templates" / "valley" / "MainActivity.kt.tpl"
PERMISSIONS = ("android.permission.INTERNET", "android.permission.ACCESS_NETWORK_STATE")
APPLICATION_ATTRIBUTES = {
    "icon": "@drawable/valley_logo",
    "roundIcon": "@drawable/valley_logo",
    "usesCleartextTraffic": "false",
    "allowBackup": "false",
}


def _set_android_attribute(tag: str, name: str, value: str) -> str:
    attribute = f'android:{name}="{value}"'
    pattern = re.compile(rf'android:{re.escape(name)}="[^"]*"')
    if pattern.search(tag):
        return pattern.sub(attribute, tag, count=1)
    return tag[:-1].rstrip() + f"\n        {attribute}>"


def _materialize_manifest(text: str, app_label: str = "Valley") -> str:
    if "<manifest" not in text or "<application" not in text:
        raise RuntimeError("Manifesto Android fora do formato esperado.")
    permission_lines = []
    for permission in PERMISSIONS:
        marker = f'android:name="{permission}"'
        if marker not in text:
            permission_lines.append(f'    <uses-permission android:name="{permission}" />')
    if permission_lines:
        manifest_end = text.find(">", text.find("<manifest"))
        if manifest_end < 0:
            raise RuntimeError("Abertura do manifesto Android inválida.")
        insertion = "\n" + "\n".join(permission_lines)
        text = text[: manifest_end + 1] + insertion + text[manifest_end + 1 :]
    match = re.search(r"<application\b[^>]*>", text, flags=re.DOTALL)
    if match is None:
        raise RuntimeError("Elemento application não encontrado no manifesto Android.")
    application_tag = match.group(0)
    attributes = {"label": app_label, **APPLICATION_ATTRIBUTES}
    for name, value in attributes.items():
        application_tag = _set_android_attribute(application_tag, name, value)
    return text[: match.start()] + application_tag + text[match.end() :]


def _install_company_shortcut_bridge() -> Path:
    if not SHORTCUT_TEMPLATE.is_file():
        raise FileNotFoundError("Template Android do atalho empresarial ausente.")
    kotlin_root = FLUTTER_APP / "android" / "app" / "src" / "main" / "kotlin"
    candidates = list(kotlin_root.rglob("MainActivity.kt"))
    if len(candidates) != 1:
        raise RuntimeError(
            "Esperado exatamente um MainActivity.kt gerado pelo Flutter; "
            f"encontrados: {len(candidates)}."
        )
    main_activity = candidates[0]
    original = main_activity.read_text(encoding="utf-8")
    package_match = re.search(r"^package\s+([\w.]+)\s*$", original, flags=re.MULTILINE)
    if package_match is None:
        raise RuntimeError("Package Kotlin não encontrado no MainActivity gerado.")
    template = SHORTCUT_TEMPLATE.read_text(encoding="utf-8")
    main_activity.write_text(
        template.replace("__PACKAGE__", package_match.group(1)),
        encoding="utf-8",
    )
    return main_activity


def configure(app_label: str = "Valley") -> None:
    if not MANIFEST.is_file():
        raise FileNotFoundError("AndroidManifest.xml ausente; execute flutter create antes desta etapa.")
    if not OFFICIAL_LOGO.is_file():
        raise FileNotFoundError("Logomarca oficial Valley ausente.")
    original = MANIFEST.read_text(encoding="utf-8")
    MANIFEST.write_text(_materialize_manifest(original, app_label), encoding="utf-8")
    DRAWABLE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OFFICIAL_LOGO, ICON)
    _install_company_shortcut_bridge()


def check(app_label: str = "Valley") -> None:
    if not MANIFEST.is_file() or not ICON.is_file():
        raise SystemExit("Configuração Android Valley não materializada.")
    text = MANIFEST.read_text(encoding="utf-8")
    missing = [permission for permission in PERMISSIONS if f'android:name="{permission}"' not in text]
    if missing:
        raise SystemExit(f"Permissões Android ausentes: {', '.join(missing)}")
    match = re.search(r"<application\b[^>]*>", text, flags=re.DOTALL)
    if match is None:
        raise SystemExit("Elemento application ausente.")
    application_tag = match.group(0)
    attributes = {"label": app_label, **APPLICATION_ATTRIBUTES}
    for name, value in attributes.items():
        if f'android:{name}="{value}"' not in application_tag:
            raise SystemExit(f"Manifesto Android divergente em {name}.")
    if ICON.read_bytes() != OFFICIAL_LOGO.read_bytes():
        raise SystemExit("Ícone Android não corresponde byte a byte à logomarca oficial Valley.")
    kotlin_root = FLUTTER_APP / "android" / "app" / "src" / "main" / "kotlin"
    candidates = list(kotlin_root.rglob("MainActivity.kt"))
    if len(candidates) != 1:
        raise SystemExit("Ponte Android do atalho empresarial não foi materializada.")
    main_activity = candidates[0].read_text(encoding="utf-8")
    for marker in (
        "com.allinone.valley/company_shortcut",
        "requestPinShortcut",
        "createWithAdaptiveBitmap",
        "initialCompanyId",
    ):
        if marker not in main_activity:
            raise SystemExit(f"Ponte Android incompleta: {marker}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--label", default="Valley")
    args = parser.parse_args()
    if args.check:
        check(args.label)
    else:
        configure(args.label)
        check(args.label)
        print(
            f"Android {args.label} configurado com rede segura, ícone oficial "
            "e ponte de atalho empresarial."
        )


if __name__ == "__main__":
    main()
