#!/usr/bin/env python3
"""Prepara o projeto Android e o bundle Stitch/Web para o build Flutter."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLUTTER_APP = ROOT / "apps" / "valley-flutter"
VALLEY_DIST = ROOT / "apps" / "valley" / "dist"
VALLEY_ASSETS = FLUTTER_APP / "assets" / "valley"
MANIFEST = FLUTTER_APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml"


def prepare() -> None:
    if not VALLEY_DIST.joinpath("index.html").is_file():
        raise FileNotFoundError(
            "apps/valley/dist ausente; execute npm --prefix apps/valley run build"
        )
    if not MANIFEST.is_file():
        raise FileNotFoundError(
            "plataforma Android ausente; execute flutter create --platforms=android ."
        )

    shutil.rmtree(VALLEY_ASSETS, ignore_errors=True)
    shutil.copytree(VALLEY_DIST, VALLEY_ASSETS)

    manifest = MANIFEST.read_text(encoding="utf-8")
    permission = '<uses-permission android:name="android.permission.INTERNET" />'
    if permission not in manifest:
        manifest = manifest.replace("<application", f"{permission}\n    <application", 1)
    manifest = manifest.replace('android:label="valley_consumer"', 'android:label="Valley"')
    MANIFEST.write_text(manifest, encoding="utf-8")


def validate() -> None:
    if not VALLEY_ASSETS.joinpath("index.html").is_file():
        raise FileNotFoundError("bundle Valley não foi copiado para o app Flutter")
    manifest = MANIFEST.read_text(encoding="utf-8")
    for marker in (
        'android.permission.INTERNET',
        'android:label="Valley"',
    ):
        if marker not in manifest:
            raise ValueError(f"AndroidManifest sem marcador obrigatório: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        prepare()
    validate()
    print("Projeto Flutter Valley preparado e validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
