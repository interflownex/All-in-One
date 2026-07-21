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

    assert len(contract["required_complementary"]) == 16
    assert "artifacts/dicionario_de_dados.csv" in contract["required_complementary"]
    assert "artifacts/catalogo_logico.json" in contract["required_complementary"]
    assert "artifacts/catalogo_eventos.json" in contract["required_complementary"]
    assert "artifacts/catalogo_apis.json" in contract["required_complementary"]
    assert "artifacts/relatorio_divergencias.json" in contract["required_complementary"]


def test_contract_requires_all_completion_dimensions() -> None:
    module = load_validator()
    contract = module.load_json(module.CONTRACT_PATH, [])

    assert len(contract["coverage_dimensions"]) == 15
    assert "campos" in contract["coverage_dimensions"]
    assert "permissoes_backend" in contract["coverage_dimensions"]


def test_generated_coverage_does_not_claim_false_completion() -> None:
    coverage = ROOT / "docs" / "data-audit" / "artifacts" / "checklist_cobertura.json"
    data = __import__("json").loads(coverage.read_text(encoding="utf-8"))

    assert data["status"] == "em_execucao"
    assert data["counts"]["migrations"] == 24
    assert data["counts"]["tables"] >= 80
    assert any(item["percentual"] < 100 for item in data["dimensoes"].values())


def test_generated_summary_is_rendered_markdown() -> None:
    summary = (ROOT / "docs" / "data-audit" / "00_RESUMO_EXECUTIVO.md").read_text(encoding="utf-8")

    assert "24 migrations PostgreSQL" in summary
    assert 'f"A varredura' not in summary
    assert "conclusão de 100% não declarada" in summary


def test_logical_catalog_exposes_cross_layer_gaps() -> None:
    catalog = ROOT / "docs" / "data-audit" / "artifacts" / "catalogo_logico.json"
    data = __import__("json").loads(catalog.read_text(encoding="utf-8"))

    assert data["counts"]["logical_entities"] == 120
    assert data["counts"]["logical_without_physical_table"] > 0
    assert data["counts"]["logical_without_ui_surface"] > 0
    assert all(item["evidence"] for item in data["entities"])


def test_event_catalog_preserves_backend_transition_contract() -> None:
    catalog = ROOT / "docs" / "data-audit" / "artifacts" / "catalogo_eventos.json"
    data = __import__("json").loads(catalog.read_text(encoding="utf-8"))

    assert data["counts"]["event_transitions"] == 194
    assert data["counts"]["unique_events"] == 187
    assert all(item["event"] and item["producer"] for item in data["events"])
    assert any(item["requires_mfa"] for item in data["events"])


def test_api_catalog_exposes_models_and_untyped_payloads() -> None:
    catalog = ROOT / "docs" / "data-audit" / "artifacts" / "catalogo_apis.json"
    data = __import__("json").loads(catalog.read_text(encoding="utf-8"))

    assert data["counts"]["endpoints"] == 99
    assert data["counts"]["api_model_fields"] > 0
    assert all(item["method"] and item["path"] and item["evidence"] for item in data["endpoints"])
    assert any(not item["response_model"] for item in data["endpoints"])
