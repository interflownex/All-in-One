from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import scaffold_modules

STOCK_OPENAPI = "modules/stock/OPENAPI.yaml"
PROPERTY_MAIN = "modules/property/main.py"
CUSTOMIZED_ARTIFACTS = set(scaffold_modules.CUSTOMIZED_ARTIFACTS) | {
    STOCK_OPENAPI,
    PROPERTY_MAIN,
}


def main() -> int:
    """Executa o scaffold oficial preservando contratos especializados."""

    scaffold_modules.CUSTOMIZED_ARTIFACTS.clear()
    scaffold_modules.CUSTOMIZED_ARTIFACTS.update(CUSTOMIZED_ARTIFACTS)
    return scaffold_modules.main()


if __name__ == "__main__":
    raise SystemExit(main())
