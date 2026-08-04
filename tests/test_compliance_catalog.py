from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_validator():
    path = ROOT / "scripts/validate_compliance_catalog.py"
    spec = importlib.util.spec_from_file_location("compliance_validator", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bundles_are_exactly_b0_to_b14() -> None:
    data = json.loads(
        (ROOT / "config/compliance/bundles.v1.json").read_text(encoding="utf-8")
    )
    assert {item["id"] for item in data["bundles"]} == {f"B{i}" for i in range(15)}


def test_registry_has_frozen_baseline_and_valid_contract() -> None:
    validator = _load_validator()
    bundles = validator.validate_bundles(validator.load_json(validator.BUNDLES))
    registry = validator.load_json(validator.REGISTRY)

    assert registry["baseline_sha"] == "ab2ebca1849d2e3ed31ca8922ab74a0215e04939"
    registered = validator.validate_registry(registry, bundles)

    assert len(registered) == 33
    assert ("compliance.catalog_versions", "baseline_sha") in registered
    assert ("compliance.field_registry", "legal_basis") in registered
    assert ("compliance.field_registry", "bundle_ids") in registered


def test_sql_parser_handles_nested_parentheses_and_constraints() -> None:
    validator = _load_validator()
    sql = """
    CREATE TABLE compliance.sample (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      amount NUMERIC(18, 2) NOT NULL,
      status TEXT CHECK (status IN ('active', 'blocked')),
      tenant_id UUID NOT NULL,
      CONSTRAINT sample_unique UNIQUE (tenant_id, status)
    );
    ALTER TABLE compliance.sample ADD COLUMN purpose TEXT;
    """
    assert validator.parse_columns(sql) == {
        ("compliance.sample", "id"),
        ("compliance.sample", "amount"),
        ("compliance.sample", "status"),
        ("compliance.sample", "tenant_id"),
        ("compliance.sample", "purpose"),
    }


def test_sql_parser_rejects_unbalanced_create_table() -> None:
    validator = _load_validator()
    with pytest.raises(ValueError, match="não balanceados"):
        validator.parse_columns(
            "CREATE TABLE compliance.invalid (id UUID DEFAULT gen_random_uuid();"
        )


def test_sensitive_literal_pattern_rejects_secrets() -> None:
    validator = _load_validator()
    assert validator.FORBIDDEN_LITERAL.search('client_secret = "valor-real"')
    assert not validator.FORBIDDEN_LITERAL.search(
        'client_secret_env = os.environ["CLIENT_SECRET"]'
    )
