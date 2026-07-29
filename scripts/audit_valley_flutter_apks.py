#!/usr/bin/env python3
"""Audita os APKs Flutter gratuitos antes da publicação como artefato."""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import urlsplit


REQUIRED_APKS = {
    "app-release.apk",
    "app-arm64-v8a-release.apk",
    "app-armeabi-v7a-release.apk",
    "app-x86_64-release.apk",
}
INDEX_PATH = "assets/flutter_assets/assets/valley/index.html"
LOCAL_REFERENCE_PATTERN = re.compile(r"(?:src|href)=[\"']([^\"']+)[\"']")


def find_apksigner() -> str | None:
    executable = shutil.which("apksigner")
    if executable:
        return executable

    for variable in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        sdk_root = os.environ.get(variable)
        if not sdk_root:
            continue
        candidates = sorted(
            Path(sdk_root).glob("build-tools/*/apksigner"),
            reverse=True,
        )
        if candidates:
            return str(candidates[0])
    return None


def command_output(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return f"{completed.stdout}\n{completed.stderr}"


def _resolve_archive_reference(reference: str) -> str | None:
    parsed = urlsplit(reference)
    if parsed.scheme or reference.startswith(("#", "//")):
        return None
    if reference.startswith("/"):
        raise ValueError(f"referência absoluta incompatível: {reference}")
    base = posixpath.dirname(INDEX_PATH)
    normalized = posixpath.normpath(posixpath.join(base, parsed.path))
    expected_prefix = "assets/flutter_assets/assets/valley/"
    if not normalized.startswith(expected_prefix):
        raise ValueError(f"referência escapou do bundle Valley: {reference}")
    return normalized


def _audit_web_bundle(apk_name: str, archive: zipfile.ZipFile, errors: list[str]) -> None:
    names = set(archive.namelist())
    try:
        index = archive.read(INDEX_PATH).decode("utf-8")
    except (KeyError, UnicodeDecodeError) as error:
        errors.append(f"{apk_name}: index.html inválido: {error}")
        return

    if '<div id="root"></div>' not in index:
        errors.append(f"{apk_name}: raiz React ausente no index.html")

    references = LOCAL_REFERENCE_PATTERN.findall(index)
    javascript = [item for item in references if urlsplit(item).path.endswith(".js")]
    stylesheets = [item for item in references if urlsplit(item).path.endswith(".css")]
    if not javascript:
        errors.append(f"{apk_name}: index.html não referencia JavaScript")
    if not stylesheets:
        errors.append(f"{apk_name}: index.html não referencia CSS")

    for reference in references:
        try:
            target = _resolve_archive_reference(reference)
        except ValueError as error:
            errors.append(f"{apk_name}: {error}")
            continue
        if target is None:
            continue
        if target not in names:
            errors.append(
                f"{apk_name}: recurso referenciado não foi empacotado: {reference}"
            )
            continue
        if target.endswith((".js", ".css")) and archive.getinfo(target).file_size < 32:
            errors.append(f"{apk_name}: recurso web vazio ou truncado: {reference}")


def audit(directory: Path) -> list[str]:
    errors: list[str] = []
    discovered = {path.name for path in directory.glob("*.apk")}
    missing = sorted(REQUIRED_APKS - discovered)
    if missing:
        errors.append(f"APKs obrigatórios ausentes: {', '.join(missing)}")

    apksigner = find_apksigner()
    if not apksigner:
        errors.append("apksigner não encontrado no Android SDK")

    for apk in sorted(directory.glob("*.apk")):
        if apk.stat().st_size < 1_000_000:
            errors.append(f"{apk.name}: arquivo menor que 1 MiB")
            continue
        try:
            with zipfile.ZipFile(apk) as archive:
                names = set(archive.namelist())
                for marker in (
                    "AndroidManifest.xml",
                    "classes.dex",
                    "assets/flutter_assets/AssetManifest.bin",
                    INDEX_PATH,
                    "assets/flutter_assets/assets/brand/valley-logo-official.png",
                ):
                    if marker not in names:
                        errors.append(
                            f"{apk.name}: conteúdo obrigatório ausente: {marker}"
                        )
                _audit_web_bundle(apk.name, archive, errors)
        except zipfile.BadZipFile:
            errors.append(f"{apk.name}: ZIP/APK inválido")

        if apksigner:
            try:
                output = command_output([apksigner, "verify", "--verbose", str(apk)])
            except subprocess.CalledProcessError as exc:
                errors.append(f"{apk.name}: assinatura APK inválida: {exc}")
            else:
                if "Verified" not in output:
                    errors.append(f"{apk.name}: apksigner não confirmou a assinatura")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    errors = audit(args.directory)
    if errors:
        print("Auditoria dos APKs Flutter reprovada:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Auditoria dos APKs Flutter aprovada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
