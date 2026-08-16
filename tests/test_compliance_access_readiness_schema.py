from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "config" / "compliance" / "access_readiness_report.schema.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class AccessReadinessSchemaTest(unittest.TestCase):
    def test_readiness_schema_is_closed_and_versioned(self) -> None:
        schema = _load(SCHEMA_PATH)

        self.assertEqual(
            schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
        )
        self.assertTrue(schema["$id"].endswith("access-readiness-report.v1.json"))
        self.assertEqual(schema["type"], "object")
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(
            set(schema["required"]),
            {
                "issue",
                "default_effect",
                "ready",
                "asset_count",
                "assets",
            },
        )
        self.assertEqual(schema["properties"]["issue"]["const"], 204)
        self.assertEqual(schema["properties"]["default_effect"]["const"], "deny")
