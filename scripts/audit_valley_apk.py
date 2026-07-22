#!/usr/bin/env python3
"""Inspeciona o APK Valley e reprova material interno ou assinatura debug."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

FORBIDDEN_ENTRY_PATTERNS = (
    re.compile(
        r"(^|/)(?:docs?|runbooks?|roadmap|database|migrations?|scripts?)(/|$)", re.I
    ),
    re.compile(r"\.(?:sql|mongo|md|rst)$", re.I),
    re.compile(r"(^|/)(?:README|CHANGELOG)(?:\.|$)", re.I),
)
FORBIDDEN_TEXT_PATTERNS = (
    re.compile(rb"https?://(?:localhost|127\.0\.0\.1|10\.0\.2\.2)(?:[:/]|$)", re.I),
    re.compile(rb"https?://[^\s\"']+/(?:admin|internal)(?:[/\s\"']|$)", re.I),
    re.compile(rb"(?:/home/|[A-Z]:\\Users\\)", re.I),
)
TEXT_EXTENSIONS = {".html", ".js", ".css", ".json", ".xml", ".txt"}
FORBIDDEN_PERMISSIONS = {
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.READ_MEDIA_VIDEO",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    "android.permission.READ_PHONE_STATE",
    "android.permission.CALL_PHONE",
    "android.permission.READ_SMS",
    "android.permission.SEND_SMS",
    "android.permission.BLUETOOTH_CONNECT",
    "com.google.android.gms.permission.AD_ID",
    "android.permission.ACCESS_ADSERVICES_AD_ID",
    "android.permission.ACCESS_ADSERVICES_ATTRIBUTION",
}


def forbidden_entries(names: list[str]) -> list[str]:
    return sorted(
        name
        for name in names
        if any(pattern.search(name) for pattern in FORBIDDEN_ENTRY_PATTERNS)
    )


def forbidden_text(name: str, content: bytes) -> list[str]:
    if Path(name).suffix.lower() not in TEXT_EXTENSIONS:
        return []
    return [
        pattern.pattern.decode("ascii")
        for pattern in FORBIDDEN_TEXT_PATTERNS
        if pattern.search(content)
    ]


def locate_apksigner(android_sdk: Path | None) -> Path | None:
    if android_sdk:
        candidates = sorted(
            [
                *(android_sdk / "build-tools").glob("*/apksigner"),
                *(android_sdk / "build-tools").glob("*/apksigner.bat"),
            ]
        )
        if candidates:
            return candidates[-1]
    result = subprocess.run(
        ["bash", "-lc", "command -v apksigner"], capture_output=True, text=True
    )
    return (
        Path(result.stdout.strip())
        if result.returncode == 0 and result.stdout.strip()
        else None
    )


def locate_aapt(android_sdk: Path | None) -> Path | None:
    if android_sdk:
        candidates = sorted(
            [
                *(android_sdk / "build-tools").glob("*/aapt"),
                *(android_sdk / "build-tools").glob("*/aapt.exe"),
            ]
        )
        if candidates:
            return candidates[-1]
    result = subprocess.run(
        ["bash", "-lc", "command -v aapt"], capture_output=True, text=True
    )
    return (
        Path(result.stdout.strip())
        if result.returncode == 0 and result.stdout.strip()
        else None
    )


def verify_permissions(apk: Path, aapt: Path | None) -> list[str]:
    if aapt is None:
        return ["aapt nao encontrado; permissoes compiladas nao podem ser comprovadas"]
    result = subprocess.run(
        [str(aapt), "dump", "badging", str(apk)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return [
            "aapt nao conseguiu ler o manifesto compilado: "
            + (result.stderr.strip() or result.stdout.strip())
        ]
    permissions = set(
        re.findall(r"^uses-permission: name='([^']+)'", result.stdout, re.M)
    )
    errors: list[str] = []
    if "android.permission.INTERNET" not in permissions:
        errors.append("APK nao declara a permissao de rede obrigatoria")
    forbidden = sorted(permissions & FORBIDDEN_PERMISSIONS)
    if forbidden:
        errors.append(
            "APK declara permissoes proibidas ou nao justificadas: "
            + ", ".join(forbidden)
        )
    return errors


def verify_signature(apk: Path, apksigner: Path, require_release: bool) -> list[str]:
    command = [str(apksigner), "verify", "--verbose", "--print-certs", str(apk)]
    if apksigner.suffix.lower() == ".bat":
        cmd_executable = shutil.which("cmd.exe")
        if cmd_executable is None:
            windows_cmd = Path("/mnt/c/Windows/System32/cmd.exe")
            cmd_executable = str(windows_cmd) if windows_cmd.is_file() else None
        if cmd_executable is None or shutil.which("wslpath") is None:
            return [
                "cmd.exe/wslpath indisponivel para executar o apksigner do SDK Windows"
            ]
        converted = [
            subprocess.run(
                ["wslpath", "-w", str(path)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            for path in (apksigner, apk.resolve())
        ]
        command = [
            cmd_executable,
            "/d",
            "/c",
            converted[0],
            "verify",
            "--verbose",
            "--print-certs",
            converted[1],
        ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return [
            "assinatura APK invalida: "
            + (result.stderr.strip() or result.stdout.strip())
        ]
    output = result.stdout + result.stderr
    errors: list[str] = []
    if require_release and re.search(r"Android Debug|CN=Android Debug", output, re.I):
        errors.append("artefato release usa certificado Android Debug")
    if "Verified using v2 scheme (APK Signature Scheme v2): true" not in output:
        errors.append("APK nao possui assinatura v2 valida")
    return errors


def audit(
    apk: Path, apksigner: Path | None, aapt: Path | None, require_release: bool
) -> list[str]:
    errors: list[str] = []
    if not apk.is_file():
        return [f"APK ausente: {apk}"]
    try:
        with zipfile.ZipFile(apk) as archive:
            names = archive.namelist()
            for name in forbidden_entries(names):
                errors.append(f"conteudo proibido embarcado: {name}")
            for name in names:
                for pattern in forbidden_text(name, archive.read(name)):
                    errors.append(f"texto proibido em {name}: {pattern}")
    except zipfile.BadZipFile:
        return [f"arquivo nao e um APK/ZIP valido: {apk}"]
    if apksigner is None:
        errors.append("apksigner nao encontrado; assinatura nao pode ser comprovada")
    else:
        errors.extend(verify_signature(apk, apksigner, require_release))
    errors.extend(verify_permissions(apk, aapt))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("--android-sdk", type=Path)
    parser.add_argument("--require-release-signature", action="store_true")
    args = parser.parse_args()
    errors = audit(
        args.apk,
        locate_apksigner(args.android_sdk),
        locate_aapt(args.android_sdk),
        args.require_release_signature,
    )
    if errors:
        print("Auditoria do APK Valley reprovada:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Auditoria do APK Valley aprovada: {args.apk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
