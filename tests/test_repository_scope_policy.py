from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_repository_scope.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_repository_scope", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repository_scope_contract() -> None:
    validator = _load_validator()
    assert validator.validate() == []


def test_policy_declares_single_official_repository() -> None:
    validator = _load_validator()
    policy = validator._load_json(validator.POLICY_PATH)
    assert policy["official_repository"] == "interflownex/All-in-One"
    assert policy["default_branch"] == "main"
    assert policy["product_scope"]["valley"].startswith("produto")
    assert policy["forbidden_repository_sources"]
