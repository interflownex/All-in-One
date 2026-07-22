from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable


ALLOWED_COMPONENTS = frozenset(
    {"text", "textarea", "number", "decimal", "date", "datetime", "select", "multiselect", "checkbox", "radio", "file", "currency", "unit", "email", "phone"}
)
ALLOWED_CALCULATIONS = frozenset(
    {"sum", "subtract", "multiply", "divide", "percentage", "average", "minimum", "maximum", "count", "date_difference", "unit_conversion", "round", "conditional", "controlled_text_composition"}
)
FORBIDDEN_KEYS = frozenset(
    {"sql", "query", "javascript", "script", "shell", "physical_table", "physical_column", "table_name", "column_name", "schema_name", "executable"}
)
FORBIDDEN_TEXT = re.compile(r"(?:\b(?:select|insert|update|delete|drop|alter|create|grant|revoke)\b|<script|javascript:|;|--|/\*)", re.I)
MAX_BLOCKS = 50
MAX_FIELDS = 200
MAX_CALCULATIONS = 50
MAX_VALIDATIONS = 500

VERSION_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"editing", "submitted"}),
    "editing": frozenset({"submitted"}),
    "submitted": frozenset({"under_review", "changes_requested", "rejected"}),
    "under_review": frozenset({"approved", "changes_requested", "rejected"}),
    "changes_requested": frozenset({"editing", "submitted"}),
    "approved": frozenset({"published", "rejected"}),
    "published": frozenset({"suspended", "retired"}),
    "suspended": frozenset({"published", "retired"}),
    "rejected": frozenset({"editing"}),
    "retired": frozenset(),
}


class DynamicFormValidationError(ValueError):
    pass


def canonical_checksum(value: Any) -> str:
    material = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def assert_transition(current: str, target: str) -> None:
    if target not in VERSION_TRANSITIONS.get(current, frozenset()):
        raise DynamicFormValidationError(f"Transicao de versao nao permitida: {current} -> {target}.")


def _reject_executable(value: Any, path: str = "blueprint") -> None:
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).casefold().replace("-", "_")
            if key in FORBIDDEN_KEYS:
                raise DynamicFormValidationError(f"Propriedade proibida em {path}: {raw_key}.")
            _reject_executable(child, f"{path}.{raw_key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_executable(child, f"{path}[{index}]")
        return
    if isinstance(value, str) and FORBIDDEN_TEXT.search(value):
        raise DynamicFormValidationError(f"Texto executavel ou SQL proibido em {path}.")


def _unique_ids(rows: list[dict[str, Any]], collection: str) -> set[str]:
    identifiers = [str(row.get("id") or "") for row in rows]
    if any(not identifier for identifier in identifiers):
        raise DynamicFormValidationError(f"Todo item de {collection} precisa de id.")
    if len(identifiers) != len(set(identifiers)):
        raise DynamicFormValidationError(f"IDs duplicados em {collection}.")
    return set(identifiers)


def _assert_acyclic(edges: dict[str, set[str]], nodes: Iterable[str], label: str) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise DynamicFormValidationError(f"Ciclo detectado em {label}: {node}.")
        if node in visited:
            return
        visiting.add(node)
        for dependency in edges.get(node, set()):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in nodes:
        visit(node)


def validate_blueprint(
    blueprint: dict[str, Any],
    *,
    catalog: dict[str, dict[str, Any]],
    bindings: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Valida metadados sem avaliar codigo, acessar tabelas ou confiar no frontend."""
    _reject_executable(blueprint)
    blocks = list(blueprint.get("blocks") or [])
    fields = list(blueprint.get("fields") or [])
    calculations = list(blueprint.get("calculations") or [])
    validations = list(blueprint.get("validations") or [])
    visibility_rules = list(blueprint.get("visibility_rules") or [])
    if not blocks or not fields:
        raise DynamicFormValidationError("Blueprint precisa conter ao menos um bloco e um campo.")
    for rows, limit, label in (
        (blocks, MAX_BLOCKS, "blocos"),
        (fields, MAX_FIELDS, "campos"),
        (calculations, MAX_CALCULATIONS, "calculos"),
        (validations, MAX_VALIDATIONS, "validacoes"),
    ):
        if len(rows) > limit:
            raise DynamicFormValidationError(f"Limite de {label} excedido: maximo {limit}.")

    block_ids = _unique_ids(blocks, "blocks")
    field_ids = _unique_ids(fields, "fields")
    _unique_ids(calculations, "calculations") if calculations else None
    validation_ids = _unique_ids(validations, "validations") if validations else set()
    visibility_ids = _unique_ids(visibility_rules, "visibility_rules") if visibility_rules else set()

    block_edges: dict[str, set[str]] = defaultdict(set)
    for block in blocks:
        block_id = str(block["id"])
        parent = block.get("parent_block_id")
        if parent:
            parent_id = str(parent)
            if parent_id not in block_ids:
                raise DynamicFormValidationError(f"Bloco pai inexistente: {parent_id}.")
            block_edges[block_id].add(parent_id)
        if block.get("block_type") not in {"section", "group", "tab", "column"}:
            raise DynamicFormValidationError(f"Tipo de bloco nao permitido: {block.get('block_type')}.")
        if not 1 <= int(block.get("width", 12)) <= 12:
            raise DynamicFormValidationError("Largura de bloco deve estar entre 1 e 12.")
        visibility = block.get("visibility_rule_id")
        if visibility and str(visibility) not in visibility_ids:
            raise DynamicFormValidationError(f"Regra de visibilidade inexistente: {visibility}.")
    _assert_acyclic(block_edges, block_ids, "hierarquia de blocos")

    validation_types_by_field: dict[str, set[str]] = defaultdict(set)
    for validation in validations:
        field_id = validation.get("field_id")
        if field_id and str(field_id) not in field_ids:
            raise DynamicFormValidationError(f"Validacao aponta para campo inexistente: {field_id}.")
        if field_id:
            validation_types_by_field[str(field_id)].add(str(validation.get("validation_type")))
        if validation.get("severity") in {"error", "blocking"} and not validation.get("run_backend", True):
            raise DynamicFormValidationError("Validacao bloqueante precisa executar no backend.")

    for field in fields:
        field_id = str(field["id"])
        block_id = str(field.get("block_id") or "")
        catalog_id = str(field.get("field_catalog_id") or "")
        binding_id = str(field.get("field_binding_id") or "")
        if block_id not in block_ids:
            raise DynamicFormValidationError(f"Campo {field_id} aponta para bloco inexistente.")
        if catalog_id not in catalog or catalog[catalog_id].get("status") != "active":
            raise DynamicFormValidationError(f"Campo de catalogo nao autorizado: {catalog_id}.")
        if binding_id not in bindings or bindings[binding_id].get("status") != "active":
            raise DynamicFormValidationError(f"Binding logico nao autorizado: {binding_id}.")
        if str(bindings[binding_id].get("field_catalog_id")) != catalog_id:
            raise DynamicFormValidationError("Binding nao pertence ao campo de catalogo informado.")
        component = str(field.get("component") or "")
        allowed = set(catalog[catalog_id].get("allowed_components") or []) & ALLOWED_COMPONENTS
        if component not in allowed:
            raise DynamicFormValidationError(f"Componente {component} nao permitido para {catalog_id}.")
        mandatory = set(catalog[catalog_id].get("mandatory_validations") or [])
        declared = validation_types_by_field[field_id]
        if not mandatory.issubset(declared):
            missing = ", ".join(sorted(mandatory - declared))
            raise DynamicFormValidationError(f"Validacoes estruturais ausentes em {field_id}: {missing}.")
        if not 1 <= int(field.get("width", 12)) <= 12:
            raise DynamicFormValidationError("Largura de campo deve estar entre 1 e 12.")
        visibility = field.get("visibility_rule_id")
        if visibility and str(visibility) not in visibility_ids:
            raise DynamicFormValidationError(f"Regra de visibilidade inexistente: {visibility}.")
        referenced_validations = {str(item) for item in field.get("validation_ids") or []}
        if not referenced_validations.issubset(validation_ids):
            raise DynamicFormValidationError(f"Campo {field_id} referencia validacao inexistente.")

    calculated_by_result: dict[str, str] = {}
    calculation_edges: dict[str, set[str]] = defaultdict(set)
    for calculation in calculations:
        calculation_id = str(calculation["id"])
        result = str(calculation.get("result_field_id") or "")
        operands = {str(item) for item in calculation.get("operand_field_ids") or []}
        if result not in field_ids or not operands or not operands.issubset(field_ids):
            raise DynamicFormValidationError(f"Campos invalidos no calculo {calculation_id}.")
        operation = str(calculation.get("operation") or "")
        if operation not in ALLOWED_CALCULATIONS:
            raise DynamicFormValidationError(f"Calculo nao permitido: {operation}.")
        result_catalog = catalog[str(next(field["field_catalog_id"] for field in fields if str(field["id"]) == result))]
        if operation not in set(result_catalog.get("allowed_calculations") or []):
            raise DynamicFormValidationError(f"Calculo {operation} nao autorizado para o campo de resultado.")
        calculated_by_result[result] = calculation_id
        for operand in operands:
            calculation_edges[calculation_id].add(operand)
    dependency_edges: dict[str, set[str]] = defaultdict(set)
    for calculation_id, operands in calculation_edges.items():
        dependency_edges[calculation_id] = {calculated_by_result[item] for item in operands if item in calculated_by_result}
    _assert_acyclic(dependency_edges, [str(item["id"]) for item in calculations], "dependencias de calculo")

    normalized = {
        "blocks": blocks,
        "fields": fields,
        "calculations": calculations,
        "validations": validations,
        "visibility_rules": visibility_rules,
    }
    return {"blueprint": normalized, "checksum": canonical_checksum(normalized)}


def validate_submission_values(
    *,
    fields: list[dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
    values: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normaliza somente IDs de catálogo publicados; paths e colunas nunca vêm do cliente."""
    allowed = {str(field["field_catalog_id"]): field for field in fields if not field.get("hidden")}
    unknown = set(values) - set(allowed)
    if unknown:
        raise DynamicFormValidationError(f"Campos nao autorizados na submissao: {', '.join(sorted(unknown))}.")
    normalized: list[dict[str, Any]] = []
    for catalog_id, field in allowed.items():
        present = catalog_id in values
        if field.get("required") and (not present or values[catalog_id] in (None, "", [])):
            raise DynamicFormValidationError(f"Campo obrigatorio ausente: {catalog_id}.")
        if not present:
            continue
        if field.get("read_only"):
            raise DynamicFormValidationError(f"Campo somente leitura nao aceita entrada: {catalog_id}.")
        definition = catalog.get(catalog_id)
        if definition is None or definition.get("status") != "active":
            raise DynamicFormValidationError(f"Campo de catalogo indisponivel: {catalog_id}.")
        raw = values[catalog_id]
        data_type = str(definition.get("data_type") or "string")
        try:
            if raw is None:
                value = None
            elif data_type in {"integer", "int"}:
                if isinstance(raw, bool):
                    raise ValueError
                value = int(raw)
            elif data_type in {"decimal", "currency", "number"}:
                if isinstance(raw, float):
                    raise ValueError
                decimal = Decimal(str(raw))
                if not decimal.is_finite():
                    raise ValueError
                value = format(decimal, "f")
            elif data_type in {"boolean", "bool"}:
                if not isinstance(raw, bool):
                    raise ValueError
                value = raw
            elif data_type == "date":
                value = date.fromisoformat(str(raw)).isoformat()
            elif data_type == "datetime":
                value = datetime.fromisoformat(str(raw).replace("Z", "+00:00")).isoformat()
            elif data_type in {"array", "list"}:
                if not isinstance(raw, list):
                    raise ValueError
                value = raw
            elif data_type in {"object", "json"}:
                if not isinstance(raw, dict):
                    raise ValueError
                value = raw
            else:
                if not isinstance(raw, str):
                    raise ValueError
                value = raw.strip()
        except (InvalidOperation, TypeError, ValueError):
            raise DynamicFormValidationError(f"Tipo invalido para {catalog_id}: esperado {data_type}.") from None
        normalized.append(
            {
                "field_catalog_id": catalog_id,
                "data_type": data_type,
                "normalized_value": value,
                "display_value": None if value is None else str(value),
                "unit": definition.get("unit"),
                "sensitivity": definition.get("sensitivity", "internal"),
            }
        )
    return normalized
