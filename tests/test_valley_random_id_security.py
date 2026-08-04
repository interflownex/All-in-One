from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps/valley/src/lib/valleyPlatform.ts"


def _random_id_body(source: str) -> str:
    match = re.search(
        r"function\s+randomId\s*\(length:\s*number\)\s*(?::\s*string\s*)?\{(?P<body>.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    assert match is not None, "Função randomId não localizada na fonte Valley."
    return match.group("body")


def test_random_id_uses_browser_cryptographic_randomness() -> None:
    body = _random_id_body(SOURCE.read_text(encoding="utf-8"))

    assert re.search(r"(?:window\.)?crypto\.getRandomValues", body)
    assert "Math.random" not in body
