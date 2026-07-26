#!/usr/bin/env python3
from pathlib import Path
import base64
import gzip
import shutil

ROOT = Path(__file__).resolve().parents[1]
payload_dir = ROOT / "scripts" / ".pr34_payload_gz"
parts = sorted(payload_dir.glob("part*.txt"))
encoded = "".join(path.read_text(encoding="ascii") for path in parts)
source = gzip.decompress(base64.b64decode(encoded)).decode("utf-8")
for path in parts:
    path.unlink()
payload_dir.rmdir()
shutil.rmtree(ROOT / "scripts" / ".pr34_payload", ignore_errors=True)
corrupt_patch = ROOT / "reports" / "ci" / "fix-pr34.patch.gz"
corrupt_patch.unlink(missing_ok=True)
exec(compile(source, str(Path(__file__).resolve()), "exec"), {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"})
