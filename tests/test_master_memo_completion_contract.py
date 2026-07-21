from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "data-audit"
ARTIFACTS = AUDIT / "artifacts"


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_todos_relacionamentos_descritos_no_dicionario_e_erd() -> None:
    dictionary = load_json("docs/data-audit/artifacts/dicionario_de_dados.json")
    relationships = [field for field in dictionary["fields"] if field["reference"]]
    erd = (ARTIFACTS / "erd.mmd").read_text(encoding="utf-8")

    assert len(relationships) == dictionary["counts"]["relationships"] == 348
    assert erd.count("}o--||") == len(relationships)
    assert all(field["evidence"] and field["reference"].count(".") == 2 for field in relationships)
    for field in relationships:
        source = f'{field["schema"]}_{field["table"]}'.replace(".", "_")
        target = field["reference"].rsplit(".", 1)[0].replace(".", "_")
        assert f'{source} }}o--|| {target} : "{field["physical_name"]}"' in erd


def test_mapear_ecossistema_e_fontes_de_verdade() -> None:
    coordinate = load_json("config/stitch/template_project_coordinate.json")
    contract = load_json("config/data_audit/delivery_contract.json")

    assert coordinate["authoritative_sources"]
    assert len(coordinate["projects"]) == 3
    assert {project["id"] for project in coordinate["projects"]} == {
        "valley_apk_template",
        "all_in_one_web_mobile_template",
        "valley_riders_apk_template",
    }
    assert contract["required_database_paths"]
    assert set(contract["coverage_dimensions"]) >= {"bancos", "formularios", "permissoes_backend"}


def test_planejar_ordem_de_leitura_matriz_de_comparacao_prioridades_entregaveis_criterios_de_aceite() -> None:
    contract = load_json("config/data_audit/delivery_contract.json")
    gaps = load_json("docs/data-audit/artifacts/relatorio_divergencias.json")["gaps"]

    assert contract["required_markdown"][0] == "00_RESUMO_EXECUTIVO.md"
    assert contract["required_markdown"][-1] == "19_CRITERIOS_DE_ACEITE.md"
    assert "artifacts/matriz_formulario_campo.csv" in contract["required_complementary"]
    assert {gap["priority"] for gap in gaps} >= {"P0", "P1"}
    assert all(gap["acceptance"] and gap["status"] for gap in gaps)


def test_catalogar_impostos_e_logs() -> None:
    fiscal = load_json("docs/data-audit/artifacts/modelo_unidades_tributacao.json")
    audit = load_json("docs/data-audit/artifacts/cobertura_auditoria.json")

    assert "fiscal_rules" in fiscal["fiscal_entities"]
    assert "tax_calculation_snapshots" in fiscal["fiscal_entities"]
    assert fiscal["fiscal_entities"]["fiscal_rules"]
    assert audit["counts"]["audit_candidate_tables"] >= 1
    assert any(item["covered"] and item["evidence"] for item in audit["coverage"])


def test_validar_integridade_e_regras() -> None:
    coverage = load_json("docs/data-audit/artifacts/checklist_cobertura.json")
    logical = load_json("docs/data-audit/artifacts/catalogo_logico.json")
    permissions = load_json("docs/data-audit/artifacts/matriz_enforcement_permissao.json")

    assert coverage["status"] != "concluido"
    assert logical["entities"]
    assert all(item["evidence"] for item in logical["entities"])
    assert permissions["counts"]["permission_operations"] == len(permissions["operations"])


def test_documentar_csv_json_erd_e_matrizes() -> None:
    contract = load_json("config/data_audit/delivery_contract.json")
    required = [AUDIT / relative for relative in contract["required_complementary"]]

    assert all(path.is_file() and path.stat().st_size > 0 for path in required)
    assert any(path.suffix == ".csv" for path in required)
    assert any(path.suffix == ".json" for path in required)
    assert ARTIFACTS.joinpath("erd.mmd") in required
    assert len([path for path in required if "matriz" in path.name]) >= 8


def test_orientar_stitch_coordenada_por_tela_validacoes_acoes() -> None:
    coordinates = load_json("docs/data-audit/artifacts/coordenadas_stitch.json")["coordinates"]

    assert coordinates
    assert all(item["route"] and item["fields"] and item["actions"] for item in coordinates)
    assert all(item["states"] and item["binding_status"] and item["evidence"] for item in coordinates)
    assert all(all(action["contract_status"] for action in item["actions"]) for item in coordinates)


def test_orientar_stitch_acessibilidade_integracao_e_criterios_de_aceite() -> None:
    coordinates = load_json("docs/data-audit/artifacts/coordenadas_stitch.json")["coordinates"]
    directive = load_json("config/stitch/template_project_coordinate.json")

    assert all({"desktop", "tablet", "mobile"} <= set(item["responsive"]) for item in coordinates)
    assert all({"label", "teclado", "contraste"} <= set(item["accessibility"]) for item in coordinates)
    assert all(item["endpoint"] and item["permissions"] for item in coordinates)
    text = " ".join(directive["universal_directives"]).casefold()
    assert "wcag aa" in text and "endpoint/contrato" in text and "teste" in text
