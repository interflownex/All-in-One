#!/usr/bin/env python3
"""Corrige imports de _primicias.py nos main.py dos módulos.

Muda de:
  from _primicias import router as primacia_router
Para:
  from ._primicias import router as primacia_router
"""

import sys
from pathlib import Path

MODULES = [
    "ai_core",
    "api_hub",
    "bi",
    "bpm",
    "business",
    "crm",
    "delivery",
    "document",
    "erp",
    "finance",
    "health",
    "hr",
    "identity",
    "jobs",
    "legal",
    "marketplace",
    "mobility",
    "permissions",
    "property",
    "riders",
    "services",
    "tms",
    "wms",
]


def fix_imports(module_name: str) -> bool:
    """Corrige imports no main.py do módulo."""
    workspace = Path(__file__).resolve().parents[1]
    module_path = workspace / "modules" / module_name
    main_py = module_path / "main.py"

    if not main_py.exists():
        print(f"  ⚠️  {module_name}: main.py não existe")
        return False

    content = main_py.read_text()

    # Padrão para alterar import
    # De: from _primicias import router as primacia_router
    # Para: from ._primicias import router as primacia_router
    if "from _primicias import" in content:
        new_content = content.replace(
            "from _primicias import router as primacia_router",
            "from ._primicias import router as primacia_router",
        )
        main_py.write_text(new_content)
        print(f"  ✅ {module_name}: import corrigido")
        return True
    elif "from ._primicias import" in content:
        print(f"  ✓ {module_name}: import já correto")
        return True
    else:
        print(f"  ⚠️  {module_name}: nenhum import de _primicias encontrado")
        return False


def main():
    """Processa todos os módulos."""
    print(f"\n{'=' * 80}")
    print(f"{'CORRIGIR IMPORTS DE _PRIMICIAS.PY':^80}")
    print(f"{'=' * 80}\n")

    fixed = 0
    skipped = 0

    for module_name in sorted(MODULES):
        try:
            if fix_imports(module_name):
                fixed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ {module_name}: erro {type(e).__name__}: {e}")
            skipped += 1

    print(f"\n{'=' * 80}")
    print(f"Resumo: {fixed} módulos corrigidos, {skipped} pulados/com erro")
    print(f"{'=' * 80}\n")

    return 0 if skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
