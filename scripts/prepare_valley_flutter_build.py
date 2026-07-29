#!/usr/bin/env python3
"""Prepara o projeto Android e o bundle Stitch/Web para o build Flutter."""

from __future__ import annotations

import argparse
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
FLUTTER_APP = ROOT / "apps" / "valley-flutter"
VALLEY_DIST = ROOT / "apps" / "valley" / "dist"
VALLEY_ASSETS = FLUTTER_APP / "assets" / "valley"
FLUTTER_BRANDS = FLUTTER_APP / "assets" / "brand"
CANONICAL_BRANDS = ROOT / "assets" / "brand"
MANIFEST = FLUTTER_APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
PUBSPEC = FLUTTER_APP / "pubspec.yaml"
ASSET_BLOCK_BEGIN = "    # BEGIN GENERATED VALLEY WEB ASSETS"
ASSET_BLOCK_END = "    # END GENERATED VALLEY WEB ASSETS"
LOCAL_REFERENCE_PATTERN = re.compile(r"(?:src|href)=[\"']([^\"']+)[\"']")
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".map", ".svg"}
BRAND_FILES = (
    "all-in-one-logo-official.png",
    "valley-logo-official.png",
)


def _copy_official_brands(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for filename in BRAND_FILES:
        source = CANONICAL_BRANDS / filename
        if not source.is_file():
            raise FileNotFoundError(f"marca canônica ausente: {source}")
        shutil.copy2(source, target / filename)


def _rewrite_local_asset_urls() -> None:
    replacements = (
        ('"/assets/', '"./assets/'),
        ("'/assets/", "'./assets/"),
        ("`/assets/", "`./assets/"),
        ("url(/assets/", "url(./assets/"),
        ('url("/assets/', 'url("./assets/'),
        ("url('/assets/", "url('./assets/"),
        ("./assets/brand/favicon-valley.svg", "./assets/brand/valley-logo-official.png"),
    )
    for path in VALLEY_ASSETS.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = content
        for source, target in replacements:
            updated = updated.replace(source, target)
        if updated != content:
            path.write_text(updated, encoding="utf-8")


def _asset_directories() -> list[str]:
    directories = {
        path.parent.relative_to(FLUTTER_APP).as_posix()
        for path in VALLEY_ASSETS.rglob("*")
        if path.is_file()
    }
    return sorted(directories, key=lambda item: (item.count("/"), item))


def _sync_pubspec_assets() -> None:
    content = PUBSPEC.read_text(encoding="utf-8")
    if ASSET_BLOCK_BEGIN not in content or ASSET_BLOCK_END not in content:
        raise ValueError("pubspec.yaml sem bloco gerenciado de assets Valley")
    entries = "\n".join(f"    - {directory}/" for directory in _asset_directories())
    block = f"{ASSET_BLOCK_BEGIN}\n{entries}\n{ASSET_BLOCK_END}"
    pattern = re.compile(
        rf"{re.escape(ASSET_BLOCK_BEGIN)}.*?{re.escape(ASSET_BLOCK_END)}",
        re.DOTALL,
    )
    PUBSPEC.write_text(pattern.sub(block, content), encoding="utf-8")


def _local_references(index: Path) -> list[str]:
    return LOCAL_REFERENCE_PATTERN.findall(index.read_text(encoding="utf-8"))


def _resolve_reference(index: Path, reference: str) -> Path | None:
    parsed = urlsplit(reference)
    if parsed.scheme or reference.startswith(("#", "//")):
        return None
    if reference.startswith("/"):
        raise ValueError(f"referência absoluta incompatível com Flutter asset: {reference}")
    normalized = posixpath.normpath(
        posixpath.join(index.parent.relative_to(FLUTTER_APP).as_posix(), parsed.path)
    )
    candidate = FLUTTER_APP / normalized
    try:
        candidate.resolve().relative_to(VALLEY_ASSETS.resolve())
    except ValueError as error:
        raise ValueError(f"referência fora do bundle Valley: {reference}") from error
    return candidate


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
    _copy_official_brands(FLUTTER_BRANDS)
    _copy_official_brands(VALLEY_ASSETS / "assets" / "brand")
    _rewrite_local_asset_urls()
    _sync_pubspec_assets()

    manifest = MANIFEST.read_text(encoding="utf-8")
    permission = '<uses-permission android:name="android.permission.INTERNET" />'
    if permission not in manifest:
        manifest = manifest.replace("<application", f"{permission}\n    <application", 1)
    manifest = manifest.replace('android:label="valley_consumer"', 'android:label="Valley"')
    MANIFEST.write_text(manifest, encoding="utf-8")


def validate() -> None:
    index = VALLEY_ASSETS / "index.html"
    if not index.is_file():
        raise FileNotFoundError("bundle Valley não foi copiado para o app Flutter")

    for filename in BRAND_FILES:
        if not (FLUTTER_BRANDS / filename).is_file():
            raise FileNotFoundError(f"marca Flutter ausente: {filename}")
        if not (VALLEY_ASSETS / "assets" / "brand" / filename).is_file():
            raise FileNotFoundError(f"marca web ausente: {filename}")

    references = _local_references(index)
    javascript = [item for item in references if urlsplit(item).path.endswith(".js")]
    stylesheets = [item for item in references if urlsplit(item).path.endswith(".css")]
    if not javascript:
        raise ValueError("index.html sem referência JavaScript")
    if not stylesheets:
        raise ValueError("index.html sem referência CSS")

    for reference in references:
        candidate = _resolve_reference(index, reference)
        if candidate is not None and not candidate.is_file():
            raise FileNotFoundError(f"asset referenciado não existe: {reference}")

    pubspec = PUBSPEC.read_text(encoding="utf-8")
    for directory in _asset_directories():
        marker = f"    - {directory}/"
        if marker not in pubspec:
            raise ValueError(f"pubspec sem diretório obrigatório: {directory}/")

    manifest = MANIFEST.read_text(encoding="utf-8")
    for marker in ("android.permission.INTERNET", 'android:label="Valley"'):
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
