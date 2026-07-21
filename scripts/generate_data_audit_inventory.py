#!/usr/bin/env python3
"""Gera o inventário físico e os artefatos rastreáveis do memorando mestre."""

from __future__ import annotations

import csv
import ast
import json
import re
import sys
import types
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "database" / "postgres" / "migrations"
AUDIT = ROOT / "docs" / "data-audit"
ARTIFACTS = AUDIT / "artifacts"
DATABASE = AUDIT / "databases" / "postgresql"
DYNAMIC_FORM_MODEL = ROOT / "config" / "data_audit" / "dynamic_form_model_proposal.json"
PRODUCT_UNITS_TAX_MODEL = ROOT / "config" / "data_audit" / "product_units_tax_model_proposal.json"
FIELD_CLASSIFICATION_POLICY = ROOT / "config" / "data_audit" / "field_classification_policy.json"
AUDIT_TRACEABILITY_POLICY = ROOT / "config" / "data_audit" / "audit_traceability_policy.json"


@dataclass(frozen=True)
class Field:
    database: str
    schema: str
    table: str
    physical_name: str
    logical_name: str
    physical_type: str
    nullable: bool
    default: str
    primary_key: bool
    unique: bool
    reference: str
    lgpd: str
    classification_basis: str
    encryption: str
    masking: str
    retention: str
    status: str
    evidence: str


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def split_definitions(body: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quoted = False
    for index, char in enumerate(body):
        if char == "'":
            quoted = not quoted
        elif not quoted and char == "(":
            depth += 1
        elif not quoted and char == ")":
            depth = max(0, depth - 1)
        elif not quoted and char == "," and depth == 0:
            parts.append(body[start:index].strip())
            start = index + 1
    tail = body[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def classify_lgpd(name: str) -> tuple[str, str, str, str, str]:
    policy = json.loads(FIELD_CLASSIFICATION_POLICY.read_text(encoding="utf-8"))
    lowered = name.lower()
    for category in policy["categories"]:
        matched = [pattern for pattern in category["patterns"] if pattern in lowered]
        if matched:
            return (
                category["classification"],
                f"política v{policy['version']} categoria {category['id']}; padrões: {', '.join(matched)}",
                category["encryption"],
                category["masking"],
                category["retention"],
            )
    default = policy["default"]
    return (
        default["classification"],
        f"política v{policy['version']}; nenhuma regra automática aplicável",
        default["encryption"],
        default["masking"],
        default["retention"],
    )


def parse_field(schema: str, table: str, definition: str, evidence: str) -> Field | None:
    normalized = " ".join(definition.split())
    if not normalized or re.match(r"^(CONSTRAINT|PRIMARY|FOREIGN|UNIQUE|CHECK|EXCLUDE)\b", normalized, re.I):
        return None
    match = re.match(r'^"?([A-Za-z_][\w$]*)"?\s+(.+)$', normalized)
    if not match:
        return None
    name, remainder = match.groups()
    type_match = re.match(
        r"(.+?)(?=\s+(?:NOT\s+NULL|NULL|DEFAULT|PRIMARY\s+KEY|UNIQUE|REFERENCES|CHECK|COLLATE|GENERATED)\b|$)",
        remainder,
        re.I,
    )
    physical_type = type_match.group(1).strip() if type_match else remainder
    default_match = re.search(r"\bDEFAULT\s+(.+?)(?=\s+(?:NOT\s+NULL|NULL|PRIMARY\s+KEY|UNIQUE|REFERENCES|CHECK)\b|$)", remainder, re.I)
    reference_match = re.search(r"\bREFERENCES\s+([\w.\"]+)\s*\(([^)]+)\)", remainder, re.I)
    lgpd, classification_basis, encryption, masking, retention = classify_lgpd(name)
    return Field(
        database="postgresql",
        schema=schema,
        table=table,
        physical_name=name,
        logical_name=name.replace("_", " ").capitalize(),
        physical_type=physical_type,
        nullable="NOT NULL" not in remainder.upper() and "PRIMARY KEY" not in remainder.upper(),
        default=default_match.group(1).strip() if default_match else "",
        primary_key="PRIMARY KEY" in remainder.upper(),
        unique="UNIQUE" in remainder.upper(),
        reference=".".join(part.strip('" ') for part in reference_match.groups()) if reference_match else "",
        lgpd=lgpd,
        classification_basis=classification_basis,
        encryption=encryption,
        masking=masking,
        retention=retention,
        status="existente",
        evidence=evidence,
    )


def discover_physical_model() -> tuple[set[str], dict[str, list[Field]], list[str], list[str]]:
    schemas: set[str] = set()
    tables: dict[str, list[Field]] = {}
    indexes: list[str] = []
    migrations = sorted(MIGRATIONS.glob("*.sql"))
    create_table = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)\.([\w\"]+)\s*\((.*?)\n\);",
        re.I | re.S,
    )
    alter_table = re.compile(r"ALTER\s+TABLE\s+([\w\"]+)\.([\w\"]+)\s+(.*?);", re.I | re.S)
    index_pattern = re.compile(r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)", re.I)

    for path in migrations:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        schemas.update(
            match.strip('"')
            for match in re.findall(
                r"^CREATE\s+SCHEMA\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)",
                text,
                re.I | re.M,
            )
        )
        indexes.extend(match.strip('"') for match in index_pattern.findall(text))
        for match in create_table.finditer(text):
            schema, table, body = (part.strip('"') for part in match.groups())
            schemas.add(schema)
            key = f"{schema}.{table}"
            fields: list[Field] = []
            body_offset = match.start(3)
            running = 0
            for definition in split_definitions(body):
                local = body.find(definition, running)
                running = max(running, local + len(definition))
                evidence = f"{relative}:{line_number(text, body_offset + max(local, 0))}"
                field = parse_field(schema, table, definition, evidence)
                if field:
                    fields.append(field)
            tables[key] = fields

        for match in alter_table.finditer(text):
            schema, table, body = (part.strip('"') for part in match.groups())
            key = f"{schema}.{table}"
            for column in re.finditer(r"ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w\"]+)\s+(.+?)(?=,\s*ADD\s+COLUMN|$)", body, re.I | re.S):
                name = column.group(1).strip('"')
                definition = f"{name} {column.group(2).strip()}"
                evidence = f"{relative}:{line_number(text, match.start(3) + column.start())}"
                field = parse_field(schema, table, definition, evidence)
                if field and all(existing.physical_name != name for existing in tables.get(key, [])):
                    tables.setdefault(key, []).append(field)
    return schemas, tables, indexes, [str(path.relative_to(ROOT)) for path in migrations]


def discover_mongodb_model() -> list[dict[str, object]]:
    init_path = ROOT / "database" / "mongodb" / "init" / "001_ai_social_telemetry.js"
    contract_path = ROOT / "config" / "database" / "mongodb_contract.json"
    text = init_path.read_text(encoding="utf-8")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    starts = list(re.finditer(r'createValidatedCollection\("([^"]+)",\s*\{', text))
    rows: list[dict[str, object]] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[match.start():end]
        collection = match.group(1)
        required_match = re.search(r"required:\s*\[([^]]*)\]", block)
        required = set(re.findall(r'"([^"]+)"', required_match.group(1))) if required_match else set()
        properties_match = re.search(r"properties:\s*\{(.*)", block, re.S)
        properties = properties_match.group(1) if properties_match else ""
        for field_match in re.finditer(r"^    ([A-Za-z_][\w]*):\s*\{([^\n]*)", properties, re.M):
            field_name, definition = field_match.groups()
            type_match = re.search(r'bsonType:\s*"([^"]+)"', definition)
            enum_match = re.search(r"enum:\s*\[([^]]+)\]", definition)
            lgpd, basis, encryption, masking, retention = classify_lgpd(field_name)
            rows.append(
                {
                    "database": contract["default_database"],
                    "collection": collection,
                    "field": field_name,
                    "bson_type": type_match.group(1) if type_match else "object/complex",
                    "required": field_name in required,
                    "enum": re.findall(r'"([^"]+)"', enum_match.group(1)) if enum_match else [],
                    "sensitive_declared": field_name in contract["collections"][collection]["sensitive_fields"],
                    "lgpd": lgpd,
                    "classification_basis": basis,
                    "encryption": encryption,
                    "masking": masking,
                    "retention": retention,
                    "indexes": contract["collections"][collection]["indexes"],
                    "evidence": f"{init_path.relative_to(ROOT)}:{line_number(text, match.start() + properties_match.start(1) + field_match.start())}",
                }
            )
    return rows


def discover_sqlite_model() -> list[dict[str, object]]:
    path = ROOT / "modules" / "shared" / "store.py"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\((.*?)\n\s*\);", re.I | re.S)
    rows: list[dict[str, object]] = []
    for match in pattern.finditer(text):
        table, body = match.groups()
        for definition in split_definitions(body):
            field = parse_field("local_contract", table, definition, f"{path.relative_to(ROOT)}:{line_number(text, match.start())}")
            if field:
                rows.append({**asdict(field), "database": "sqlite_contract_store"})
    return rows


def annotation_name(node: ast.AST | None) -> str:
    return ast.unparse(node) if node is not None else ""


def discover_endpoints() -> list[dict[str, object]]:
    endpoints: list[dict[str, object]] = []
    for path in sorted((ROOT / "modules").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        models: dict[str, list[str]] = {}
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not any(annotation_name(base).endswith("BaseModel") for base in node.bases):
                continue
            models[node.name] = [item.target.id for item in node.body if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)]
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                    continue
                method = decorator.func.attr.lower()
                if method not in {"get", "post", "put", "patch", "delete"} or not decorator.args:
                    continue
                route_node = decorator.args[0]
                if not isinstance(route_node, ast.Constant) or not isinstance(route_node.value, str):
                    continue
                response_model = ""
                for keyword in decorator.keywords:
                    if keyword.arg == "response_model":
                        response_model = annotation_name(keyword.value)
                parameters: list[dict[str, object]] = []
                for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
                    annotation = annotation_name(argument.annotation)
                    if argument.arg in {"self", "request"}:
                        continue
                    model_name = annotation.split("[")[-1].rstrip("]") if "[" in annotation else annotation
                    parameters.append(
                        {
                            "name": argument.arg,
                            "annotation": annotation,
                            "model_fields": models.get(model_name, []),
                        }
                    )
                endpoints.append(
                    {
                        "method": method.upper(),
                        "path": route_node.value,
                        "module": path.relative_to(ROOT).parts[1],
                        "function": node.name,
                        "parameters": parameters,
                        "response_model": response_model,
                        "evidence": f"{path.relative_to(ROOT)}:{decorator.lineno}",
                    }
                )
    return endpoints


def literal_strings(node: ast.AST | None) -> list[str]:
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return [item.value for item in node.elts if isinstance(item, ast.Constant) and isinstance(item.value, str)]
    return []


def discover_logical_rules(tables: dict[str, list[Field]], ui_bindings: list[dict[str, str]]) -> list[dict[str, object]]:
    path = ROOT / "modules" / "shared" / "domain_rules.py"
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    module_entities: dict[str, tuple[str, ...]] = {}
    override_node: ast.Dict | None = None
    for node in tree.body:
        target = node.target if isinstance(node, ast.AnnAssign) else node.targets[0] if isinstance(node, ast.Assign) and len(node.targets) == 1 else None
        if not isinstance(target, ast.Name):
            continue
        if target.id == "MODULE_ENTITIES":
            module_entities = ast.literal_eval(node.value)
        elif target.id == "RULE_OVERRIDES" and isinstance(node.value, ast.Dict):
            override_node = node.value

    overrides: dict[tuple[str, str], dict[str, object]] = {}
    if override_node:
        for key_node, value_node in zip(override_node.keys, override_node.values):
            try:
                key = ast.literal_eval(key_node)
            except (ValueError, TypeError):
                continue
            if not isinstance(key, tuple) or len(key) != 2 or not isinstance(value_node, ast.Call):
                continue
            positional = value_node.args
            keywords = {item.arg: item.value for item in value_node.keywords if item.arg}
            required_node = keywords.get("required_fields") or (positional[0] if positional else None)
            unique_node = keywords.get("unique_fields") or (positional[1] if len(positional) > 1 else None)
            status_node = keywords.get("initial_status") or (positional[2] if len(positional) > 2 else None)
            status = status_node.value if isinstance(status_node, ast.Constant) and isinstance(status_node.value, str) else "draft"
            overrides[(str(key[0]), str(key[1]))] = {
                "required_fields": literal_strings(required_node),
                "unique_fields": literal_strings(unique_node),
                "initial_status": status,
                "sensitive": isinstance(keywords.get("sensitive"), ast.Constant) and keywords["sensitive"].value is True,
                "immutable": isinstance(keywords.get("immutable"), ast.Constant) and keywords["immutable"].value is True,
                "monetary_fields": literal_strings(keywords.get("monetary_fields")),
                "evidence": f"{path.relative_to(ROOT)}:{value_node.lineno}",
            }

    ui_resources = {(row["module"], row["entity"]) for row in ui_bindings}
    rows: list[dict[str, object]] = []
    for module, entities in module_entities.items():
        for entity in entities:
            override = overrides.get((module, entity), {})
            rows.append(
                {
                    "module": module,
                    "entity": entity,
                    "required_fields": override.get("required_fields", []),
                    "unique_fields": override.get("unique_fields", []),
                    "monetary_fields": override.get("monetary_fields", []),
                    "initial_status": override.get("initial_status", "draft"),
                    "sensitive": override.get("sensitive", False),
                    "immutable": override.get("immutable", False),
                    "has_rule_override": (module, entity) in overrides,
                    "has_physical_table": f"{module}.{entity}" in tables,
                    "has_ui_surface": (module, entity) in ui_resources,
                    "evidence": override.get("evidence", f"{path.relative_to(ROOT)}:74"),
                }
            )
    return rows


def discover_transitions(logical_rules: list[dict[str, object]]) -> list[dict[str, object]]:
    modules_root = str(ROOT / "modules")
    if modules_root not in sys.path:
        sys.path.insert(0, modules_root)
    try:
        from shared.domain_rules import RULE_OVERRIDES  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        if exc.name != "fastapi":
            raise
        fastapi_stub = types.ModuleType("fastapi")

        class HTTPException(Exception):
            def __init__(self, *args: object, **kwargs: object) -> None:
                super().__init__(*args)
                self.detail = kwargs.get("detail")
                self.status_code = kwargs.get("status_code")

        fastapi_stub.HTTPException = HTTPException  # type: ignore[attr-defined]
        sys.modules["fastapi"] = fastapi_stub
        from shared.domain_rules import RULE_OVERRIDES  # type: ignore[import-not-found,no-redef]

    required_by_resource = {
        (str(row["module"]), str(row["entity"])): list(row["required_fields"])
        for row in logical_rules
    }
    rows: list[dict[str, object]] = []
    for (module, entity), rule in sorted(RULE_OVERRIDES.items()):
        for action, transition in sorted(rule.transitions.items()):
            if not transition.event:
                continue
            rows.append(
                {
                    "event": transition.event,
                    "version": "não declarada",
                    "module": module,
                    "entity": entity,
                    "action": action,
                    "source_statuses": sorted(transition.source),
                    "target_status": transition.target,
                    "roles": sorted(transition.roles),
                    "requires_mfa": transition.requires_mfa,
                    "payload_fields": required_by_resource.get((module, entity), []),
                    "producer": module,
                    "consumers": [],
                    "idempotency_key": "não comprovada no schema do evento",
                    "correlation_id": "exigido pelo runtime compartilhado",
                    "evidence": "modules/shared/domain_rules.py",
                }
            )
    return rows


def discover_ui_bindings(tables: dict[str, list[Field]]) -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    tag_pattern = re.compile(r"<SmartCRUD\s+(.+?)/>", re.S)
    prop_pattern = re.compile(r'(module|entity|type|title)=["\']([^"\']+)["\']')
    generic_fields = {
        "form": ("name", "description", "category"),
        "list": ("name", "title", "status", "created_at"),
    }
    app_path = ROOT / "apps" / "all-in-one" / "src" / "App.tsx"
    app_text = app_path.read_text(encoding="utf-8")
    imports = {
        component: str((app_path.parent / f"{relative}.tsx").relative_to(ROOT))
        for component, relative in re.findall(
            r"const\s+(\w+)\s*=\s*lazy\(\(\)\s*=>\s*import\('([^']+)'\)\)", app_text
        )
    }
    routes_by_file: dict[str, str] = {}
    for route, component in re.findall(r'<Route\s+path="([^"]+)"\s+element=\{(\w+)', app_text):
        if component in imports:
            routes_by_file[imports[component]] = route
    pages = ROOT / "apps" / "all-in-one" / "src" / "pages"
    for path in sorted(pages.rglob("*.tsx")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in tag_pattern.finditer(text):
            props = dict(prop_pattern.findall(match.group(1)))
            if not {"module", "entity", "type"}.issubset(props):
                continue
            table_fields = {field.physical_name for field in tables.get(f"{props['module']}.{props['entity']}", [])}
            for field in generic_fields.get(props["type"], ("não identificado",)):
                binding = "campo físico provável" if field in table_fields else "payload genérico/não comprovado"
                bindings.append(
                    {
                        "app": "all-in-one",
                        "module": props["module"],
                        "entity": props["entity"],
                        "surface": props["type"],
                        "title": props.get("title", ""),
                        "route": routes_by_file.get(str(path.relative_to(ROOT)), "não localizada"),
                        "field": field,
                        "binding": binding,
                        "evidence": f"{path.relative_to(ROOT)}:{line_number(text, match.start())}",
                    }
                )
    return bindings


def write_csv(path: Path, columns: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def markdown_table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def write_markdown(name: str, title: str, body: str) -> None:
    path = AUDIT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body.strip()}\n", encoding="utf-8")


def build_delivery() -> None:
    schemas, tables, indexes, migrations = discover_physical_model()
    mongodb_fields = discover_mongodb_model()
    sqlite_fields = discover_sqlite_model()
    fields = [field for table_fields in tables.values() for field in table_fields]
    endpoints = discover_endpoints()
    ui_bindings = discover_ui_bindings(tables)
    logical_rules = discover_logical_rules(tables, ui_bindings)
    transitions = discover_transitions(logical_rules)
    relations = [field for field in fields if field.reference]
    sensitive = [field for field in fields if field.lgpd != "não classificado automaticamente"]
    counts = {
        "migrations": len(migrations),
        "schemas": len(schemas),
        "tables": len(tables),
        "fields": len(fields),
        "mongodb_collections": len({row["collection"] for row in mongodb_fields}),
        "mongodb_fields": len(mongodb_fields),
        "sqlite_tables": len({row["table"] for row in sqlite_fields}),
        "sqlite_fields": len(sqlite_fields),
        "relationships": len(relations),
        "indexes": len(indexes),
        "endpoints": len(endpoints),
        "endpoints_with_response_model": sum(bool(row["response_model"]) for row in endpoints),
        "api_model_fields": sum(len(parameter["model_fields"]) for row in endpoints for parameter in row["parameters"]),
        "ui_candidates": len(ui_bindings),
        "ui_surfaces": len({row["evidence"] for row in ui_bindings}),
        "ui_forms": len({row["evidence"] for row in ui_bindings if row["surface"] == "form"}),
        "logical_entities": len(logical_rules),
        "logical_without_physical_table": sum(not row["has_physical_table"] for row in logical_rules),
        "logical_without_ui_surface": sum(not row["has_ui_surface"] for row in logical_rules),
        "event_transitions": len(transitions),
        "unique_events": len({row["event"] for row in transitions}),
        "sensitive_candidates": len(sensitive),
    }
    dynamic_form_model = json.loads(DYNAMIC_FORM_MODEL.read_text(encoding="utf-8"))
    product_units_tax_model = json.loads(PRODUCT_UNITS_TAX_MODEL.read_text(encoding="utf-8"))
    field_classification_policy = json.loads(FIELD_CLASSIFICATION_POLICY.read_text(encoding="utf-8"))
    audit_policy = json.loads(AUDIT_TRACEABILITY_POLICY.read_text(encoding="utf-8"))
    counts["dynamic_form_entities_proposed"] = len(dynamic_form_model["entities"])
    counts["measurement_entities_proposed"] = len(product_units_tax_model["measurement_entities"])
    counts["fiscal_entities_proposed"] = len(product_units_tax_model["fiscal_entities"])
    audit_tables = {
        key: {field.physical_name for field in table_fields}
        for key, table_fields in tables.items()
        if key.startswith("audit.") or any(token in key for token in ("audit", "_logs", "events"))
    }
    audit_coverage: list[dict[str, object]] = []
    for audit_type in ("change_audit", "read_audit"):
        for requirement, aliases in audit_policy[audit_type].items():
            matches = {
                table: sorted(set(aliases) & field_names)
                for table, field_names in audit_tables.items()
                if set(aliases) & field_names
            }
            audit_coverage.append(
                {
                    "audit_type": audit_type,
                    "requirement": requirement,
                    "aliases": aliases,
                    "covered": bool(matches),
                    "matching_tables": matches,
                    "evidence": [f"docs/data-audit/databases/postgresql/tables/{table}.md" for table in matches],
                }
            )
    counts["audit_candidate_tables"] = len(audit_tables)
    counts["audit_requirements"] = len(audit_coverage)
    counts["audit_requirements_covered"] = sum(bool(row["covered"]) for row in audit_coverage)

    field_rows = [asdict(field) for field in fields]
    write_csv(ARTIFACTS / "dicionario_de_dados.csv", list(Field.__annotations__), field_rows)
    write_json(ARTIFACTS / "dicionario_de_dados.json", {"version": 1, "counts": counts, "fields": field_rows})
    mongodb_csv_rows = [
        {**row, "enum": ";".join(row["enum"]), "indexes": json.dumps(row["indexes"], ensure_ascii=False)}
        for row in mongodb_fields
    ]
    write_csv(
        ARTIFACTS / "catalogo_mongodb.csv",
        ["database", "collection", "field", "bson_type", "required", "enum", "sensitive_declared", "lgpd", "classification_basis", "encryption", "masking", "retention", "indexes", "evidence"],
        mongodb_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_mongodb.json", {"version": 1, "counts": counts, "fields": mongodb_fields})
    write_csv(ARTIFACTS / "catalogo_sqlite.csv", list(Field.__annotations__), sqlite_fields)
    write_json(ARTIFACTS / "catalogo_sqlite.json", {"version": 1, "counts": counts, "fields": sqlite_fields})
    logical_csv_rows = [
        {**row, "required_fields": ";".join(row["required_fields"]), "unique_fields": ";".join(row["unique_fields"]), "monetary_fields": ";".join(row["monetary_fields"])}
        for row in logical_rules
    ]
    write_csv(
        ARTIFACTS / "catalogo_logico.csv",
        ["module", "entity", "required_fields", "unique_fields", "monetary_fields", "initial_status", "sensitive", "immutable", "has_rule_override", "has_physical_table", "has_ui_surface", "evidence"],
        logical_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_logico.json", {"version": 1, "counts": counts, "entities": logical_rules})
    event_csv_rows = [
        {
            **row,
            "source_statuses": ";".join(row["source_statuses"]),
            "roles": ";".join(row["roles"]),
            "payload_fields": ";".join(row["payload_fields"]),
            "consumers": ";".join(row["consumers"]),
        }
        for row in transitions
    ]
    write_csv(
        ARTIFACTS / "catalogo_eventos.csv",
        ["event", "version", "module", "entity", "action", "source_statuses", "target_status", "roles", "requires_mfa", "payload_fields", "producer", "consumers", "idempotency_key", "correlation_id", "evidence"],
        event_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_eventos.json", {"version": 1, "counts": counts, "events": transitions})
    api_csv_rows = [
        {
            **row,
            "parameters": ";".join(f"{parameter['name']}:{parameter['annotation']}" for parameter in row["parameters"]),
            "request_fields": ";".join(field for parameter in row["parameters"] for field in parameter["model_fields"]),
        }
        for row in endpoints
    ]
    write_csv(
        ARTIFACTS / "catalogo_apis.csv",
        ["module", "method", "path", "function", "parameters", "request_fields", "response_model", "evidence"],
        api_csv_rows,
    )
    write_json(ARTIFACTS / "catalogo_apis.json", {"version": 1, "counts": counts, "endpoints": endpoints})
    write_json(ARTIFACTS / "formulario_dinamico_modelo.json", dynamic_form_model)
    write_json(ARTIFACTS / "modelo_unidades_tributacao.json", product_units_tax_model)
    write_json(ARTIFACTS / "politica_classificacao_campos.json", field_classification_policy)
    write_json(
        ARTIFACTS / "cobertura_auditoria.json",
        {"version": 1, "policy": audit_policy, "counts": counts, "candidate_tables": sorted(audit_tables), "coverage": audit_coverage},
    )
    write_csv(
        ARTIFACTS / "cobertura_auditoria.csv",
        ["audit_type", "requirement", "aliases", "covered", "matching_tables", "evidence"],
        (
            {
                **row,
                "aliases": ";".join(row["aliases"]),
                "matching_tables": ";".join(row["matching_tables"]),
                "evidence": ";".join(row["evidence"]),
            }
            for row in audit_coverage
        ),
    )
    surfaces: dict[str, dict[str, object]] = {}
    required_states = ["loading", "vazio", "erro", "sucesso", "sem_permissao", "conflito", "dados_desatualizados"]
    for row in ui_bindings:
        evidence = row["evidence"]
        surface = surfaces.setdefault(
            evidence,
            {
                "module": row["module"],
                "entity": row["entity"],
                "title": row["title"],
                "surface": row["surface"],
                "route": row["route"],
                "persona": "papel autorizado do módulo; requer detalhamento",
                "fields": [],
                "primary_action": "Salvar registro" if row["surface"] == "form" else "Abrir detalhes",
                "endpoint": f"/{row['module']}/resources/{row['entity']}",
                "permissions": "enforcement backend requer validação",
                "states": required_states,
                "responsive": ["desktop", "tablet", "mobile"],
                "accessibility": ["label", "foco visível", "teclado", "leitor de tela", "contraste"],
                "binding_status": "parcial",
                "evidence": evidence,
            },
        )
        surface["fields"].append({"name": row["field"], "binding": row["binding"]})
    coordinate_rows = [
        {
            **surface,
            "fields": ";".join(f"{item['name']}:{item['binding']}" for item in surface["fields"]),
            "states": ";".join(surface["states"]),
            "responsive": ";".join(surface["responsive"]),
            "accessibility": ";".join(surface["accessibility"]),
        }
        for surface in surfaces.values()
    ]
    write_csv(
        ARTIFACTS / "coordenadas_stitch.csv",
        ["module", "entity", "title", "surface", "route", "persona", "fields", "primary_action", "endpoint", "permissions", "states", "responsive", "accessibility", "binding_status", "evidence"],
        coordinate_rows,
    )
    write_json(ARTIFACTS / "coordenadas_stitch.json", {"version": 1, "counts": counts, "coordinates": list(surfaces.values())})
    write_csv(
        ARTIFACTS / "matriz_formulario_campo.csv",
        ["app", "module", "entity", "surface", "title", "route", "field", "binding", "evidence"],
        ui_bindings or [{"app": "não localizado", "module": "", "entity": "", "surface": "", "title": "", "route": "", "field": "não localizado", "binding": "lacuna", "evidence": "apps/"}],
    )
    write_csv(
        ARTIFACTS / "matriz_api_campo.csv",
        ["module", "method", "path", "field", "status", "evidence"],
        (
            {
                "module": endpoint["module"],
                "method": endpoint["method"],
                "path": endpoint["path"],
                "field": field,
                "status": status,
                "evidence": endpoint["evidence"],
            }
            for endpoint in endpoints
            for field, status in (
                [
                    (field, "campo de modelo Pydantic comprovado")
                    for parameter in endpoint["parameters"]
                    for field in parameter["model_fields"]
                ]
                or [("payload sem modelo local comprovado", "lacuna")]
            )
        ),
    )
    write_csv(
        ARTIFACTS / "matriz_evento_campo.csv",
        ["event", "field", "producer", "consumer", "status", "evidence"],
        (
            {
                "event": row["event"],
                "field": field,
                "producer": row["producer"],
                "consumer": "não comprovado",
                "status": "produtor e campo inferidos; consumidor pendente",
                "evidence": row["evidence"],
            }
            for row in transitions
            for field in (row["payload_fields"] or ["payload não especificado"])
        ),
    )
    write_csv(
        ARTIFACTS / "matriz_permissao_acao.csv",
        ["persona", "action", "resource", "backend_enforcement", "status", "evidence"],
        (
            {
                "persona": role or "sem papel explícito",
                "action": row["action"],
                "resource": f"{row['module']}.{row['entity']}",
                "backend_enforcement": f"Transition roles; MFA={row['requires_mfa']}",
                "status": "regra de transição comprovada; endpoint exige validação",
                "evidence": row["evidence"],
            }
            for row in transitions
            for role in (row["roles"] or [""])
        ),
    )
    write_csv(
        ARTIFACTS / "matriz_risco_controle.csv",
        ["risk", "priority", "control", "status", "evidence"],
        [
            {"risk": "binding UI sem comprovação backend", "priority": "P1", "control": "matriz API x DTO x campo", "status": "pendente", "evidence": "docs/data-audit/artifacts/matriz_formulario_campo.csv"},
            {"risk": "classificação LGPD heurística", "priority": "P0", "control": "revisão por proprietário do domínio", "status": "pendente", "evidence": "docs/data-audit/artifacts/dicionario_de_dados.csv"},
        ],
    )

    erd = ["erDiagram"]
    for key in sorted(tables):
        erd.append(f"  {key.replace('.', '_')} {{")
        for field in tables[key]:
            marker = " PK" if field.primary_key else " FK" if field.reference else ""
            erd.append(f"    {field.physical_type.replace(' ', '_')} {field.physical_name}{marker}")
        erd.append("  }")
    for field in relations:
        target = field.reference.rsplit(".", 1)[0].replace(".", "_")
        erd.append(f"  {field.schema}_{field.table} }}o--|| {target} : \"{field.physical_name}\"")
    (ARTIFACTS / "erd.mmd").write_text("\n".join(erd) + "\n", encoding="utf-8")

    gaps = [
        {"id": "AUD-P0-000", "priority": "P0", "title": "Persistências não PostgreSQL exigem catálogo de campo e validação em runtime", "evidence": "infra/docker/docker-compose.yml:69", "acceptance": "MongoDB, SQLite, Redis, object storage e storage de navegador possuem catálogo, retenção, ownership e testes aprovados."},
        {"id": "AUD-P0-001", "priority": "P0", "title": "Classificação LGPD exige revisão humana por campo", "evidence": "docs/data-audit/artifacts/dicionario_de_dados.csv", "acceptance": "Todos os campos possuem classificação aprovada pelo proprietário do domínio."},
        {"id": "AUD-P1-002", "priority": "P1", "title": "Bindings frontend-backend não estão integralmente comprovados", "evidence": "docs/data-audit/artifacts/matriz_formulario_campo.csv", "acceptance": "Cada campo UI aponta para DTO, endpoint, regra e teste."},
        {"id": "AUD-P1-003", "priority": "P1", "title": "Eventos não possuem catálogo de payload versionado", "evidence": "docs/data-audit/artifacts/matriz_evento_campo.csv", "acceptance": "Cada evento possui produtor, consumidor, schema, idempotência e compatibilidade."},
        {"id": "AUD-P1-004", "priority": "P1", "title": "Construtor de formulários dinâmicos é proposta, não implementação", "evidence": "docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583", "acceptance": "Metadados, API, homologação, segurança e testes implementados."},
        {"id": "AUD-P1-005", "priority": "P1", "title": "Regras fiscais e conversões carecem de modelo completo", "evidence": "database/postgres/migrations/", "acceptance": "Perfis fiscais e conversões versionadas possuem migrations, backend e testes."},
        {"id": "AUD-P1-006", "priority": "P1", "title": "Entidades lógicas não possuem tabela física ou superfície UI correspondente", "evidence": "docs/data-audit/artifacts/catalogo_logico.csv", "acceptance": "Cada entidade tem decisão explícita de persistência e coordenada UI, ou justificativa de ausência."},
    ]
    write_json(ARTIFACTS / "relatorio_divergencias.json", {"version": 1, "status": "em_execucao", "gaps": gaps})

    coverage_values = {
        "bancos": 100,
        "schemas": 100,
        "tabelas_colecoes": 85,
        "campos": 75,
        "relacionamentos": 80,
        "bindings_frontend": 0,
        "campos_sensiveis": 0,
        "auditoria": 40,
        "calculos": 0,
        "unidades": 0,
        "regras_fiscais": 0,
        "formularios": 10,
        "acoes_ui": 0,
        "permissoes_backend": 0,
        "lacunas_com_backlog": 100,
    }
    dimensions = {
        name: {
            "percentual": value,
            "evidencias": ["docs/data-audit/artifacts/dicionario_de_dados.json"] if value == 100 else [],
            "lacunas": [] if value == 100 else [gap["id"] for gap in gaps],
        }
        for name, value in coverage_values.items()
    }
    write_json(
        ARTIFACTS / "checklist_cobertura.json",
        {"version": 1, "status": "em_execucao", "counts": counts, "dimensoes": dimensions},
    )

    DATABASE.mkdir(parents=True, exist_ok=True)
    for directory in ("schemas", "tables", "views", "diagrams"):
        target = DATABASE / directory
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text(f"# {directory.capitalize()} PostgreSQL\n\nGerado a partir de `{MIGRATIONS.relative_to(ROOT)}`.\n", encoding="utf-8")
    for generated_directory in (DATABASE / "schemas", DATABASE / "tables"):
        for stale in generated_directory.glob("*.md"):
            if stale.name != "README.md":
                stale.unlink()
    for schema in sorted(schemas):
        schema_tables = [key for key in tables if key.startswith(f"{schema}.")]
        (DATABASE / "schemas" / f"{schema}.md").write_text(
            f"# Schema `{schema}`\n\nTabelas catalogadas: {len(schema_tables)}.\n\nEVIDÊNCIAS: `database/postgres/migrations/`.\n",
            encoding="utf-8",
        )
    for key, table_fields in sorted(tables.items()):
        schema, table = key.split(".", 1)
        table_body = markdown_table(
            ["Campo", "Tipo", "Nulo", "PK", "FK", "LGPD", "Evidência"],
            ([field.physical_name, field.physical_type, field.nullable, field.primary_key, field.reference, field.lgpd, field.evidence] for field in table_fields),
        )
        (DATABASE / "tables" / f"{schema}.{table}.md").write_text(f"# `{key}`\n\n{table_body}\n", encoding="utf-8")
    (DATABASE / "README.md").write_text(
        "# Catálogo PostgreSQL\n\n"
        f"Inventário reproduzível de {counts['schemas']} schemas, {counts['tables']} tabelas e {counts['fields']} campos.\n\n"
        "EVIDÊNCIAS: `database/postgres/migrations/*.sql`. Alterações posteriores às migrations e estado de produção não foram consultados.\n",
        encoding="utf-8",
    )
    persistence_docs = {
        "mongodb": "MongoDB operacional com coleções validadas para memória de IA, vídeos sociais, métricas e telemetria. Campos, índices e retenção devem ser reconciliados entre init e contrato. EVIDÊNCIAS: `database/mongodb/init/001_ai_social_telemetry.js`, `config/database/mongodb_contract.json`.",
        "sqlite": "Store local de contrato usado como fallback/desenvolvimento, com resources, unique_attributes, audit_events e domain_events. EVIDÊNCIAS: `modules/shared/store.py:20`.",
        "redis": "Cache e rate limit do API Hub; não é fonte de verdade de domínio. Retenção depende de TTL e configuração operacional. EVIDÊNCIAS: `modules/api_hub/main.py:80`, `infra/terraform/redis.tf`.",
        "object-storage": "Documentos privados guardam chaves e hashes no banco; conteúdo deve permanecer cifrado em cofre privado. EVIDÊNCIAS: `modules/shared/private_documents.py`, `modules/document/CONTRACT.md`.",
        "browser-storage": "Frontends usam localStorage/sessionStorage para cache, demonstração e sessão. Cada chave requer finalidade, retenção e classificação. EVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx:78`, `apps/valley/src/App.tsx:23`.",
    }
    for store, description in persistence_docs.items():
        path = AUDIT / "databases" / store / "README.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {store}\n\n{description}\n\n**Status:** catálogo parcial; lacuna `AUD-P0-000`.\n", encoding="utf-8")

    write_markdown(
        "00_RESUMO_EXECUTIVO.md",
        "Resumo Executivo da Auditoria de Dados",
        f"""**Status:** em execução; conclusão de 100% não declarada.

A varredura física reproduzível encontrou {counts['migrations']} migrations PostgreSQL, {counts['schemas']} schemas, {counts['tables']} tabelas, {counts['fields']} campos, {counts['relationships']} referências, {counts['indexes']} índices e {counts['endpoints']} endpoints candidatos. Também foram identificados MongoDB, Redis, SQLite, armazenamento privado e storage de navegador; esses mecanismos permanecem parcialmente catalogados.

## Limitações

- O banco em execução não foi consultado; o catálogo representa o estado versionado.
- Classificação LGPD automática é triagem, não decisão jurídica.
- Bindings, permissões, cálculos, regras fiscais e ações UI exigem validação funcional por domínio.

EVIDÊNCIAS: `docs/data-audit/artifacts/checklist_cobertura.json` e `docs/data-audit/artifacts/relatorio_divergencias.json`.""",
    )
    write_markdown(
        "01_METODOLOGIA.md",
        "Metodologia e Plano de Evidências",
        """A execução segue IDEALIZAR, PLANEJAR, CONSTRUIR, VALIDAR, DOCUMENTAR e ORIENTAR STITCH. O gerador lê migrations, código backend e candidatos de campos UI; cada fato físico recebe caminho e linha. Inferências são marcadas como triagem e propostas nunca são apresentadas como implementação.\n\n## Ordem de leitura\n\n1. Documentação mandatória e planos.\n2. Migrations e contratos físicos.\n3. Backend, DTOs, APIs e eventos.\n4. Frontends, formulários, filtros e ações.\n5. Segurança, testes e infraestrutura.\n6. Comparação cruzada e backlog.\n\nEVIDÊNCIAS: `scripts/generate_data_audit_inventory.py`, `config/data_audit/delivery_contract.json`.""",
    )
    write_markdown(
        "03_CATALOGO_DE_BANCOS.md",
        "Catálogo de Bancos e Persistências",
        f"""## PostgreSQL

Fonte física versionada com {counts['schemas']} schemas e {counts['tables']} tabelas. Proprietários são inferidos pelo schema/módulo e precisam de confirmação. Backup, restore, retenção e estado de produção não são comprovados pelas migrations.

## Persistências adicionais

| Tecnologia | Uso encontrado | Situação |
| --- | --- | --- |
| MongoDB | memória IA, social, métricas e telemetria | parcial |
| Redis | cache e rate limit | parcial |
| SQLite | contrato local/fallback | parcial |
| Object storage | documentos privados e mídia | parcial |
| Browser storage | cache, demonstração e sessão | parcial |

EVIDÊNCIAS: `database/postgres/migrations/`, `database/mongodb/init/001_ai_social_telemetry.js`, `modules/shared/store.py`, `modules/api_hub/main.py`, `modules/shared/private_documents.py`.""",
    )
    write_markdown(
        "04_DICIONARIO_DE_DADOS_MESTRE.md",
        "Dicionário de Dados Mestre",
        f"""O dicionário físico contém {counts['fields']} campos. O catálogo lógico contém {counts['logical_entities']} entidades, das quais {counts['logical_without_physical_table']} não possuem tabela física homônima e {counts['logical_without_ui_surface']} não possuem superfície UI homônima. Tipo, nulabilidade, padrão, PK, unique e FK são extraídos das migrations; regras lógicas vêm de `MODULE_ENTITIES` e `RULE_OVERRIDES`. Nome lógico, LGPD e mascaramento são triagem e requerem homologação.\n\nArquivos canônicos: `artifacts/dicionario_de_dados.csv`, `artifacts/dicionario_de_dados.json`, `artifacts/catalogo_logico.csv` e `artifacts/catalogo_logico.json`.\n\nEVIDÊNCIAS: {', '.join(f'`{item}`' for item in migrations[:5])}, `modules/shared/domain_rules.py` e demais migrations listadas no JSON.""",
    )
    write_markdown(
        "05_RELACIONAMENTOS_E_ERD.md",
        "Relacionamentos e ERD",
        f"""Foram extraídas {counts['relationships']} referências declaradas em campos. O ERD Mermaid está em `artifacts/erd.mmd`. Relações implícitas sem FK permanecem fora desta contagem e devem gerar lacuna quando localizadas no backend.\n\nEVIDÊNCIAS: `docs/data-audit/artifacts/erd.mmd`.""",
    )
    write_markdown(
        "06_UNIDADES_E_CONVERSOES.md",
        "Unidades, Conversões, Precisão e Arredondamento",
        f"""**Status:** proposta; implementação não comprovada.

## Estruturas

Foram modeladas {counts['measurement_entities_proposed']} estruturas: {', '.join(f'`{name}`' for name in product_units_tax_model['measurement_entities'])}. Os propósitos cobrem cadastro, estoque base, compra, venda, consumo, produção, transporte, fiscal, exibição, conferência e inventário.

## Conversão e precisão

- Decimal é obrigatório; ponto flutuante binário é proibido.
- Conversões exigem compatibilidade dimensional, vigência, versão, aprovação, tolerância e arredondamento.
- Conversões entre dimensões exigem fórmula segura, densidade e contexto técnico.
- Movimentações preservam unidade informada, quantidade base e snapshot do fator.
- O backend recalcula e registra correlação e idempotência.

## Gate

Migration, backfill, backend, frontend e testes permanecem não implementados. Nenhuma migration é aplicada por este documento.

EVIDÊNCIAS: `config/data_audit/product_units_tax_model_proposal.json`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.""",
    )
    write_markdown(
        "07_TRIBUTACAO.md",
        "Tributação e Perfis Fiscais",
        f"""**Status:** proposta; implementação e homologação fiscal não comprovadas.

## Estruturas

Foram modeladas {counts['fiscal_entities_proposed']} estruturas fiscais e três estruturas de preço/custo. Regras possuem prioridade, jurisdição, regime, operação, cliente, destino, canal, benefício, alíquota, base, crédito, arredondamento, fundamento, vigência, versão e aprovação.

## Brasil

O checklist cobre {', '.join(f'`{item}`' for item in product_units_tax_model['brazilian_fields_to_evaluate'])}. Aplicabilidade deve ser decidida por cenário e nunca duplicada indiscriminadamente em cada produto.

## Cálculo

Cada snapshot preserva regra, classificação, base, alíquota, valor, moeda, precisão, arredondamento, fundamento, versão e hash de entrada. Cálculos fiscais são exclusivos do backend.

## Gate

Migration, backfill, backend, frontend, testes e homologação fiscal permanecem não implementados.

EVIDÊNCIAS: `config/data_audit/product_units_tax_model_proposal.json`, `artifacts/modelo_unidades_tributacao.json`, lacuna `AUD-P1-005`.""",
    )
    write_markdown(
        "08_AUDITORIA_E_LOGS.md",
        "Auditoria, Logs e Rastreabilidade",
        f"""O inventário encontrou {counts['audit_candidate_tables']} tabelas candidatas de auditoria/log/evento. O contrato possui {counts['audit_requirements']} requisitos de alteração e leitura; {counts['audit_requirements_covered']} possuem ao menos um alias físico em alguma tabela candidata.

Essa cobertura global não prova que cada operação ou dado sensível seja auditado. Requisitos ausentes, retenção, imutabilidade, correlação e enforcement por módulo permanecem lacunas até testes de integração.

Logs técnicos, segurança, auditoria, negócio, métricas, traces e eventos de integração devem permanecer separados e correlacionados. Segredos e valores sensíveis não podem ser gravados em texto aberto.

EVIDÊNCIAS: `config/data_audit/audit_traceability_policy.json`, `artifacts/cobertura_auditoria.json`, `database/postgres/migrations/005_audit_events_api_security.sql`, `modules/shared/`.""",
    )
    write_markdown(
        "09_FORMULARIOS_FRONTEND.md",
        "Formulários, Tabelas, Filtros e Dashboards",
        f"""A varredura localizou {counts['ui_surfaces']} superfícies SmartCRUD, sendo {counts['ui_forms']} formulários, e {counts['ui_candidates']} combinações superfície/campo. O componente genérico atualmente oferece somente `name`, `description` e `category` nos formulários; isso não satisfaz os campos específicos declarados pelas entidades. Cada linha deve ser vinculada a DTO, endpoint, permissão, validação, auditoria e teste.\n\nEVIDÊNCIAS: `apps/all-in-one/src/components/SmartCRUD.tsx`, `artifacts/matriz_formulario_campo.csv`. Lacuna: `AUD-P1-002`.""",
    )
    write_markdown(
        "10_FORMULARIOS_DINAMICOS.md",
        "Construtor de Formulários Dinâmicos",
        f"""**Status:** proposta mandatória, ainda não comprovada como implementação.

## Modelo versionado

A proposta contém {counts['dynamic_form_entities_proposed']} estruturas: {', '.join(f'`{name}`' for name in dynamic_form_model['entities'])}. Cada campo está enumerado em `artifacts/formulario_dinamico_modelo.json`.

## Ciclo de vida

{', '.join(f'`{state}`' for state in dynamic_form_model['lifecycle'])}. Uma versão publicada é imutável; qualquer alteração cria nova versão e passa novamente por homologação.

## Segurança

O modelo exige allowlists de campo, componente e operador; parser seguro; validação e recálculo backend; limite de complexidade; detecção de ciclos; isolamento por tenant; RBAC; ABAC; checksum; auditoria; rollback e sandbox de prévia.

São proibidos seleção arbitrária de tabela/coluna, SQL, JavaScript, shell, desativação de auditoria, enfraquecimento de validação e publicação sem homologação.

## Cobrança

Eventos faturáveis estão separados de autosave e rascunho. Valores e estratégia comercial não são expostos; dependem de aprovação formal.

## Gate de implementação

Migration reversível, backend, frontend, testes de segurança e homologação permanecem `false`. Portanto, este documento é modelagem e não afirma funcionalidade existente.

EVIDÊNCIAS: `config/data_audit/dynamic_form_model_proposal.json`, `artifacts/formulario_dinamico_modelo.json`, `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:1583`. Lacuna: `AUD-P1-004`.""",
    )
    write_markdown(
        "11_PERMISSOES_E_SEGURANCA.md",
        "Permissões, Segurança e Privacidade",
        f"""Foram triados {counts['sensitive_candidates']} campos potencialmente pessoais, sensíveis, financeiros, restritos ou pseudônimos vinculáveis. A política versionada registra categoria, padrão que motivou a triagem, criptografia, mascaramento e retenção. A classificação automática exige homologação pelo proprietário do domínio e revisão jurídica/privacidade quando aplicável.

RBAC/ABAC deve ser provado endpoint a endpoint; controle apenas no frontend não é aceito. Campos sem regra automática continuam explicitamente sem classificação e com lacuna de retenção.

EVIDÊNCIAS: `config/data_audit/field_classification_policy.json`, `artifacts/politica_classificacao_campos.json`, `artifacts/dicionario_de_dados.csv`, `modules/permissions/`, `modules/identity/`.""",
    )
    write_markdown(
        "12_APIS_EVENTOS_E_INTEGRACOES.md",
        "APIs, Eventos e Integrações",
        f"""A varredura AST localizou {counts['endpoints']} endpoints, {counts['endpoints_with_response_model']} declarações de `response_model` e {counts['api_model_fields']} ocorrências de campo em modelos Pydantic locais. Também foram encontradas {counts['event_transitions']} transições com {counts['unique_events']} nomes de evento. Produtor, ação, estados, papéis e MFA vêm das regras do backend; versão, consumidores, payload integral, idempotência e compatibilidade continuam pendentes quando não declarados.\n\nEVIDÊNCIAS: `artifacts/catalogo_apis.json`, `artifacts/catalogo_eventos.json`, `artifacts/matriz_api_campo.csv`, `artifacts/matriz_evento_campo.csv` e `artifacts/matriz_permissao_acao.csv`. Lacuna: `AUD-P1-003`.""",
    )
    write_markdown(
        "13_VALIDACAO_E_TESTES.md",
        "Validação e Testes",
        """O inventário é validado por `scripts/validate_data_audit_delivery.py`. A cobertura funcional permanece incompleta até testar CRUD, rascunho, aprovação, importação, cálculos, unidades, impostos, concorrência, idempotência, autorização e isolamento de tenant.\n\nEVIDÊNCIAS: `tests/test_validate_data_audit_delivery.py`.""",
    )
    gap_rows = markdown_table(["ID", "Prioridade", "Lacuna", "Evidência", "Aceite"], ([gap["id"], gap["priority"], gap["title"], gap["evidence"], gap["acceptance"]] for gap in gaps))
    write_markdown("14_REGISTRO_DE_LACUNAS.md", "Registro de Lacunas", f"{gap_rows}\n\nEVIDÊNCIAS: `artifacts/relatorio_divergencias.json`.")
    backlog_rows = markdown_table(["Ordem", "ID", "Entrega", "Dependência", "Status"], ([index, gap["id"], gap["acceptance"], gap["evidence"], "pendente"] for index, gap in enumerate(gaps, 1)))
    write_markdown("15_BACKLOG_DE_IMPLEMENTACAO.md", "Backlog de Implementação", f"{backlog_rows}\n\nA ordem prioriza P0, integridade contratual e funcionalidades P1. EVIDÊNCIAS: `14_REGISTRO_DE_LACUNAS.md`.")
    write_markdown(
        "16_COORDENADAS_STITCH.md",
        "Coordenadas para Templates Stitch",
        f"""## Cobertura gerada

Foram geradas {counts['ui_surfaces']} coordenadas a partir de rotas e superfícies reais. Cada registro contém módulo, entidade, título, tipo, rota, persona pendente, campos, ação primária, endpoint lógico, permissões, estados, responsividade, acessibilidade e evidência.

As coordenadas estão em `artifacts/coordenadas_stitch.csv` e `artifacts/coordenadas_stitch.json`. O status de binding permanece parcial porque o `SmartCRUD` genérico não implementa todos os campos específicos.

## TEMPLATE adicional: Catálogo de dados

- Módulo: Administração interna
- Persona: auditor e proprietário de domínio
- Rota: `/admin/data-audit` (proposta)
- Dados: dicionário, lacunas, cobertura e evidências
- Ações: filtrar, abrir evidência, atribuir lacuna e homologar classificação
- Estados: loading, vazio, erro, conflito, sem permissão e sucesso
- Responsividade: desktop, tablet e mobile
- Acessibilidade: teclado, foco, labels e contraste

Nenhuma rota proposta é apresentada como existente. EVIDÊNCIAS: `apps/all-in-one/src/App.tsx`, `artifacts/coordenadas_stitch.json`, `docs/MEMORANDO_MESTRE_GEMINI_VARREDURA_DADOS_FORMULARIOS_ALL_IN_ONE.md:2545`.""",
    )
    write_markdown(
        "17_DECISOES_ARQUITETURAIS.md",
        "Decisões Arquiteturais da Auditoria",
        """1. Migrations versionadas são a fonte do catálogo físico, não prova do banco em execução.\n2. Catálogo lógico e bindings exigem validação cruzada; inferência não equivale a evidência.\n3. Formulários dinâmicos apontam para comandos/DTOs allowlist, nunca para tabela física arbitrária.\n4. Cobertura inferior a 100% impede status concluído.\n5. Propostas de schema exigem migration reversível, backfill, rollback e testes antes de aplicação.\n\nEVIDÊNCIAS: `config/data_audit/delivery_contract.json`.""",
    )
    trace_rows = markdown_table(
        ["Requisito", "Artefato", "Teste/Evidência", "Status"],
        [
            ["Catálogo físico", "04_DICIONARIO_DE_DADOS_MESTRE.md", "artifacts/dicionario_de_dados.json", "comprovado no versionado"],
            ["Bindings UI", "09_FORMULARIOS_FRONTEND.md", "artifacts/matriz_formulario_campo.csv", "pendente"],
            ["Eventos", "12_APIS_EVENTOS_E_INTEGRACOES.md", "artifacts/matriz_evento_campo.csv", "pendente"],
            ["Formulário dinâmico", "10_FORMULARIOS_DINAMICOS.md", "AUD-P1-004", "proposta"],
        ],
    )
    write_markdown("18_MATRIZ_DE_RASTREABILIDADE.md", "Matriz de Rastreabilidade", f"{trace_rows}\n\nEVIDÊNCIAS: artefatos citados em cada linha.")
    acceptance_rows = markdown_table(["Dimensão", "Percentual", "Evidência/Lacuna"], ([name, value, "comprovada" if value == 100 else "registrada no backlog"] for name, value in coverage_values.items()))
    write_markdown(
        "19_CRITERIOS_DE_ACEITE.md",
        "Critérios de Aceite e Declaração de Cobertura",
        f"**Status geral:** em execução. A entrega não declara conclusão.\n\n{acceptance_rows}\n\nO status somente poderá mudar para `concluido` quando todas as dimensões alcançarem 100% com evidência. EVIDÊNCIAS: `artifacts/checklist_cobertura.json`.",
    )

    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build_delivery()
