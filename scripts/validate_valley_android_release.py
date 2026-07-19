#!/usr/bin/env python3
"""Falha quando o contrato minimo de seguranca do APK Valley regride."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "apps" / "valley-android"


def require(text: str, marker: str, source: Path, errors: list[str]) -> None:
    if marker not in text:
        errors.append(f"{source.relative_to(ROOT)}: marcador obrigatorio ausente: {marker}")


def validate() -> list[str]:
    errors: list[str] = []
    gradle_path = ANDROID / "app" / "build.gradle.kts"
    manifest_path = ANDROID / "app" / "src" / "main" / "AndroidManifest.xml"
    network_path = ANDROID / "app" / "src" / "main" / "res" / "xml" / "network_security_config.xml"
    source_root = ANDROID / "app" / "src" / "main" / "java"
    secure_store_path = source_root / "com" / "example" / "valley" / "security" / "SecureSessionStore.kt"
    integrity_path = source_root / "com" / "example" / "valley" / "security" / "PlayIntegrityAttestor.kt"
    catalog_source = ROOT / "apps" / "valley" / "src"
    gradle = gradle_path.read_text(encoding="utf-8")
    manifest = manifest_path.read_text(encoding="utf-8")
    network = network_path.read_text(encoding="utf-8")
    secure_store = secure_store_path.read_text(encoding="utf-8")
    integrity = integrity_path.read_text(encoding="utf-8")

    for marker in (
        'create("staging")',
        "isDebuggable = false",
        "isMinifyEnabled = true",
        "isShrinkResources = true",
        'signingConfigs.findByName("release")',
        "releaseRequested && !releaseSigningPropertiesFile.isFile",
        "VALLEY_PLAY_INTEGRITY_CLOUD_PROJECT_NUMBER",
        "releaseRequested && playIntegrityCloudProjectNumber == \"0\"",
        "implementation(libs.play.integrity)",
    ):
        require(gradle, marker, gradle_path, errors)
    if re.search(r"release\s*\{[^}]*signingConfig\s*=\s*signingConfigs\.getByName\(\"debug\"\)", gradle, re.S):
        errors.append("release referencia explicitamente a assinatura debug")
    if re.search(r"packaging\s*\{[^}]*keepDebugSymbols", gradle, re.S):
        errors.append("configuracao global preserva simbolos nativos no release")
    for variant in ("debug", "staging"):
        require(
            gradle,
            f'selector().withBuildType("{variant}")',
            gradle_path,
            errors,
        )

    for marker in (
        'android:allowBackup="false"',
        'android:fullBackupContent="false"',
        'android:usesCleartextTraffic="false"',
        'android:networkSecurityConfig="@xml/network_security_config"',
    ):
        require(manifest, marker, manifest_path, errors)
    require(network, 'cleartextTrafficPermitted="false"', network_path, errors)

    for marker in ("AndroidKeyStore", "AES/GCM/NoPadding", "KeyGenParameterSpec", "setKeySize(256)"):
        require(secure_store, marker, secure_store_path, errors)
    for marker in ("IntegrityManagerFactory.createStandard", "setCloudProjectNumber", "setRequestHash"):
        require(integrity, marker, integrity_path, errors)

    kotlin_sources = "\n".join(path.read_text(encoding="utf-8") for path in source_root.rglob("*.kt"))
    if re.search(r'putString\(\s*"(?:token|password|refresh_token)"', kotlin_sources):
        errors.append("credencial sensivel persiste em SharedPreferences sem envelope criptografado")
    if "buildDemoSession(" in kotlin_sources:
        errors.append("aplicativo Android ainda aceita sessao local simulada quando o backend falha")

    web_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in catalog_source.rglob("*")
        if path.is_file() and path.suffix in {".ts", ".tsx"}
    )
    if re.search(r'localStorage\.(?:getItem|setItem)\(\s*[\'\"]valley\.session\.(?:token|user-id)', web_sources):
        errors.append("sessao web sensivel persiste em localStorage")
    if "ws://localhost" in web_sources or "http://localhost" in web_sources:
        errors.append("fonte Valley contem endpoint local inseguro que pode vazar para o APK")

    permissions = re.findall(r'<uses-permission[^>]+android:name="([^"]+)"', manifest)
    unexpected = sorted(set(permissions) - {"android.permission.INTERNET"})
    if unexpected:
        errors.append("permissoes Android fora da allowlist: " + ", ".join(unexpected))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Contrato de release Valley reprovado:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Contrato de release Valley aprovado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
