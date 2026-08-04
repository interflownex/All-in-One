#!/usr/bin/env python3
"""Gate incremental do catálogo regulatório da Fase 0.

Valida o contrato, os bundles B0-B14 e exige registro prévio para colunas
introduzidas por novas migrations após a baseline congelada.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/compliance/field_registry.v1.json"
BUNDLES = ROOT / "config/compliance/bundles.v1.json"
REQUIRED_FIELDS = {
    "field_id",
    "asset",
    "field",
    "owner",
    "physical_type",
    "required",
    "purpose",
    "legal_basis",
    "sensitivity",
    "retention_policy",
    "access_policy",
    "security_policy",
    "source",
    "lineage",
    "disposal_policy",
    "status",
}
SENSITIVITY = {
    "public",
    "internal",
    "personal",
    "sensitive_personal",
    "financial",
    "secret",
}
STATUS = {"implemented", "partial", "planned", "conditional", "divergent"}
FORBIDDEN_LITERAL = re.compile(
    r"(?i)(cvv|private[_ -]?key|client[_ -]?secret|access[_ -]?token)"
    r"\s*[:=]\s*['\"][^'\"]+['\"]"
)
CREATE_TABLE_START = re.compile(
    r"(?is)create\s+table\s+(?:if\s+not\s+exists\s+)?([\w.\"]+)\s*\("
)
ADD_COLUMN = re.compile(
    r"(?is)alter\s+table\s+([\w.\"]+).*?"
    r"add\s+column\s+(?:if\s+not\s+exists\s+)?([\w\"]+)"
)


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"JSON inválido ou ausente: {path.relative_to(ROOT)}: {exc}")


def normalize(value: str) -> str:
    return value.replace('"', "").strip().lower()


def validate_bundles(data: dict[str, Any]) -> set[str]:
    bundles = data.get("bundles")
    if not isinstance(bundles, list):
        fail("bundles.v1.json deve conter uma lista 'bundles'")
    ids = {item.get("id") for item in bundles if isinstance(item, dict)}
    expected = {f"B{i}" for i in range(15)}
    if ids != expected:
        fail(f"Bundles devem ser exatamente B0-B14; encontrados: {sorted(ids)}")
    return expected


def validate_registry(
    data: dict[str, Any], bundle_ids: set[str]
) -> set[tuple[str, str]]:
    if data.get("schema_version") != "1.0.0":
        fail("schema_version do catálogo deve ser 1.0.0")
    baseline = data.get("baseline_sha")
    if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline):
        fail("baseline_sha deve ser SHA Git completo de 40 caracteres")
    fields = data.get("fields")
    if not isinstance(fields, list):
        fail("fields deve ser uma lista")

    keys: set[tuple[str, str]] = set()
    ids: set[str] = set()
    for index, item in enumerate(fields):
        if not isinstance(item, dict):
            fail(f"fields[{index}] deve ser objeto")
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            fail(f"fields[{index}] incompleto; faltam {sorted(missing)}")
        if item["sensitivity"] not in SENSITIVITY:
            fail(f"fields[{index}].sensitivity inválida")
        if item["status"] not in STATUS:
            fail(f"fields[{index}].status inválido")
        if not isinstance(item["lineage"], list):
            fail(f"fields[{index}].lineage deve ser lista")
        selected = set(item.get("bundle_ids", []))
        if not selected <= bundle_ids:
            fail(f"fields[{index}] referencia bundle inexistente")
        field_id = item["field_id"]
        if field_id in ids:
            fail(f"field_id duplicado: {field_id}")
        ids.add(field_id)
        key = (normalize(item["asset"]), normalize(item["field"]))
        if key in keys:
            fail(f"campo duplicado no catálogo: {key[0]}.{key[1]}")
        keys.add(key)
    return keys


def _parenthesized_body(sql: str, open_index: int) -> str:
    """Extrai o corpo iniciado em ``open_index`` respeitando aninhamento."""

    depth = 0
    quote: str | None = None
    index = open_index
    while index < len(sql):
        char = sql[index]
        if quote:
            if char == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return sql[open_index + 1 : index]
        index += 1
    fail("CREATE TABLE com parênteses não balanceados")


def _split_top_level_csv(value: str) -> list[str]:
    """Divide definições de colunas somente em vírgulas de nível superior."""

    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    index = 0
    while index < len(value):
        char = value[index]
        if quote:
            if char == quote:
                if index + 1 < len(value) and value[index + 1] == quote:
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                fail("Definição SQL com parênteses não balanceados")
        elif char == "," and depth == 0:
            parts.append(value[start:index])
            start = index + 1
        index += 1
    if depth != 0 or quote:
        fail("Definição SQL incompleta ou não balanceada")
    parts.append(value[start:])
    return parts


def changed_migrations(baseline: str) -> list[Path]:
    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "--diff-filter=AM",
                f"{baseline}...HEAD",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    return [
        ROOT / line
        for line in result.stdout.splitlines()
        if "migration" in line.lower() and line.endswith(".sql")
    ]


def parse_columns(sql: str) -> set[tuple[str, str]]:
    found: set[tuple[str, str]] = set()
    for match in CREATE_TABLE_START.finditer(sql):
        table = normalize(match.group(1))
        body = _parenthesized_body(sql, match.end() - 1)
        for raw in _split_top_level_csv(body):
            token = raw.strip().split()
            if not token:
                continue
            first = normalize(token[0])
            if first not in {
                "constraint",
                "primary",
                "foreign",
                "unique",
                "check",
                "exclude",
            }:
                found.add((table, first))
    for match in ADD_COLUMN.finditer(sql):
        found.add((normalize(match.group(1)), normalize(match.group(2))))
    return found


def validate_new_migrations(
    registered: set[tuple[str, str]], baseline: str
) -> None:
    orphaned: list[str] = []
    for path in changed_migrations(baseline):
        sql = path.read_text(encoding="utf-8")
        if FORBIDDEN_LITERAL.search(sql):
            fail(f"segredo ou token literal detectado em {path.relative_to(ROOT)}")
        for table, field in parse_columns(sql):
            if (table, field) not in registered:
                orphaned.append(f"{path.relative_to(ROOT)}: {table}.{field}")
    if orphaned:
        fail(
            "Novas colunas sem registro prévio:\n- "
            + "\n- ".join(sorted(orphaned))
        )


def main() -> int:
    try:
        bundle_ids = validate_bundles(load_json(BUNDLES))
        registry = load_json(REGISTRY)
        registered = validate_registry(registry, bundle_ids)
        validate_new_migrations(registered, registry["baseline_sha"])
    except ValueError as exc:
        print(f"[COMPLIANCE GATE FAIL] {exc}", file=sys.stderr)
        return 1
    print(
        f"[COMPLIANCE GATE OK] {len(registered)} campos registrados; "
        "bundles B0-B14 válidos."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
