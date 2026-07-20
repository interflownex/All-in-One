from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECURITY_SOURCE = (
    ROOT
    / "apps"
    / "valley-android"
    / "app"
    / "src"
    / "main"
    / "java"
    / "com"
    / "example"
    / "valley"
    / "security"
    / "RuntimeIntegrityGuard.kt"
)


def test_masvs_resilience_contract_covers_all_resilience_controls() -> None:
    policy = json.loads((ROOT / "config" / "security" / "valley_masvs_resilience.json").read_text())

    assert policy["profile"] == "MASVS-R"
    assert set(policy["controls"]) == {
        "MASVS-RESILIENCE-1",
        "MASVS-RESILIENCE-2",
        "MASVS-RESILIENCE-3",
        "MASVS-RESILIENCE-4",
    }
    assert "server-side Play Integrity verdict validation is mandatory before production" in policy["limitations"]


def test_release_guard_detects_root_debugger_instrumentation_and_repackaging() -> None:
    source = SECURITY_SOURCE.read_text(encoding="utf-8")

    for marker in (
        "BuildConfig.DEBUG",
        "Debug.isDebuggerConnected()",
        "TracerPid:",
        "/system/xbin/su",
        "/data/adb/magisk",
        "frida",
        "xposed",
        "substrate",
        "zygisk",
        "hasSigningCertificate",
        "CERT_INPUT_SHA256",
    ):
        assert marker in source


def test_runtime_guard_does_not_collect_sensitive_runtime_details() -> None:
    policy = json.loads((ROOT / "config" / "security" / "valley_masvs_resilience.json").read_text())
    source = SECURITY_SOURCE.read_text(encoding="utf-8")

    assert set(policy["response"]["never_log"]) >= {"process_maps", "tokens", "user_identifiers"}
    assert "getInstalledPackages" not in source
    assert "ValleyObservability" not in source
