import json
from pathlib import Path

from modules.shared.domain_rules import MODULE_ENTITIES

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "apps/all-in-one/src/config/entityFieldBindings.generated.json"
SMART_CRUD_PATH = ROOT / "apps/all-in-one/src/components/SmartCRUD.tsx"
DICTIONARY_PATH = ROOT / "docs/data-audit/artifacts/dicionario_de_dados.json"
MATRIX_PATH = ROOT / "docs/data-audit/artifacts/matriz_formulario_campo.csv"


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_covers_every_persistent_domain_entity():
    manifest = _manifest()
    expected = {
        f"{module}:{entity}"
        for module, entities in MODULE_ENTITIES.items()
        for entity in entities
    }

    assert manifest["contractCount"] == 120
    assert set(manifest["contracts"]) == expected


def test_every_ui_field_has_a_unique_physical_dto_binding():
    manifest = _manifest()
    dictionary = json.loads(DICTIONARY_PATH.read_text(encoding="utf-8"))
    physical_fields = {
        f"{field['schema']}.{field['table']}.{field['physical_name']}"
        for field in dictionary["fields"]
    }

    for key, contract in manifest["contracts"].items():
        names = [field["name"] for field in contract["fields"]]
        assert names, key
        assert len(names) == len(set(names)), key
        assert (
            contract["endpoint"]
            == f"/{contract['module']}/resources/{contract['resource']}"
        )
        for field in contract["fields"]:
            assert field["binding"] == f"ResourceCreate.payload.{field['name']}"
            assert field["patchBinding"] == f"ResourcePatch.payload.{field['name']}"
            assert field["storage"] in physical_fields
            assert field["evidence"].startswith("database/postgres/migrations/")


def test_smart_crud_is_contract_driven_and_sends_only_bound_fields():
    source = SMART_CRUD_PATH.read_text(encoding="utf-8")

    assert "entityFieldBindings.generated.json" in source
    assert "Object.fromEntries(boundFields.map" in source
    assert "data-storage-binding" in source
    assert "status: 'Ativo'" not in source
    assert "image: `/assets/demo/modules/" not in source
    assert "record-name" not in source
    assert "record-description" not in source
    assert "record-category" not in source


def test_generated_matrix_distinguishes_verified_and_legacy_surfaces():
    matrix = MATRIX_PATH.read_text(encoding="utf-8")

    assert "comprovado_por_contrato_versionado" in matrix
    assert "ResourceCreate.payload." in matrix
    assert "lacuna_entidade_sem_contrato" in matrix
    assert "payload genérico/não comprovado" not in matrix
