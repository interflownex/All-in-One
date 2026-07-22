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
    sync_projects,
    sync_summary,
    write_manifest,
)
from scripts.validate_stitch_mcp_config import (
    is_stitch_enabled,
    validate_stitch_mcp_config,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Executa plano, validacao e sincronizacao remota do Stitch."
    )
    parser.add_argument(
        "--require-remote",
        action="store_true",
        help="Falha quando STITCH_API_KEY nao estiver presente.",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Falha se o estado Stitch ainda nao cobrir todos os projetos e telas.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Valida e mostra o status sem chamar o MCP remoto.",
    )
    parser.add_argument(
        "--max-operations",
        type=int,
        default=None,
        help="Limita criacoes/edicoes remotas para execucoes resumiveis.",
    )
    args = parser.parse_args()

    manifest = write_manifest()
    errors = validate_stitch_mcp_config(
        require_secret=args.require_remote,
        require_codex_config=not args.dry_run or args.require_remote,
    )
    if errors:
        print("\nFalhas de validacao do sync Stitch:")
        for error in errors:
            print(f"- {error}")
        return 1

    if not is_stitch_enabled():
        state = load_state()
    elif not args.dry_run:
        state = sync_projects(manifest, max_operations=args.max_operations)
    else:
        state = load_state()

    summary = sync_summary(manifest, state)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    if args.require_complete and (
        summary["synced_projects"] != summary["expected_projects"]
        or summary["synced_screens"] != summary["expected_screens"]
        or summary["branding_pending"]
    ):
        print("\nSincronizacao Stitch remota incompleta.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
