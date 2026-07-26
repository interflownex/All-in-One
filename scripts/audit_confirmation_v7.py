#!/usr/bin/env python3
"""Auditor de confirmação v7.

Verifica a consistência entre o catálogo de módulos, os contratos,
a configuração Business (MODULE_NAMES) e o schema OpenAPI do API Hub.

Uso:
    python3 scripts/audit_confirmation_v7.py

Saída:
    Relatório de auditoria em docs/relatorios/audit_confirmation_v7_<data>.md
    Código de saída 0 em sucesso, 1 em falha.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "config" / "module_catalog.json"
CONTRACTS_DIR = ROOT / "contracts"
OPENAPI_PATH = ROOT / "modules" / "api_hub" / "openapi.json"
SETTINGS_PATH = ROOT / "modules" / "business" / "module_settings.py"
REPORTS_DIR = ROOT / "docs" / "relatorios"


def load_catalog() -> list[str]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return [m["slug"] for m in data["modules"]]


def load_module_names_from_settings() -> list[str]:
    source = SETTINGS_PATH.read_text(encoding="utf-8")
    slugs: list[str] = []
    in_block = False
    for line in source.splitlines():
        stripped = line.strip()
        if "MODULE_NAMES" in stripped and "=" in stripped and "{" in stripped:
            in_block = True
            continue
        if in_block:
            if stripped.startswith("}"):
                break
            if stripped.startswith('"') and ":" in stripped:
                slug = stripped.split('"')[1]
                slugs.append(slug)
    return slugs


def load_contracts() -> list[str]:
    return [p.stem for p in CONTRACTS_DIR.glob("*.md")]


def load_openapi_paths() -> list[str]:
    if not OPENAPI_PATH.exists():
        return []
    data = json.loads(OPENAPI_PATH.read_text(encoding="utf-8"))
    return list(data.get("paths", {}).keys())


def check_vision_residuals() -> list[str]:
    issues: list[str] = []
    extensions = ["*.py", "*.ts", "*.tsx"]
    self_path = Path(__file__).resolve()
    search_dirs = [
        ROOT / "modules",
        ROOT / "apps",
        ROOT / "tests",
        ROOT / "scripts",
    ]
    for search_dir in search_dirs:
        for ext in extensions:
            for fpath in search_dir.rglob(ext):
                if ".git" in fpath.parts or "node_modules" in fpath.parts:
                    continue
                if fpath.resolve() == self_path:
                    continue
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for lineno, line in enumerate(content.splitlines(), start=1):
                    lower = line.lower()
                    if (
                        "vision" in lower
                        and "division_by_zero" not in lower
                        and "visibility" not in lower
                        and "provision" not in lower
                        and "supervision" not in lower
                        and "television" not in lower
                    ):
                        rel = fpath.relative_to(ROOT)
                        issues.append(f"{rel}:{lineno}: {line.strip()}")
    return issues


def run_audit() -> dict[str, object]:
    catalog_slugs = load_catalog()
    module_name_slugs = load_module_names_from_settings()
    contract_slugs = load_contracts()
    openapi_paths = load_openapi_paths()

    results: dict[str, object] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "catalog_count": len(catalog_slugs),
        "catalog_slugs": catalog_slugs,
        "checks": {},
    }

    checks: dict[str, object] = {}

    # 1. Catálogo vs MODULE_NAMES
    catalog_set = set(catalog_slugs)
    settings_set = set(module_name_slugs)
    missing_in_settings = sorted(catalog_set - settings_set)
    extra_in_settings = sorted(settings_set - catalog_set)
    checks["catalog_vs_module_names"] = {
        "status": "OK" if not missing_in_settings and not extra_in_settings else "FALHA",
        "missing_in_module_names": missing_in_settings,
        "extra_in_module_names": extra_in_settings,
    }

    # 2. Catálogo vs contratos
    contract_set = set(contract_slugs)
    missing_contracts = sorted(catalog_set - contract_set)
    extra_contracts = sorted(contract_set - catalog_set)
    checks["catalog_vs_contracts"] = {
        "status": "OK" if not missing_contracts else "FALHA",
        "missing_contracts": missing_contracts,
        "extra_contracts": extra_contracts,
    }

    # 3. Referências residuais ao Vision
    vision_issues = check_vision_residuals()
    checks["vision_residuals"] = {
        "status": "OK" if not vision_issues else "FALHA",
        "count": len(vision_issues),
        "occurrences": vision_issues[:20],
    }

    # 4. OpenAPI (informativo)
    if openapi_paths:
        checks["openapi_paths"] = {
            "status": "INFO",
            "count": len(openapi_paths),
        }
    else:
        checks["openapi_paths"] = {
            "status": "AUSENTE",
            "note": f"Arquivo não encontrado em {OPENAPI_PATH.relative_to(ROOT)}",
        }

    results["checks"] = checks

    # Veredicto geral
    failures = [k for k, v in checks.items() if isinstance(v, dict) and v.get("status") == "FALHA"]
    results["overall_status"] = "FALHA" if failures else "OK"
    results["failures"] = failures

    return results


def render_report(audit: dict[str, object]) -> str:
    ts = audit["timestamp"]
    overall = audit["overall_status"]
    checks = audit["checks"]  # type: ignore[assignment]
    catalog_count = audit["catalog_count"]

    lines = [
        "# Relatório de Auditoria de Confirmação v7",
        "",
        f"**Data:** {ts}",
        f"**Repositório:** `interflownex/All-in-One`",
        f"**Resultado geral:** {overall}",
        f"**Módulos no catálogo:** {catalog_count}",
        "",
        "---",
        "",
        "## 1. Catálogo × MODULE_NAMES (module_settings.py)",
        "",
    ]

    cnm = checks["catalog_vs_module_names"]  # type: ignore[index]
    lines.append(f"**Status:** {cnm['status']}")
    if cnm["missing_in_module_names"]:
        lines.append(f"- Faltam em MODULE_NAMES: `{cnm['missing_in_module_names']}`")
    if cnm["extra_in_module_names"]:
        lines.append(f"- Extras em MODULE_NAMES: `{cnm['extra_in_module_names']}`")
    if cnm["status"] == "OK":
        lines.append("- Todos os módulos do catálogo estão presentes em MODULE_NAMES. ✅")

    lines += [
        "",
        "## 2. Catálogo × Contratos",
        "",
    ]
    cvc = checks["catalog_vs_contracts"]  # type: ignore[index]
    lines.append(f"**Status:** {cvc['status']}")
    if cvc["missing_contracts"]:
        lines.append(f"- Contratos ausentes: `{cvc['missing_contracts']}`")
    if cvc["extra_contracts"]:
        lines.append(f"- Contratos sem módulo no catálogo: `{cvc['extra_contracts']}`")
    if cvc["status"] == "OK":
        lines.append("- Todos os módulos possuem contrato. ✅")

    lines += [
        "",
        "## 3. Referências residuais ao módulo Vision",
        "",
    ]
    vr = checks["vision_residuals"]  # type: ignore[index]
    lines.append(f"**Status:** {vr['status']}")
    lines.append(f"**Ocorrências encontradas:** {vr['count']}")
    if vr["occurrences"]:
        lines.append("")
        lines.append("```")
        for occ in vr["occurrences"]:
            lines.append(occ)
        lines.append("```")
    else:
        lines.append("- Nenhuma referência ativa ao Vision encontrada. ✅")

    lines += [
        "",
        "## 4. OpenAPI do API Hub",
        "",
    ]
    oa = checks["openapi_paths"]  # type: ignore[index]
    lines.append(f"**Status:** {oa['status']}")
    if "count" in oa:
        lines.append(f"- Rotas documentadas: {oa['count']}")
    if "note" in oa:
        lines.append(f"- {oa['note']}")

    if audit["failures"]:
        lines += [
            "",
            "## ⚠ Falhas detectadas",
            "",
        ]
        for f in audit["failures"]:  # type: ignore[union-attr]
            lines.append(f"- `{f}`")

    return "\n".join(lines) + "\n"


def main() -> int:
    print("Executando auditoria de confirmação v7...")
    audit = run_audit()
    report = render_report(audit)

    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"audit_confirmation_v7_{date_str}.md"
    report_path.write_text(report, encoding="utf-8")

    print(report)
    print(f"\nRelatório salvo em: {report_path.relative_to(ROOT)}")

    if audit["overall_status"] == "FALHA":
        print("\nAuditoria concluída com FALHAS.")
        return 1
    print("\nAuditoria concluída com SUCESSO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
