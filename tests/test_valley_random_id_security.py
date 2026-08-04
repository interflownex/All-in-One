from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps/valley/src/lib/valleyPlatform.ts"
ANDROID_ASSETS = ROOT / "apps/valley-android/app/src/main/assets/valley"


def _random_id_body(source: str) -> str:
    match = re.search(
        r"function\s+randomId\s*\(length:\s*number\)\s*:\s*string\s*\{(?P<body>.*?)\n\}",
        source,
        flags=re.DOTALL,
    )
    assert match is not None, "Função randomId não localizada na fonte Valley."
    return match.group("body")


def test_random_id_uses_browser_cryptographic_randomness() -> None:
    body = _random_id_body(SOURCE.read_text(encoding="utf-8"))

    assert "crypto.getRandomValues" in body
    assert "Math.random" not in body


def test_generated_android_assets_do_not_keep_insecure_random_id() -> None:
    javascript = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in ANDROID_ASSETS.rglob("*.js")
    )

    assert "Math.random().toString(36)" not in javascript
