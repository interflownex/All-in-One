#!/usr/bin/env python3
"""Validate the executable compliance catalog and the migration gate."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.compliance_inventory import check_outputs, extract_sql_assets
except ModuleNotFoundError:
    from compliance_inventory import check_outputs, extract_sql_assets

ROOT = Path(__file__).resolve().parents[1]
BUNDLES_PATH = ROOT / "config" / "compliance" / "bundles.json"
REGISTRY_PATH = ROOT / "config" / "compliance" / "field_registry.json"
MIGRATION_BASELINE_PATH = ROOT / "config" / "compliance" / "migration_baseline.json"
MIGRATIONS_DIR = ROOT / "database" / "postgres" / "migrations"

EXPECTED_BUNDLES = {f"B{index}" for index in range(15)}
REQUIRED_METADATA = {
    "domain",
    "owner_service",
    "processing_activity",
    "purpose",
    "legal_basis",
    "sensitivity",
    "retention_policy",
    "encryption_policy",
    "masking_policy",
    "access_policy",
    "sharing_policy",
    "source_system",
    "lineage",
    "disposal_method",
    "status",
    "bundle_codes",
}
REQUIRED_PHYSICAL = {
    "field_id",
    "schema_name",
    "table_name",
    "field_name",
    "physical_type",
    "nullable",
}
FORBIDDEN_RAW_FIELD_NAMES = {
    "access_token",
    "card_number",
    "client_secret",
    "cvc",
    "cvv",
    "pan",
    "private_key",
    "raw_token",
    "refresh_token",
    "secret",
}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
VALID_STATUSES = {"planned", "active", "deprecated"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _walk_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_strings(nested)


def expand_fields(registry: dict[str, Any]) -> list[dict[str, Any]]:
    defaults = registry.get("field_defaults", {})
    return [{**defaults, **field} for field in registry.get("fields", [])]


def validate_bundles(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bundles = data.get("bundles")
    if not isinstance(bundles, list):
        return ["config/compliance/bundles.json: bundles must be a list"]

    codes: list[str] = []
    names: set[str] = set()
    for index, bundle in enumerate(bundles):
        if not isinstance(bundle, dict):
            errors.append(f"bundle[{index}] must be an object")
            continue
        missing = {"code", "name", "purpose", "required_attributes"} - set(bundle)
        if missing:
            errors.append(f"bundle[{index}] missing: {sorted(missing)}")
            continue
        code = str(bundle["code"])
        name = str(bundle["name"])
        codes.append(code)
        if name in names:
            errors.append(f"duplicate bundle name: {name}")
        names.add(name)
        attributes = bundle["required_attributes"]
        if not isinstance(attributes, list) or not attributes or not all(
            isinstance(item, str) and item.strip() for item in attributes
        ):
            errors.append(f"{code}: required_attributes must be non-empty strings")

    code_set = set(codes)
    if code_set != EXPECTED_BUNDLES:
        errors.append(
            "bundles must contain exactly B0-B14; "
            f"missing={sorted(EXPECTED_BUNDLES - code_set)}, "
            f"extra={sorted(code_set - EXPECTED_BUNDLES)}"
        )
    if len(codes) != len(code_set):
        errors.append("bundle codes must be unique")
    return errors


def validate_registry_data(
    registry: dict[str, Any], bundle_codes: set[str] = EXPECTED_BUNDLES
) -> list[str]:
    errors: list[str] = []
    defaults = registry.get("field_defaults")
    raw_fields = registry.get("fields")
    if not isinstance(defaults, dict):
        errors.append("field_registry.json: field_defaults must be an object")
        defaults = {}
    if not isinstance(raw_fields, list):
        errors.append("field_registry.json: fields must be a list")
        raw_fields = []

    missing_defaults = REQUIRED_METADATA - set(defaults)
    if missing_defaults:
        errors.append(f"field_defaults missing: {sorted(missing_defaults)}")

    seen_ids: set[str] = set()
    seen_logical: set[tuple[str, str, str]] = set()

    for index, raw in enumerate(raw_fields):
        if not isinstance(raw, dict):
            errors.append(f"field[{index}] must be an object")
            continue
        field = {**defaults, **raw}
        missing = (REQUIRED_METADATA | REQUIRED_PHYSICAL) - set(field)
        if missing:
            errors.append(f"field[{index}] missing: {sorted(missing)}")
            continue

        field_id = str(field["field_id"])
        logical = (
            str(field["schema_name"]).lower(),
            str(field["table_name"]).lower(),
            str(field["field_name"]).lower(),
        )
        expected_id = ".".join(logical)
        if field_id != expected_id:
            errors.append(f"{field_id}: field_id must equal {expected_id}")
        if field_id in seen_ids:
            errors.append(f"duplicate field_id: {field_id}")
        seen_ids.add(field_id)
        if logical in seen_logical:
            errors.append(f"duplicate logical field: {expected_id}")
        seen_logical.add(logical)

        for key in REQUIRED_METADATA - {"lineage", "bundle_codes"}:
            value = field.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field_id}: {key} must be a non-empty string")

        if not isinstance(field.get("nullable"), bool):
            errors.append(f"{field_id}: nullable must be boolean")
        if field.get("status") not in VALID_STATUSES:
            errors.append(f"{field_id}: invalid status {field.get('status')!r}")

        lineage = field.get("lineage")
        if not isinstance(lineage, list) or not lineage or not all(
            isinstance(item, str) and item.strip() for item in lineage
        ):
            errors.append(f"{field_id}: lineage must be a non-empty string list")

        codes = field.get("bundle_codes")
        if not isinstance(codes, list) or not codes:
            errors.append(f"{field_id}: bundle_codes must be a non-empty list")
        else:
            unknown = set(codes) - bundle_codes
            if unknown:
                errors.append(f"{field_id}: unknown bundle codes {sorted(unknown)}")

        if str(field.get("physical_type", "")).lower() in {"json", "jsonb"}:
            if not field.get("json_schema_ref"):
                errors.append(f"{field_id}: JSON fields require json_schema_ref")
            if field.get("allow_unregistered_personal_keys") is not False:
                errors.append(
                    f"{field_id}: JSON fields must set "
                    "allow_unregistered_personal_keys=false"
                )

    if not raw_fields:
        errors.append("field_registry.json: fields must not be empty")

    for value in _walk_strings(registry):
        for pattern in SECRET_PATTERNS:
            if pattern.search(value):
                errors.append("field_registry.json contains a secret-like literal")
                return errors
    return errors


def validate_migration_gate(
    root: Path, expanded_fields: list[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    baseline_path = root / MIGRATION_BASELINE_PATH.relative_to(ROOT)
    if not baseline_path.exists():
        return ["migration baseline is missing; initialize Phase 0 baseline"]

    baseline = _load_json(baseline_path)
    baseline_entries = baseline.get("migrations")
    if not isinstance(baseline_entries, list):
        return ["migration_baseline.json: migrations must be a list"]

    baseline_map = {
        str(entry["path"]): str(entry["sha256"])
        for entry in baseline_entries
        if isinstance(entry, dict) and "path" in entry and "sha256" in entry
    }
    current_paths = sorted(
        path.relative_to(root).as_posix()
        for path in (root / MIGRATIONS_DIR.relative_to(ROOT)).glob("*.sql")
    )
    current_set = set(current_paths)
    baseline_set = set(baseline_map)

    for missing in sorted(baseline_set - current_set):
        errors.append(f"baseline migration removed: {missing}")
    for path_text in sorted(baseline_set & current_set):
        path = root / path_text
        if _sha256(path) != baseline_map[path_text]:
            errors.append(f"baseline migration modified: {path_text}")

    registry_map = {
        (
            str(field["schema_name"]).lower(),
            str(field["table_name"]).lower(),
            str(field["field_name"]).lower(),
        ): field
        for field in expanded_fields
        if REQUIRED_PHYSICAL <= set(field)
    }

    for path_text in sorted(current_set - baseline_set):
        path = root / path_text
        assets = extract_sql_assets(path.read_text(encoding="utf-8"))
        for logical_table, columns in assets["tables"].items():
            schema, table = logical_table.split(".", 1)
            for column in columns:
                key = (schema, table, column)
                field = registry_map.get(key)
                if field is None:
                    errors.append(
                        f"{path_text}: unregistered migration field "
                        f"{schema}.{table}.{column}"
                    )
                    continue
                if column in FORBIDDEN_RAW_FIELD_NAMES:
                    errors.append(
                        f"{path_text}: forbidden raw secret/payment field name "
                        f"{schema}.{table}.{column}"
                    )
                if str(field.get("physical_type", "")).lower() in {"json", "jsonb"}:
                    if not field.get("json_schema_ref"):
                        errors.append(
                            f"{path_text}: JSON field lacks schema contract "
                            f"{schema}.{table}.{column}"
                        )
                    if field.get("allow_unregistered_personal_keys") is not False:
                        errors.append(
                            f"{path_text}: JSON field allows unregistered personal keys "
                            f"{schema}.{table}.{column}"
                        )
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        bundles = _load_json(root / BUNDLES_PATH.relative_to(ROOT))
        registry = _load_json(root / REGISTRY_PATH.relative_to(ROOT))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load compliance catalog: {exc}"]

    errors.extend(validate_bundles(bundles))
    codes = {
        str(bundle.get("code"))
        for bundle in bundles.get("bundles", [])
        if isinstance(bundle, dict)
    }
    errors.extend(validate_registry_data(registry, codes))
    fields = expand_fields(registry)
    errors.extend(validate_migration_gate(root, fields))
    errors.extend(check_outputs(root))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Compliance catalog gate failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Compliance catalog gate approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
