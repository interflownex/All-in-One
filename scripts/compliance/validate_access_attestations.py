from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SECRET_PATTERN = re.compile(r"(?i)(api[_-]?key|client[_-]?secret|private[_-]?key|password|token)\s*[:=]")
APPROVED_STATUSES = {"approved", "confirmed"}


def validate(registry: dict, contract: dict) -> list[str]:
    errors: list[str] = []
    assets = {item["asset"] for item in registry.get("assets", [])}
    required = contract.get("required_evidence", {})
    seen: set[tuple[str, str]] = set()

    for index, attestation in enumerate(contract.get("attestations", [])):
        kind = attestation.get("type")
        asset = attestation.get("asset")
        prefix = f"attestations[{index}]"

        if kind not in required:
            errors.append(f"{prefix}: unknown evidence type")
            continue
        if asset not in assets:
            errors.append(f"{prefix}: unregistered asset")

        key = (str(kind), str(asset))
        if key in seen:
            errors.append(f"{prefix}: duplicate evidence for asset and type")
        seen.add(key)

        for field in required[kind]["fields"]:
            value = attestation.get(field)
            if value is None or value == "":
                errors.append(f"{prefix}: missing required field {field}")

        reference = str(attestation.get("evidence_reference", ""))
        if SECRET_PATTERN.search(reference):
            errors.append(f"{prefix}: evidence reference appears to contain a secret")

        status = attestation.get("review_status", attestation.get("validation_status"))
        if status is not None and status not in APPROVED_STATUSES:
            errors.append(f"{prefix}: pending or rejected evidence cannot activate access")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    registry = json.loads((root / "config/compliance/access_assets.v1.json").read_text(encoding="utf-8"))
    contract = json.loads((root / "config/compliance/access_attestations.v1.json").read_text(encoding="utf-8"))
    errors = validate(registry, contract)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("access attestations: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
