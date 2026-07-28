from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DYNAMIC_STORE = ROOT / "modules" / "shared" / "dynamic_forms_postgres_store.py"
DATA_AUDIT = ROOT / "scripts" / "generate_data_audit_inventory.py"

EXPECTED_COLLECTION_TABLES = {
    "form_blocks",
    "form_fields",
    "form_calculations",
    "form_validations",
    "form_visibility_rules",
}
EXPECTED_ORDER_FRAGMENTS = {"display_order, id", "created_at, id"}
EXPECTED_REPORTS = {
    "pytest_unit_results.xml",
    "pytest_identity_e2e_results.xml",
}


def literal_strings(node: ast.AST) -> set[str]:
    return {
        child.value
        for child in ast.walk(node)
        if isinstance(child, ast.Constant) and isinstance(child.value, str)
    }


def validate_dynamic_sql_scope() -> list[str]:
    errors: list[str] = []
    source = DYNAMIC_STORE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = literal_strings(tree)

    missing_tables = EXPECTED_COLLECTION_TABLES - literals
    if missing_tables:
        errors.append(
            "Allowlist de tabelas do formulário dinâmico incompleta: "
            + ", ".join(sorted(missing_tables))
        )

    missing_orders = EXPECTED_ORDER_FRAGMENTS - literals
    if missing_orders:
        errors.append(
            "Allowlist de ordenação do formulário dinâmico incompleta: "
            + ", ".join(sorted(missing_orders))
        )

    expected_fragments = (
        'f"SELECT * FROM forms.{table} WHERE form_version_id = %s ORDER BY {order}"',
        'f"DELETE FROM forms.{table} WHERE form_version_id = %s"',
    )
    for fragment in expected_fragments:
        if fragment not in source:
            errors.append(f"Construção SQL esperada mudou: {fragment}")

    if "params.append(status)" not in source or "d.status = %s" not in source:
        errors.append("Filtro de status deixou de usar parâmetro PostgreSQL.")
    return errors


def validate_junit_xml_scope() -> list[str]:
    errors: list[str] = []
    source = DATA_AUDIT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    literals = literal_strings(tree)

    missing_reports = EXPECTED_REPORTS - literals
    if missing_reports:
        errors.append(
            "Lista fixa de relatórios JUnit incompleta: "
            + ", ".join(sorted(missing_reports))
        )
    if "for report in PYTEST_EXECUTION_REPORTS" not in source:
        errors.append("Parser XML deixou de iterar somente sobre a allowlist JUnit.")
    if "ET.parse(report).getroot()" not in source:
        errors.append("Ponto de parsing XML esperado foi alterado e exige nova revisão.")
    return errors


def validate() -> list[str]:
    return validate_dynamic_sql_scope() + validate_junit_xml_scope()


def main() -> int:
    errors = validate()
    if errors:
        print("Exceções Bandit delimitadas ficaram inválidas:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Exceções Bandit delimitadas validadas: SQL usa allowlists literais e "
        "XML lê somente relatórios JUnit locais fixos."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
