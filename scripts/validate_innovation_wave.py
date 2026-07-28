#!/usr/bin/env python3
"""Valida a cobertura da onda de inovacao contra o catalogo oficial de modulos."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.shared.innovation_runtime import (  # noqa: E402
    InnovationCatalogError,
    innovation_summary,
    load_innovation_catalog,
)


def main() -> int:
    try:
        definitions = load_innovation_catalog()
        summary = innovation_summary()
    except InnovationCatalogError as exc:
        print(f"innovation-wave: FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "wave_id": summary["wave_id"],
                "module_count": len(definitions),
                "priorities": summary["priorities"],
                "enabled": summary["enabled"],
                "forbidden_modules": summary["forbidden_modules"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
