"""Legacy remote Stitch writer.

The public Codex flow no longer uses this module to perform remote writes.
"""

from __future__ import annotations

import sys


def main() -> int:
    message = "sincronizacao remota legada por modulo foi desativada"
    print(message, file=sys.stderr)
    raise RuntimeError(message)


if __name__ == "__main__":
    raise SystemExit(main())

