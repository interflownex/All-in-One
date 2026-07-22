from copy import deepcopy

import pytest

from modules.shared.dynamic_forms import (
    DynamicFormValidationError,
    assert_transition,
    validate_blueprint,
    validate_submission_values,
)

CATALOG = {
    "catalog-name": {
        "status": "active",
        "allowed_components": ["text", "textarea"],
        "mandatory_validations": ["required", "max_length"],
        "allowed_calculations": [],
    },
    "catalog-total": {
        "status": "active",
        "allowed_components": ["decimal"],
        "mandatory_validations": [],
        "allowed_calculations": ["sum"],
    },
}
BINDINGS = {
    "binding-name": {"status": "active", "field_catalog_id": "catalog-name"},
    "binding-total": {"status": "active", "field_catalog_id": "catalog-total"},
}


def blueprint() -> dict:
    return {
        "blocks": [
            {
                "id": "block-main",
                "block_type": "section",
                "title": "Principal",
                "width": 12,
            },
        ],
        "fields": [
            {
                "id": "field-name",
                "block_id": "block-main",
                "field_catalog_id": "catalog-name",
                "field_binding_id": "binding-name",
                "component": "text",
                "label": "Nome",
                "width": 12,
                "validation_ids": ["validation-required", "validation-length"],
            },
            {
                "id": "field-total",
                "block_id": "block-main",
                "field_catalog_id": "catalog-total",
                "field_binding_id": "binding-total",
                "component": "decimal",
                "label": "Total",
                "width": 6,
                "validation_ids": [],
            },
        ],
        "validations": [
            {
                "id": "validation-required",
                "field_id": "field-name",
                "validation_type": "required",
                "severity": "blocking",
                "run_backend": True,
            },
            {
                "id": "validation-length",
                "field_id": "field-name",
                "validation_type": "max_length",
                "severity": "error",
                "run_backend": True,
            },
        ],
        "calculations": [
            {
                "id": "calculation-total",
                "result_field_id": "field-total",
                "operand_field_ids": ["field-name"],
                "operation": "sum",
                "safe_expression": {"operation": "sum"},
            },
        ],
        "visibility_rules": [],
    }


def test_blueprint_valido_produz_checksum_estavel() -> None:
    first = validate_blueprint(blueprint(), catalog=CATALOG, bindings=BINDINGS)
    second = validate_blueprint(
        deepcopy(blueprint()), catalog=CATALOG, bindings=BINDINGS
    )
    assert first["checksum"] == second["checksum"]
    assert len(first["checksum"]) == 64


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("sql", "SELECT * FROM users"),
        ("javascript", "alert(1)"),
        ("physical_table", "identity.users"),
    ],
)
def test_blueprint_rejeita_codigo_e_destino_fisico(key: str, value: str) -> None:
    candidate = blueprint()
    candidate["fields"][0][key] = value
    with pytest.raises(DynamicFormValidationError, match="proibida"):
        validate_blueprint(candidate, catalog=CATALOG, bindings=BINDINGS)


def test_blueprint_rejeita_enfraquecimento_de_validacao_obrigatoria() -> None:
    candidate = blueprint()
    candidate["validations"] = candidate["validations"][:1]
    candidate["fields"][0]["validation_ids"] = ["validation-required"]
    with pytest.raises(
        DynamicFormValidationError, match="Validacoes estruturais ausentes"
    ):
        validate_blueprint(candidate, catalog=CATALOG, bindings=BINDINGS)


def test_blueprint_rejeita_binding_de_outro_campo() -> None:
    candidate = blueprint()
    candidate["fields"][0]["field_binding_id"] = "binding-total"
    with pytest.raises(DynamicFormValidationError, match="Binding nao pertence"):
        validate_blueprint(candidate, catalog=CATALOG, bindings=BINDINGS)


def test_blueprint_rejeita_ciclo_de_blocos() -> None:
    candidate = blueprint()
    candidate["blocks"] = [
        {"id": "a", "block_type": "section", "parent_block_id": "b"},
        {"id": "b", "block_type": "group", "parent_block_id": "a"},
    ]
    candidate["fields"][0]["block_id"] = "a"
    candidate["fields"][1]["block_id"] = "a"
    with pytest.raises(DynamicFormValidationError, match="Ciclo detectado"):
        validate_blueprint(candidate, catalog=CATALOG, bindings=BINDINGS)


def test_blueprint_rejeita_componente_fora_da_allowlist() -> None:
    candidate = blueprint()
    candidate["fields"][0]["component"] = "file"
    with pytest.raises(DynamicFormValidationError, match="nao permitido"):
        validate_blueprint(candidate, catalog=CATALOG, bindings=BINDINGS)


def test_transicoes_impedem_publicacao_sem_aprovacao() -> None:
    assert_transition("approved", "published")
    with pytest.raises(DynamicFormValidationError, match="nao permitida"):
        assert_transition("draft", "published")
    with pytest.raises(DynamicFormValidationError, match="nao permitida"):
        assert_transition("published", "editing")


def test_submissao_normaliza_por_catalogo_sem_destino_fisico() -> None:
    fields = [
        {
            "field_catalog_id": "catalog-name",
            "required": True,
            "read_only": False,
            "hidden": False,
        },
        {
            "field_catalog_id": "catalog-total",
            "required": True,
            "read_only": False,
            "hidden": False,
        },
    ]
    catalog = {
        **CATALOG,
        "catalog-name": {
            **CATALOG["catalog-name"],
            "data_type": "string",
            "sensitivity": "personal",
        },
        "catalog-total": {
            **CATALOG["catalog-total"],
            "data_type": "decimal",
            "unit": "BRL",
        },
    }
    result = validate_submission_values(
        fields=fields,
        catalog=catalog,
        values={"catalog-name": " Pessoa ", "catalog-total": "10.50"},
    )
    assert result[0]["normalized_value"] == "Pessoa"
    assert result[1]["normalized_value"] == "10.50"
    assert result[1]["unit"] == "BRL"


def test_submissao_rejeita_campo_nao_publicado_e_float_financeiro() -> None:
    fields = [
        {
            "field_catalog_id": "catalog-total",
            "required": True,
            "read_only": False,
            "hidden": False,
        }
    ]
    catalog = {"catalog-total": {**CATALOG["catalog-total"], "data_type": "decimal"}}
    with pytest.raises(DynamicFormValidationError, match="nao autorizados"):
        validate_submission_values(
            fields=fields, catalog=catalog, values={"outro-campo": "x"}
        )
    with pytest.raises(DynamicFormValidationError, match="Tipo invalido"):
        validate_submission_values(
            fields=fields, catalog=catalog, values={"catalog-total": 10.5}
        )
