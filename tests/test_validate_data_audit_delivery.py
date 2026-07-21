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

    assert len(contract["required_complementary"]) == 44
    assert "artifacts/dicionario_de_dados.csv" in contract["required_complementary"]
    assert "artifacts/catalogo_logico.json" in contract["required_complementary"]
    assert "artifacts/catalogo_eventos.json" in contract["required_complementary"]
    assert "artifacts/catalogo_apis.json" in contract["required_complementary"]
    assert "artifacts/formulario_dinamico_modelo.json" in contract["required_complementary"]
    assert "artifacts/coordenadas_stitch.json" in contract["required_complementary"]
    assert "artifacts/modelo_unidades_tributacao.json" in contract["required_complementary"]
    assert "artifacts/politica_classificacao_campos.json" in contract["required_complementary"]
    assert "artifacts/cobertura_auditoria.json" in contract["required_complementary"]
    assert "artifacts/relatorio_divergencias.json" in contract["required_complementary"]
    assert "artifacts/catalogo_mongodb.json" in contract["required_complementary"]
    assert "artifacts/catalogo_mongodb.csv" in contract["required_complementary"]
    assert "artifacts/catalogo_sqlite.json" in contract["required_complementary"]
    assert "artifacts/catalogo_sqlite.csv" in contract["required_complementary"]
    assert "artifacts/catalogo_redis.json" in contract["required_complementary"]
    assert "artifacts/catalogo_object_storage.json" in contract["required_complementary"]
    assert "artifacts/catalogo_browser_storage.json" in contract["required_complementary"]
    assert "artifacts/coordenada_projetos_stitch.json" in contract["required_complementary"]
    assert "artifacts/matriz_acao_ui_backend.json" in contract["required_complementary"]
    assert "artifacts/matriz_acao_ui_backend.csv" in contract["required_complementary"]
    assert "artifacts/matriz_enforcement_permissao.json" in contract["required_complementary"]
    assert "artifacts/matriz_enforcement_permissao.csv" in contract["required_complementary"]
    assert "artifacts/catalogo_testes.json" in contract["required_complementary"]
    assert "artifacts/catalogo_testes.csv" in contract["required_complementary"]
    assert "artifacts/matriz_requisito_teste.json" in contract["required_complementary"]
    assert "artifacts/matriz_requisito_teste.csv" in contract["required_complementary"]
    assert "artifacts/pytest_unit_results.xml" in contract["required_complementary"]
    assert "artifacts/pytest_identity_e2e_results.xml" in contract["required_complementary"]


def test_generated_non_postgres_catalogs_have_field_evidence() -> None:
    json = __import__("json")
    artifacts = ROOT / "docs" / "data-audit" / "artifacts"
    mongodb = json.loads((artifacts / "catalogo_mongodb.json").read_text(encoding="utf-8"))
    sqlite = json.loads((artifacts / "catalogo_sqlite.json").read_text(encoding="utf-8"))

    assert mongodb["counts"]["mongodb_collections"] == 4
    assert mongodb["counts"]["mongodb_fields"] == 29
    assert all(item["evidence"] for item in mongodb["fields"])
    assert sqlite["counts"]["sqlite_tables"] == 4
    assert sqlite["counts"]["sqlite_fields"] == 39
    assert all(item["evidence"] for item in sqlite["fields"])


def test_ephemeral_and_object_storage_catalogs_are_explicitly_static() -> None:
    json = __import__("json")
    artifacts = ROOT / "docs" / "data-audit" / "artifacts"
    expected = {
        "catalogo_redis.json": ("redis_key_patterns", 1),
        "catalogo_object_storage.json": ("object_storage_stores", 4),
        "catalogo_browser_storage.json": ("browser_storage_key_patterns", 12),
    }
    for name, (counter, total) in expected.items():
        data = json.loads((artifacts / name).read_text(encoding="utf-8"))
        assert data["status"] == "inventario_estatico"
        assert data["counts"][counter] == total == len(data["entries"])
        assert all(item["evidence"] and item["runtime_verified"] is False for item in data["entries"])


def test_stitch_coordinate_requires_exactly_three_resumable_product_projects() -> None:
    coordinate = ROOT / "config" / "stitch" / "template_project_coordinate.json"
    data = __import__("json").loads(coordinate.read_text(encoding="utf-8"))

    assert [project["id"] for project in data["projects"]] == [
        "valley_apk_template",
        "all_in_one_web_mobile_template",
        "valley_riders_apk_template",
    ]
    assert sum(len(project["screen_groups"]) for project in data["projects"]) == 24
    assert all(len(project["screen_groups"]) == 8 for project in data["projects"])
    assert data["continuation_policy"]["checkpoint_after_each_remote_operation"]
    assert data["continuation_policy"]["on_resource_exhausted"] == "registrar_checkpoint_e_retomar_na_proxima_execucao_agendada"
    assert "prohibited_claim" in data["continuation_policy"]
    assert all(project["module_scope"] and project["surfaces"] for project in data["projects"])


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


def test_dynamic_form_model_is_explicitly_a_non_implemented_proposal() -> None:
    model = ROOT / "docs" / "data-audit" / "artifacts" / "formulario_dinamico_modelo.json"
    data = __import__("json").loads(model.read_text(encoding="utf-8"))

    assert data["status"] == "proposta"
    assert len(data["entities"]) == 14
    assert "field_bindings" in data["entities"]
    assert "physical_table_selection" in data["forbidden"]
    assert not any(data["implementation_gate"].values())


def test_every_smartcrud_surface_has_a_stitch_coordinate_and_route() -> None:
    coordinates = ROOT / "docs" / "data-audit" / "artifacts" / "coordenadas_stitch.json"
    data = __import__("json").loads(coordinates.read_text(encoding="utf-8"))

    assert len(data["coordinates"]) == data["counts"]["ui_surfaces"] == 299
    assert all(item["route"].startswith("/") for item in data["coordinates"])
    assert all(item["states"] and item["accessibility"] for item in data["coordinates"])
    assert all(item["actions"] for item in data["coordinates"])
    assert all(item["binding_status"] == "parcial" for item in data["coordinates"])


def test_ui_action_matrix_exposes_the_generic_save_contract_mismatch() -> None:
    matrix = ROOT / "docs" / "data-audit" / "artifacts" / "matriz_acao_ui_backend.json"
    data = __import__("json").loads(matrix.read_text(encoding="utf-8"))
    actions = data["actions"]

    assert data["counts"]["ui_actions"] == len(actions) == 1111
    assert data["counts"]["ui_actions_incompatible"] == 129
    assert data["counts"]["ui_actions_without_frontend_permission_gate"] == 979
    incompatible = [item for item in actions if item["contract_status"] == "incompativel"]
    assert len(incompatible) == data["counts"]["ui_forms"]
    assert all(item["action"] == "Salvar Registro" for item in incompatible)
    assert all("PUT" in item["method"] and "PATCH" in item["backend_contract"] for item in incompatible)
    assert any(item["action"] == "Enviar candidatura" for item in actions)


def test_permission_matrix_exposes_horizontal_read_authorization_gaps() -> None:
    matrix = ROOT / "docs" / "data-audit" / "artifacts" / "matriz_enforcement_permissao.json"
    data = __import__("json").loads(matrix.read_text(encoding="utf-8"))
    operations = data["operations"]

    assert data["counts"]["permission_operations"] == len(operations) == 794
    assert data["counts"]["permission_horizontal_read_gaps"] == 56
    assert data["counts"]["permission_operations_with_test_candidates"] > 0
    gaps = [item for item in operations if item["enforcement_status"] == "lacuna_autorizacao_horizontal"]
    assert len(gaps) == 56
    assert all(item["operation"] == "read" and item["method"] == "GET" for item in gaps)
    assert all(not item["sensitive_resource"] and item["module"] != "permissions" for item in gaps)
    assert any(item["operation"] == "approve" and item["role_enforcement"] for item in operations)


def test_requirement_test_matrix_does_not_promote_candidates_to_proof() -> None:
    artifacts = ROOT / "docs" / "data-audit" / "artifacts"
    catalog = __import__("json").loads((artifacts / "catalogo_testes.json").read_text(encoding="utf-8"))
    matrix = __import__("json").loads((artifacts / "matriz_requisito_teste.json").read_text(encoding="utf-8"))
    test_ids = {item["test_id"] for item in catalog["tests"]}

    assert catalog["counts"]["test_functions"] == len(catalog["tests"])
    assert catalog["counts"]["test_functions_in_execution_reports"] > 0
    assert catalog["counts"]["test_functions_passed"] > 0
    assert catalog["counts"]["test_functions"] >= 360
    assert catalog["counts"]["tests_with_assertions"] < catalog["counts"]["test_functions"]
    assert catalog["counts"]["tests_with_http_calls"] > 0
    assert matrix["counts"]["memo_requirements_traced"] == len(matrix["requirements"]) == 69
    assert matrix["counts"]["memo_requirements_without_test_candidates"] == 0
    assert all(item["test_candidates"] for item in matrix["requirements"])
    assert all(candidate in test_ids for item in matrix["requirements"] for candidate in item["test_candidates"])
    assert all(item["proof_status"].startswith("não comprovado") for item in matrix["requirements"])
    assert any(item["passed_test_candidates"] for item in matrix["requirements"])


def test_units_and_tax_model_covers_precision_and_fiscal_governance() -> None:
    model = ROOT / "docs" / "data-audit" / "artifacts" / "modelo_unidades_tributacao.json"
    data = __import__("json").loads(model.read_text(encoding="utf-8"))

    assert data["status"] == "proposta"
    assert "product_unit_conversions" in data["measurement_entities"]
    assert "stock_movements" in data["measurement_entities"]
    assert "fiscal_rules" in data["fiscal_entities"]
    assert "tax_calculation_snapshots" in data["fiscal_entities"]
    assert data["conversion_rules"]["binary_float_forbidden"]
    assert data["calculation_contract"]["tax_calculation_backend_only"]
    assert not any(data["implementation_gate"].values())


def test_every_physical_field_has_classification_basis_and_retention() -> None:
    catalog = ROOT / "docs" / "data-audit" / "artifacts" / "dicionario_de_dados.json"
    data = __import__("json").loads(catalog.read_text(encoding="utf-8"))

    assert all(item["classification_basis"] for item in data["fields"])
    assert all(item["encryption"] for item in data["fields"])
    assert all(item["masking"] for item in data["fields"])
    assert all(item["retention"] for item in data["fields"])
    assert any(item["lgpd"] == "dado pessoal sensível" for item in data["fields"])


def test_audit_coverage_reports_present_and_missing_requirements() -> None:
    report = ROOT / "docs" / "data-audit" / "artifacts" / "cobertura_auditoria.json"
    data = __import__("json").loads(report.read_text(encoding="utf-8"))

    assert data["counts"]["audit_candidate_tables"] > 0
    assert data["counts"]["audit_requirements"] == len(data["coverage"])
    assert any(item["covered"] for item in data["coverage"])
    assert any(not item["covered"] for item in data["coverage"])
    assert all(item["aliases"] for item in data["coverage"])


def test_every_gap_has_the_mandatory_execution_coordinate() -> None:
    report = ROOT / "docs" / "data-audit" / "artifacts" / "relatorio_divergencias.json"
    data = __import__("json").loads(report.read_text(encoding="utf-8"))

    required = set(data["required_fields"])
    assert data["version"] == 2
    assert data["counts"]["total"] == len(data["gaps"])
    assert required
    assert all(required <= set(gap) for gap in data["gaps"])
    assert all(gap["evidence"] and gap["affected_files"] and gap["dimensions"] for gap in data["gaps"])


def test_coverage_links_only_dimension_specific_gaps_and_evidence() -> None:
    artifacts = ROOT / "docs" / "data-audit" / "artifacts"
    coverage = __import__("json").loads((artifacts / "checklist_cobertura.json").read_text(encoding="utf-8"))
    report = __import__("json").loads((artifacts / "relatorio_divergencias.json").read_text(encoding="utf-8"))
    gaps_by_id = {gap["id"]: gap for gap in report["gaps"]}

    for dimension, item in coverage["dimensoes"].items():
        assert item["evidencias"]
        assert item["metodo"]
        assert all(dimension in gaps_by_id[gap_id]["dimensions"] for gap_id in item["lacunas"])
    assert coverage["dimensoes"]["bindings_frontend"]["lacunas"] == ["AUD-P1-002", "AUD-P1-008"]
    assert coverage["dimensoes"]["campos_sensiveis"]["lacunas"] == ["AUD-P0-001", "AUD-P1-007"]
    assert "AUD-P1-007" in coverage["dimensoes"]["auditoria"]["lacunas"]
    assert not any(item["percentual"] == 100 and item["lacunas"] for item in coverage["dimensoes"].values())
