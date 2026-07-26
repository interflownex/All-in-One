#!/usr/bin/env python3
"""Integra routers de primícia aos módulos FastAPI.

Para cada módulo main.py:
  1. Importa router de _primicias.py
  2. Inclui o router na aplicação
  3. Valida a importação
"""

import sys
import re
from pathlib import Path
from datetime import datetime

# Mapeamento de módulo
MODULES = [
    "ai_core", "api_hub", "bi", "bpm", "business", "crm", "delivery",
    "document", "erp", "finance", "health", "hr", "identity", "jobs",
    "legal", "marketplace", "mobility", "permissions", "property", "riders",
    "services", "tms", "wms",
]

IMPORT_PATTERN = r"^(from fastapi import|from starlette|import)"
INCLUDE_ROUTER_PATTERN = r"app\.include_router\("

def integrate_router(module_name: str) -> bool:
    """Integra router de primícia ao módulo."""
    workspace = Path(__file__).resolve().parents[1]
    module_path = workspace / "modules" / module_name
    main_py = module_path / "main.py"
    
    if not main_py.exists():
        print(f"  ⚠️  {module_name}: main.py não existe")
        return False
    
    content = main_py.read_text()
    
    # Verifica se já está integrado
    if "from _primicias import router as primacia_router" in content:
        print(f"  ✓ {module_name}: já integrado")
        return True
    
    # Encontra linha para adicionar import (após outros imports)
    lines = content.split("\n")
    import_end_idx = 0
    
    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ")) and not line.strip().startswith("#"):
            import_end_idx = i + 1
    
    # Adiciona import de primícia
    primacia_import = "from _primicias import router as primacia_router"
    if import_end_idx < len(lines):
        lines.insert(import_end_idx, primacia_import)
    else:
        lines.append(primacia_import)
    
    # Encontra onde adicionar include_router (no final, antes de if __name__)
    content_updated = "\n".join(lines)
    
    # Procura por app.include_router ou cria um novo bloco
    include_routers_idx = None
    for i, line in enumerate(lines):
        if "app.include_router(" in line:
            # Pega a última ocorrência
            for j in range(i, len(lines)):
                if "app.include_router(" in lines[j]:
                    include_routers_idx = j
    
    if include_routers_idx is not None:
        # Adiciona após o último include_router
        lines.insert(include_routers_idx + 1, "app.include_router(primacia_router)")
    else:
        # Procura por if __name__ e adiciona antes
        for i, line in enumerate(lines):
            if line.startswith("if __name__"):
                lines.insert(i, "app.include_router(primacia_router)\n")
                break
        else:
            # Adiciona no final
            lines.append("app.include_router(primacia_router)")
    
    # Escreve arquivo atualizado
    main_py.write_text("\n".join(lines))
    print(f"  ✅ {module_name}: router integrado")
    return True

def validate_imports(module_name: str) -> bool:
    """Valida se as importações estão corretas."""
    workspace = Path(__file__).resolve().parents[1]
    module_path = workspace / "modules" / module_name
    main_py = module_path / "main.py"
    
    if not main_py.exists():
        return False
    
    content = main_py.read_text()
    has_import = "from _primicias import router as primacia_router" in content
    has_include = "app.include_router(primacia_router)" in content
    
    if has_import and has_include:
        return True
    
    if not has_import or not has_include:
        print(f"  ⚠️  {module_name}: validação falhou")
        if not has_import:
            print(f"     - Falta import de _primicias")
        if not has_include:
            print(f"     - Falta include_router")
        return False
    
    return True

def main():
    """Processa todos os módulos."""
    print(f"\n{'='*80}")
    print(f"{'INTEGRAR ROUTERS DE PRIMÍCIA AOS MÓDULOS':^80}")
    print(f"{'='*80}\n")
    
    integrated = 0
    failed = 0
    
    for module_name in sorted(MODULES):
        try:
            if integrate_router(module_name):
                integrated += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {module_name}: erro {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Resumo: {integrated} módulos integrados, {failed} falharam")
    print(f"{'='*80}\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
