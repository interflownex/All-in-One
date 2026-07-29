#!/usr/bin/env python3
"""Audita os APKs Flutter gratuitos antes da publicação como artefato."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path


REQUIRED_APKS = {
    "app-release.apk",
    "app-arm64-v8a-release.apk",
    "app-armeabi-v7a-release.apk",
    "app-x86_64-release.apk",
}


def command_output(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return f"{completed.stdout}\n{completed.stderr}"


def audit(directory: Path) -> list[str]:
    errors: list[str] = []
    discovered = {path.name for path in directory.glob("*.apk")}
    missing = sorted(REQUIRED_APKS - discovered)
    if missing:
        errors.append(f"APKs obrigatórios ausentes: {', '.join(missing)}")

    apksigner = shutil.which("apksigner")
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
                    "assets/flutter_assets/AssetManifest.bin",
                    "assets/flutter_assets/assets/valley/index.html",
                    "assets/flutter_assets/assets/brand/valley-logo-official.png",
                ):
                    if marker not in names:
                        errors.append(f"{apk.name}: conteúdo obrigatório ausente: {marker}")
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
