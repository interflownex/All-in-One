from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "apps" / "valley-android" / "app" / "src" / "main"


def test_mobile_telemetry_is_opt_in_and_granular() -> None:
    contract = json.loads(
        (
            ROOT / "config" / "observability" / "valley_mobile_observability.json"
        ).read_text(encoding="utf-8")
    )
    manifest = (ANDROID / "AndroidManifest.xml").read_text(encoding="utf-8")

    assert contract["privacy"]["default_collection_enabled"] is False
    assert set(contract["privacy"]["granular_consent"]) == {
        "analytics",
        "crash_reports",
    }
    assert contract["privacy"]["advertising_id_collection"] is False
    assert manifest.count('android:value="false"') >= 3


def test_mobile_event_allowlist_excludes_sensitive_fields() -> None:
    contract = json.loads(
        (
            ROOT / "config" / "observability" / "valley_mobile_observability.json"
        ).read_text(encoding="utf-8")
    )
    event_fields = set(
        contract["events"]["api_request_completed"]["allowed_parameters"]
    )
    forbidden = set(contract["privacy"]["forbidden_fields"])

    assert event_fields == {"route", "status_code", "duration_ms", "correlation_id"}
    assert event_fields.isdisjoint(forbidden)


def test_mobile_availability_and_latency_have_slos_and_runbooks() -> None:
    contract = json.loads(
        (
            ROOT / "config" / "observability" / "valley_mobile_observability.json"
        ).read_text(encoding="utf-8")
    )
    slos = contract["slos"]

    assert {"mobile_api_availability", "mobile_api_latency_p95"} <= set(slos)
    assert all(
        item["runbook"] == "docs/OPERATIONS.md#valley-mobile" for item in slos.values()
    )
