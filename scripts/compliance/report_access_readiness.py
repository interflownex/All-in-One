from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ASSETS_PATH = ROOT / "config" / "compliance" / "access_assets.v1.json"
ATTESTATIONS_PATH = ROOT / "config" / "compliance" / "access_attestations.v1.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(
    assets_contract: dict[str, Any], attestations_contract: dict[str, Any]
) -> dict[str, Any]:
    required_types = {
        evidence_type
        for evidence_type, definition in attestations_contract["required_evidence"].items()
        if definition.get("required") is True
    }

    accepted_by_asset: dict[str, set[str]] = {}
    for attestation in attestations_contract.get("attestations", []):
        if attestation.get("status") != "accepted":
            continue
        asset = attestation.get("asset")
        evidence_type = attestation.get("evidence_type")
        if isinstance(asset, str) and isinstance(evidence_type, str):
            accepted_by_asset.setdefault(asset, set()).add(evidence_type)

    assets: list[dict[str, Any]] = []
    all_ready = True
    for asset in assets_contract["assets"]:
        name = asset["asset"]
        accepted = accepted_by_asset.get(name, set())
        missing = sorted(required_types - accepted)
        contract_blockers = sorted(set(asset.get("blockers", [])))
        ready = (
            not missing
            and not contract_blockers
            and asset.get("production_activation_blocked") is False
            and asset.get("access_mode") != "deny_all"
        )
        all_ready = all_ready and ready
        assets.append(
            {
                "asset": name,
                "ready": ready,
                "access_mode": asset.get("access_mode"),
                "production_activation_blocked": asset.get(
                    "production_activation_blocked", True
                ),
                "accepted_evidence": sorted(accepted),
                "missing_required_evidence": missing,
                "contract_blockers": contract_blockers,
            }
        )

    return {
        "issue": assets_contract["issue"],
        "default_effect": assets_contract["default_effect"],
        "ready": all_ready and bool(assets),
        "asset_count": len(assets),
        "assets": assets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a machine-readable fail-closed access readiness report."
    )
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit with status 1 when any registered asset is not ready.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for the JSON report. Defaults to stdout.",
    )
    args = parser.parse_args()

    report = build_report(_load(ASSETS_PATH), _load(ATTESTATIONS_PATH))
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.require_ready and report["ready"] is not True:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
