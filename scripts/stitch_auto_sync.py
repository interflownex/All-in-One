from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.stitch_orchestrator import (
    load_state,
    sync_summary,
    write_manifest,
)
from scripts.validate_stitch_mcp_config import validate_stitch_mcp_config

LEGACY_NOTICE = (
    "A sincronizacao remota legada por modulo foi desativada. "
    "Use scripts/codex_stitch_director.py para coordenar diretamente "
    "os quatro projetos agregadores oficiais."
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compatibilidade somente leitura da antiga sincronizacao Stitch por modulo."
    )
    parser.add_argument(
        "--require-remote",
        action="store_true",
        help="Mantido somente para detectar chamadas antigas; escrita remota e bloqueada.",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Falha se o estado historico estiver incompleto.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida e mostra o estado historico sem chamar o MCP remoto.",
    )
    parser.add_argument(
        "--max-operations",
        type=int,
        default=None,
        help="Argumento legado sem efeito; nenhuma operacao remota e permitida.",
    )
    args = parser.parse_args()

    if args.require_remote or not args.dry_run:
        print(LEGACY_NOTICE)
        return 2

    manifest = write_manifest()
    errors = validate_stitch_mcp_config(require_codex_config=False)
    if errors:
        print("\nFalhas de validacao do estado Stitch legado:")
        for error in errors:
            print(f"- {error}")
        return 1

    summary = sync_summary(manifest, load_state())
    summary["mode"] = "legacy_read_only"
    summary["authoritative_director"] = "scripts/codex_stitch_director.py"
    print(json.dumps(summary, indent=2, ensure_ascii=True))

    if args.require_complete and (
        summary["synced_projects"] != summary["expected_projects"]
        or summary["synced_screens"] != summary["expected_screens"]
        or summary["branding_pending"]
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
