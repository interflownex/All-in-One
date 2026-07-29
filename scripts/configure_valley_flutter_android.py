#!/usr/bin/env python3
"""Configura a plataforma Android efêmera do Valley Flutter de modo determinístico."""
from __future__ import annotations

import argparse
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLUTTER_APP = ROOT / "apps" / "valley-flutter"
MANIFEST = FLUTTER_APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
OFFICIAL_LOGO = ROOT / "assets" / "brand" / "valley-logo-official.png"
DRAWABLE = FLUTTER_APP / "android" / "app" / "src" / "main" / "res" / "drawable-nodpi"
ICON = DRAWABLE / "valley_logo.png"
ANDROID_NS = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", ANDROID_NS)


def _android(name: str) -> str:
    return f"{{{ANDROID_NS}}}{name}"


def configure() -> None:
    if not MANIFEST.is_file():
        raise FileNotFoundError("AndroidManifest.xml ausente; execute flutter create antes desta etapa.")
    if not OFFICIAL_LOGO.is_file():
        raise FileNotFoundError("Logomarca oficial Valley ausente.")
    tree = ET.parse(MANIFEST)
    root = tree.getroot()
    existing = {node.get(_android("name")) for node in root.findall("uses-permission")}
    for permission in ("android.permission.INTERNET", "android.permission.ACCESS_NETWORK_STATE"):
        if permission not in existing:
            node = ET.Element("uses-permission")
            node.set(_android("name"), permission)
            root.insert(0, node)
    application = root.find("application")
    if application is None:
        raise RuntimeError("Elemento application não encontrado no manifesto Android.")
    application.set(_android("label"), "Valley")
    application.set(_android("icon"), "@drawable/valley_logo")
    application.set(_android("roundIcon"), "@drawable/valley_logo")
    application.set(_android("usesCleartextTraffic"), "false")
    application.set(_android("allowBackup"), "false")
    DRAWABLE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OFFICIAL_LOGO, ICON)
    tree.write(MANIFEST, encoding="utf-8", xml_declaration=True)


def check() -> None:
    if not MANIFEST.is_file() or not ICON.is_file():
        raise SystemExit("Configuração Android Valley não materializada.")
    tree = ET.parse(MANIFEST)
    root = tree.getroot()
    permissions = {node.get(_android("name")) for node in root.findall("uses-permission")}
    required = {"android.permission.INTERNET", "android.permission.ACCESS_NETWORK_STATE"}
    missing = sorted(required - permissions)
    if missing:
        raise SystemExit(f"Permissões Android ausentes: {', '.join(missing)}")
    application = root.find("application")
    if application is None:
        raise SystemExit("Elemento application ausente.")
    expected = {"label": "Valley", "icon": "@drawable/valley_logo", "roundIcon": "@drawable/valley_logo", "usesCleartextTraffic": "false", "allowBackup": "false"}
    for key, value in expected.items():
        if application.get(_android(key)) != value:
            raise SystemExit(f"Manifesto Android divergente em {key}.")
    if ICON.read_bytes() != OFFICIAL_LOGO.read_bytes():
        raise SystemExit("Ícone Android não corresponde byte a byte à logomarca oficial Valley.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        configure()
        check()
        print("Android Valley configurado com rede segura e ícone oficial.")


if __name__ == "__main__":
    main()
