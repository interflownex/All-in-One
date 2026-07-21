from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_data_audit_delivery.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_data_audit_delivery", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_lists_every_mandatory_markdown_document() -> None:
    module = load_validator()
    contract = module.load_json(module.CONTRACT_PATH, [])

    assert len(contract["required_markdown"]) == 20
    assert contract["required_markdown"][0] == "00_RESUMO_EXECUTIVO.md"
    assert contract["required_markdown"][-1] == "19_CRITERIOS_DE_ACEITE.md"


def test_contract_lists_every_complementary_format() -> None:
    module = load_validator()
    contract = module.load_json(module.CONTRACT_PATH, [])

    assert len(contract["required_complementary"]) == 10
    assert "artifacts/dicionario_de_dados.csv" in contract["required_complementary"]
    assert "artifacts/relatorio_divergencias.json" in contract["required_complementary"]


def test_contract_requires_all_completion_dimensions() -> None:
    module = load_validator()
    contract = module.load_json(module.CONTRACT_PATH, [])

    assert len(contract["coverage_dimensions"]) == 15
    assert "campos" in contract["coverage_dimensions"]
    assert "permissoes_backend" in contract["coverage_dimensions"]
