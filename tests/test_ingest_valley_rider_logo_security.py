from __future__ import annotations

import stat
from pathlib import Path

from scripts.branding import ingest_valley_rider_logo


def test_atomic_copy_restricts_destination_to_owner(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    destination = tmp_path / "nested" / "logo.png"
    payload = b"official-logo-bytes"
    source.write_bytes(payload)

    ingest_valley_rider_logo.atomic_copy(source, destination)

    assert destination.read_bytes() == payload
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600
