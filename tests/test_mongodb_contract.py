from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "database" / "mongodb_contract.json"
INIT_SCRIPT = ROOT / "database" / "mongodb" / "init" / "001_ai_social_telemetry.js"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _init_script() -> str:
    return INIT_SCRIPT.read_text(encoding="utf-8")


def _js_object_literal(payload: dict) -> str:
    parts = []
    for key, value in payload.items():
        rendered = f'"{value}"' if isinstance(value, str) else str(value).lower()
        parts.append(f"{key}:{rendered}")
    return "{" + ",".join(parts) + "}"


def test_mongodb_contract_declares_expected_collections_and_retention() -> None:
    contract = _contract()

    assert contract["database_env"] == "MONGO_INITDB_DATABASE"
    assert set(contract["collections"]) == {
        "ai_memory",
        "social_videos",
        "influencer_metrics",
        "telemetry_logs",
    }
    assert any(
        index["keys"] == {"retention_until": 1}
        and index.get("options", {}).get("expireAfterSeconds") == 0
        for collection in contract["collections"].values()
        for index in collection["indexes"]
    )


def test_mongodb_init_script_matches_collection_contract() -> None:
    contract = _contract()
    script = _init_script()

    for collection, spec in contract["collections"].items():
        assert f'createValidatedCollection("{collection}"' in script
        for field in spec["required"]:
            assert f'"{field}"' in script


def test_mongodb_init_script_declares_all_contract_indexes() -> None:
    contract = _contract()
    compact_script = "".join(_init_script().split())

    for collection, spec in contract["collections"].items():
        for index in spec["indexes"]:
            keys = _js_object_literal(index["keys"])
            assert f"db.{collection}.createIndex({keys}" in compact_script
            options = index.get("options", {})
            if options.get("expireAfterSeconds") == 0:
                assert "expireAfterSeconds:0" in compact_script
            if options.get("unique") is True:
                assert "unique:true" in compact_script


def test_mongodb_sensitive_fields_are_documented_in_contract() -> None:
    contract = _contract()

    for collection, spec in contract["collections"].items():
        assert spec["purpose"]
        assert spec["sensitive_fields"], collection
