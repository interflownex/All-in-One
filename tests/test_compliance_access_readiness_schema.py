from __future__ import annotations

import json
from pathlib import Path

from scripts.compliance.report_access_readiness import build_report

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "config" / "compliance" / "access_readiness_report.schema.json"
ASSETS_PATH = ROOT / "config" / "compliance" / "access_assets.v1.json"
ATTESTATIONS_PATH = ROOT / "config" / "compliance" / "access_attestations.v1.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_readiness_schema_is_closed_and_versioned() -> None:
    schema = _load(SCHEMA_PATH)

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"].endswith("access-readiness-report.v1.json")
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "issue",
        "default_effect",
        "ready",
        "asset_count",
        "assets",
    }
    assert schema["properties"]["issue"]["const"] == 204
    assert schema["properties"]["default_effect"]["const"] == "deny"


def test_generated_report_matches_the_declared_contract() -> None:
    schema = _load(SCHEMA_PATH)
    report = build_report(_load(ASSETS_PATH), _load(ATTESTATIONS_PATH))

    assert set(report) == set(schema["required"])
    assert report["issue"] == schema["properties"]["issue"]["const"]
    assert report["default_effect"] == schema["properties"]["default_effect"]["const"]
    assert isinstance(report["ready"], bool)
    assert isinstance(report["asset_count"], int)
    assert report["asset_count"] == len(report["assets"])
    assert report["asset_count"] >= schema["properties"]["assets"]["minItems"]

    item_schema = schema["properties"]["assets"]["items"]
    required_asset_keys = set(item_schema["required"])
    for asset in report["assets"]:
        assert set(asset) == required_asset_keys
        assert isinstance(asset["asset"], str) and asset["asset"]
        assert isinstance(asset["ready"], bool)
        assert isinstance(asset["production_activation_blocked"], bool)
        assert asset["access_mode"] is None or isinstance(asset["access_mode"], str)
        for field in (
            "accepted_evidence",
            "missing_required_evidence",
            "contract_blockers",
        ):
            assert isinstance(asset[field], list)
            assert len(asset[field]) == len(set(asset[field]))
            assert all(isinstance(value, str) and value for value in asset[field])


def test_current_report_remains_fail_closed() -> None:
    report = build_report(_load(ASSETS_PATH), _load(ATTESTATIONS_PATH))

    assert report["ready"] is False
    assert all(asset["ready"] is False for asset in report["assets"])
