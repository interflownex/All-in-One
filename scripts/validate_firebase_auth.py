#!/usr/bin/env python3
"""Valida o contrato versionado do Firebase Auth no Valley Android."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/autonomy/firebase_auth_policy.json"
ANDROID = ROOT / "apps/valley-android"
GOOGLE_SERVICES = ANDROID / "app/google-services.json"


def validate() -> list[str]:
    errors: list[str] = []
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    config = json.loads(GOOGLE_SERVICES.read_text(encoding="utf-8"))
    project = config.get("project_info", {})
    clients = config.get("client", [])
    client = clients[0] if len(clients) == 1 else {}
    client_info = client.get("client_info", {})
    android_info = client_info.get("android_client_info", {})
    oauth_clients = client.get("oauth_client", [])

    expected = {
        "project_id": project.get("project_id"),
        "project_number": project.get("project_number"),
        "android_app_id": client_info.get("mobilesdk_app_id"),
        "android_package": android_info.get("package_name"),
    }
    for key, actual in expected.items():
        if policy.get(key) != actual:
            errors.append(
                f"Firebase {key} divergente: politica={policy.get(key)!r}, config={actual!r}."
            )
    if not any(
        entry.get("client_type") == 3 and entry.get("client_id")
        for entry in oauth_clients
    ):
        errors.append(
            "google-services.json nao contem OAuth web client para Credential Manager."
        )

    catalog = (ANDROID / "gradle/libs.versions.toml").read_text(encoding="utf-8")
    app_gradle = (ANDROID / "app/build.gradle.kts").read_text(encoding="utf-8")
    main_screen = (
        ANDROID / "app/src/main/java/com/example/valley/ui/main/MainScreen.kt"
    ).read_text(encoding="utf-8")
    required_catalog = ("firebase-auth", "androidx-credentials", "google-services")
    for marker in required_catalog:
        if marker not in catalog:
            errors.append(
                f"Catalogo Android sem dependencia/plugin obrigatorio: {marker}."
            )
    for marker in (
        "libs.plugins.google.services",
        "libs.firebase.auth",
        "libs.googleid",
    ):
        if marker not in app_gradle:
            errors.append(f"Gradle Android sem integracao Firebase: {marker}.")
    for marker in (
        "GetGoogleIdOption",
        "GoogleIdTokenCredential",
        "GoogleAuthProvider.getCredential",
        "signInWithCredential",
    ):
        if marker not in main_screen:
            errors.append(f"Login Android sem etapa Firebase obrigatoria: {marker}.")

    forbidden_suffixes = (".jks", ".keystore")
    tracked_files = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    for relative in tracked_files:
        if any(relative.endswith(suffix) for suffix in forbidden_suffixes):
            errors.append(f"Keystore nao pode ser versionado: {relative}.")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Falhas na configuracao Firebase Auth:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Firebase Auth validado: projeto, app Android, Credential Manager e assinatura externa coerentes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
