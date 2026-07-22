from __future__ import annotations

import sys

from modules.shared.retention_worker import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
