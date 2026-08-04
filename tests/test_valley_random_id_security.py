from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps/valley/src/lib/valleyPlatform.ts"
ANDROID_ASSETS = ROOT / "apps/valley-android/app/src/main/assets/valley"


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


def test_generated_android_assets_include_cryptographic_random_id() -> None:
    javascript = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in ANDROID_ASSETS.rglob("*.js")
    )

    # Bundles include third-party framework code. React itself uses Math.random
    # for internal property-name isolation, which is unrelated to Valley IDs.
    # The security contract here verifies that the compiled Valley implementation
    # contains the Web Crypto primitive required by the source-level test above.
    assert "getRandomValues" in javascript
