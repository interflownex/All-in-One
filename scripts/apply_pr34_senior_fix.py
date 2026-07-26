#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PARTS = sorted((ROOT / "scripts" / ".pr34_payload").glob("part*.txt"))
source = "".join(path.read_text(encoding="utf-8") for path in PARTS)
for path in PARTS:
    path.unlink()
payload_dir = ROOT / "scripts" / ".pr34_payload"
payload_dir.rmdir()
exec(compile(source, str(Path(__file__).resolve()), "exec"), {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"})
