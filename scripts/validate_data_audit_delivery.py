#!/usr/bin/env python3
"""Valida a entrega mandatória definida pelo memorando mestre de dados."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config" / "data_audit" / "delivery_contract.json"


def load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"arquivo ausente: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"JSON inválido em {path.relative_to(ROOT)}: {exc}")
    return None


def validate_csv(path: Path, errors: list[str]) -> None:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
    except FileNotFoundError:
        errors.append(f"arquivo ausente: {path.relative_to(ROOT)}")
        return
    if len(rows) < 2 or not rows[0] or any(not column.strip() for column in rows[0]):
        errors.append(
            f"CSV sem cabeçalho e ao menos uma linha de dados: {path.relative_to(ROOT)}"
        )


def validate() -> list[str]:
    errors: list[str] = []
    contract = load_json(CONTRACT_PATH, errors)
    if not isinstance(contract, dict):
        return errors

    audit_root = ROOT / str(contract["root"])
    for relative in contract["required_markdown"]:
        path = audit_root / relative
        if not path.is_file():
            errors.append(f"documento obrigatório ausente: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < 200:
            errors.append(
                f"documento obrigatório insuficiente: {path.relative_to(ROOT)}"
            )

    for relative in contract["required_complementary"]:
        path = audit_root / relative
        if path.suffix == ".csv":
            validate_csv(path, errors)
        elif path.suffix == ".json":
            load_json(path, errors)
        elif not path.is_file() or not path.read_text(encoding="utf-8").strip():
            errors.append(
                f"artefato complementar ausente ou vazio: {path.relative_to(ROOT)}"
            )

    for relative in contract["required_database_paths"]:
        path = audit_root / relative
        if not path.exists():
            errors.append(
                f"estrutura de banco obrigatória ausente: {path.relative_to(ROOT)}"
            )

    coverage_path = audit_root / "artifacts" / "checklist_cobertura.json"
    coverage = load_json(coverage_path, errors)
    if isinstance(coverage, dict):
        dimensions = coverage.get("dimensoes", {})
        if not isinstance(dimensions, dict):
            errors.append("checklist_cobertura.json: 'dimensoes' deve ser objeto")
        else:
            for dimension in contract["coverage_dimensions"]:
                item = dimensions.get(dimension)
                if not isinstance(item, dict):
                    errors.append(f"cobertura sem dimensão obrigatória: {dimension}")
                    continue
                percentage = item.get("percentual")
                if (
                    not isinstance(percentage, (int, float))
                    or not 0 <= percentage <= 100
                ):
                    errors.append(f"percentual de cobertura inválido: {dimension}")
                if not item.get("evidencias") and not item.get("lacunas"):
                    errors.append(
                        f"cobertura sem evidência nem lacuna registrada: {dimension}"
                    )

        declared_status = coverage.get("status")
        incomplete = (
            any(
                isinstance(item, dict) and item.get("percentual") != 100
                for item in dimensions.values()
            )
            if isinstance(dimensions, dict)
            else True
        )
        if declared_status == "concluido" and incomplete:
            errors.append(
                "status 'concluido' é incompatível com cobertura inferior a 100%"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Entrega data-audit reprovada:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Entrega data-audit validada com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
