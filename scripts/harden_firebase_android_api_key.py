#!/usr/bin/env python3
"""Restringe a chave cliente Firebase aos certificados Android autorizados."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

from scripts.secure_http import require_https_url

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/autonomy/firebase_auth_policy.json"
GCLOUD = Path.home() / "google-cloud-sdk/bin/gcloud"
ALLOWED_API_HOSTS = {"apikeys.googleapis.com"}


def access_token() -> str:
    return subprocess.run(
        [str(GCLOUD), "auth", "application-default", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    ).stdout.strip()


def request_json(
    url: str,
    token: str,
    project_id: str,
    *,
    method: str = "GET",
    body: dict | None = None,
) -> dict:
    safe_url = require_https_url(url, allowed_hosts=ALLOWED_API_HOSTS)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    http_request = urllib.request.Request(
        safe_url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": project_id,
            "Content-Type": "application/json",
        },
    )
    # A URL foi validada por HTTPS, porta padrão e allowlist exata de host.
    with urllib.request.urlopen(http_request, timeout=60) as response:  # nosec B310
        return json.load(response)


def main() -> int:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    project_id = policy["project_id"]
    key_name = (
        f"projects/{policy['project_number']}/locations/global/keys/"
        f"{policy['android_api_key_id']}"
    )
    token = access_token()
    url = f"https://apikeys.googleapis.com/v2/{key_name}"
    key = request_json(url, token, project_id)
    restrictions = key.get("restrictions", {})
    restrictions["androidKeyRestrictions"] = {
        "allowedApplications": [
            {
                "packageName": policy["android_package"],
                "sha1Fingerprint": policy["certificates"][variant]["sha1"],
            }
            for variant in ("debug", "release")
        ]
    }
    operation = request_json(
        url + "?" + urllib.parse.urlencode({"updateMask": "restrictions"}),
        token,
        project_id,
        method="PATCH",
        body={"name": key_name, "restrictions": restrictions, "etag": key.get("etag")},
    )
    operation_name = operation["name"]
    operation_url = f"https://apikeys.googleapis.com/v2/{operation_name}"
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        result = request_json(operation_url, token, project_id)
        if result.get("done"):
            if result.get("error"):
                raise RuntimeError(
                    f"Falha ao restringir chave Firebase: {result['error']}"
                )
            print(
                "Chave Firebase Android restrita ao pacote Valley e aos certificados debug/release."
            )
            return 0
        time.sleep(2)
    raise RuntimeError("Timeout ao aguardar restricao da chave Firebase.")


if __name__ == "__main__":
    raise SystemExit(main())
