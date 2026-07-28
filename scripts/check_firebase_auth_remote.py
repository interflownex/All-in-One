#!/usr/bin/env python3
"""Confirma o projeto, app, certificados e Google provider no Firebase remoto."""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from scripts.secure_http import require_https_url

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/autonomy/firebase_auth_policy.json"
GCLOUD = Path.home() / "google-cloud-sdk/bin/gcloud"
ALLOWED_GOOGLE_API_HOSTS = {
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com",
    "apikeys.googleapis.com",
}


def access_token() -> str:
    result = subprocess.run(
        [str(GCLOUD), "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.stdout.strip()


def get_json(url: str, token: str, project_id: str) -> dict:
    safe_url = require_https_url(url, allowed_hosts=ALLOWED_GOOGLE_API_HOSTS)
    http_request = urllib.request.Request(
        safe_url,
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": project_id,
        },
    )
    try:
        # A URL foi validada por HTTPS, porta padrão e allowlist exata de hosts.
        with urllib.request.urlopen(http_request, timeout=45) as response:  # nosec B310
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Firebase remoto respondeu HTTP {error.code}: {detail}"
        ) from error


def normalized_hash(value: str) -> str:
    return value.replace(":", "").lower()


def check_remote() -> list[str]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    project_id = policy["project_id"]
    app_id = policy["android_app_id"]
    token = access_token()
    errors: list[str] = []

    project = get_json(
        f"https://firebase.googleapis.com/v1beta1/projects/{project_id}",
        token,
        project_id,
    )
    if project.get("projectId") != project_id or project.get("state") != "ACTIVE":
        errors.append("Projeto Firebase remoto ausente ou inativo.")

    app = get_json(
        f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/androidApps/{app_id}",
        token,
        project_id,
    )
    if (
        app.get("packageName") != policy["android_package"]
        or app.get("state") != "ACTIVE"
    ):
        errors.append(
            "App Android Firebase remoto ausente, inativo ou com pacote divergente."
        )

    certificates = get_json(
        f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/androidApps/{app_id}/sha",
        token,
        project_id,
    ).get("certificates", [])
    remote = {(entry.get("certType"), entry.get("shaHash")) for entry in certificates}
    for variant in ("debug", "release"):
        expected = policy["certificates"][variant]
        for key, cert_type in (("sha1", "SHA_1"), ("sha256", "SHA_256")):
            if (cert_type, normalized_hash(expected[key])) not in remote:
                errors.append(f"Fingerprint remoto ausente: {variant}.{key}.")

    provider = get_json(
        "https://identitytoolkit.googleapis.com/admin/v2/"
        f"projects/{project_id}/defaultSupportedIdpConfigs/google.com",
        token,
        project_id,
    )
    if provider.get("enabled") is not True or not provider.get("clientId"):
        errors.append("Provider Google do Firebase Authentication nao esta habilitado.")

    key = get_json(
        "https://apikeys.googleapis.com/v2/"
        f"projects/{policy['project_number']}/locations/global/keys/{policy['android_api_key_id']}",
        token,
        project_id,
    )
    allowed = {
        (entry.get("packageName"), entry.get("sha1Fingerprint", "").lower())
        for entry in key.get("restrictions", {})
        .get("androidKeyRestrictions", {})
        .get("allowedApplications", [])
    }
    for variant in ("debug", "release"):
        expected = (
            policy["android_package"],
            normalized_hash(policy["certificates"][variant]["sha1"]),
        )
        if expected not in allowed:
            errors.append(f"Chave API Firebase nao autoriza a assinatura {variant}.")
    return errors


def main() -> int:
    try:
        errors = check_remote()
    except (RuntimeError, subprocess.SubprocessError, OSError, ValueError) as error:
        print(f"Falha ao validar Firebase remoto: {error}")
        return 2
    if errors:
        print("Firebase remoto divergente:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Firebase remoto validado: projeto, Android app, quatro fingerprints, "
        "Google provider e chave API Android restrita."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
