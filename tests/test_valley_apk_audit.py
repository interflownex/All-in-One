from __future__ import annotations

from scripts.audit_valley_apk import forbidden_entries, forbidden_text


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
    assert forbidden_entries(["assets/valley/index.html", "assets/valley/catalog.json"]) == []
    assert forbidden_text("assets/valley/index.js", b"https://api.valley.example/v1/catalog") == []


def test_apk_audit_rejects_local_and_administrative_endpoints() -> None:
    assert forbidden_text("assets/index.js", b"http://localhost:8000/admin")
    assert forbidden_text("assets/index.js", b"https://api.example/internal/session")
    assert forbidden_text("assets/index.js", b"/home/developer/private/file")
