from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import audit_valley_apk
from scripts.audit_valley_apk import (
    forbidden_entries,
    forbidden_text,
    verify_permissions,
)


def test_apk_audit_rejects_internal_material() -> None:
    rejected = forbidden_entries(
        [
            "assets/valley/index.html",
            "assets/docs/runbook.md",
            "assets/database/schema.sql",
            "assets/README.txt",
        ]
    )
    assert rejected == [
        "assets/README.txt",
        "assets/database/schema.sql",
        "assets/docs/runbook.md",
    ]


def test_apk_audit_accepts_public_assets() -> None:
    assert (
        forbidden_entries(["assets/valley/index.html", "assets/valley/catalog.json"])
        == []
    )
    assert (
        forbidden_text(
            "assets/valley/index.js", b"https://api.valley.example/v1/catalog"
        )
        == []
    )


def test_apk_audit_rejects_local_and_administrative_endpoints() -> None:
    assert forbidden_text("assets/index.js", b"http://localhost:8000/admin")
    assert forbidden_text("assets/index.js", b"https://api.example/internal/session")
    assert forbidden_text("assets/index.js", b"/home/developer/private/file")


def test_apk_audit_reads_compiled_permissions_and_rejects_ad_id(monkeypatch) -> None:
    output = "\n".join(
        (
            "uses-permission: name='android.permission.INTERNET'",
            "uses-permission: name='com.google.android.gms.permission.AD_ID'",
        )
    )
    monkeypatch.setattr(
        audit_valley_apk.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, output, ""),
    )

    errors = verify_permissions(Path("valley.apk"), Path("aapt"))

    assert errors == [
        "APK declara permissoes proibidas ou nao justificadas: com.google.android.gms.permission.AD_ID"
    ]


def test_apk_audit_accepts_minimal_compiled_permissions(monkeypatch) -> None:
    output = "uses-permission: name='android.permission.INTERNET'\n"
    monkeypatch.setattr(
        audit_valley_apk.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, output, ""),
    )

    assert verify_permissions(Path("valley.apk"), Path("aapt")) == []
