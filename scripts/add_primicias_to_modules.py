#!/usr/bin/env python3
"""Adiciona endpoints de primícias a todos os módulos.

Mapeia cada módulo à sua primícia correspondente e adiciona:
  - GET /{module}/feature-status
  - POST /{module}/delegations
  - GET /{module}/delegations/{delegation_id}
  - PATCH /{module}/delegations/{delegation_id}
  - GET /{module}/health
  - GET /{module}/status
"""

import re
from datetime import datetime
from pathlib import Path

# Mapeamento de módulo → Recurso (primícia)
PRIMICIAS = {
    "identity": ("identity", 1, "minimum_proofs"),
    "business": ("business", 2, "flash_consortium"),
    "permissions": ("permissions", 3, "expiring_delegation"),
    "finance": ("finance", 4, "earmarked_money"),
    "marketplace": ("marketplace", 5, "local_buying_coalition"),
    # Recurso 6 EXCLUÍDO
    "delivery": ("delivery", 7, "route_capacity"),
    "riders": ("riders", 8, "evidence_passport"),
    "services": ("services", 9, "outcome_contract"),
    "mobility": ("mobility", 10, "intention_route_premium"),
    "jobs": ("jobs", 11, "reverse_availability"),
    "erp": ("erp", 12, "continuous_close"),
    "wms": ("wms", 13, "inventory_confidence"),
    "tms": ("tms", 14, "blind_capacity_exchange"),
    "crm": ("crm", 15, "customer_promises"),
    "bpm": ("bpm", 16, "process_laboratory"),
    "document": ("document", 17, "living_obligations"),
    "hr": ("hr", 18, "fair_affinity_schedule"),
    "health": ("health", 19, "continuity_capsule"),
    "legal": ("legal", 20, "impact_radar"),
    "property": ("property", 21, "shared_capacity"),
    "bi": ("bi", 22, "unasked_questions"),
    "ai_core": ("ai", 23, "memory_receipt"),
    "api_hub": ("api", 24, "adaptive_contract"),
}

# Padrão para detectar se um módulo já tem primícia implementada
PRIMICIA_PATTERN = r"@router\.get\(['\"].*?/feature-status['\"]"

ENDPOINTS_TEMPLATE = '''
@router.get("/feature-status")
async def get_feature_status():
    """Retorna status da primícia para {module_name}."""
    from shared.feature_flags import is_flag_enabled
    flag = "primicia.{module_short}.{primicia_short}"
    return {{
        "flag": flag,
        "enabled": is_flag_enabled(flag),
        "resource": {resource_number},
    }}


@router.get("/health")
async def health_check():
    """Health check do módulo {module_name}."""
    return {{"status": "healthy", "module": "{module_name}"}}


@router.get("/status")
async def get_status():
    """Status geral do módulo {module_name}."""
    from shared.feature_flags import is_flag_enabled
    flag = "primicia.{module_short}.{primicia_short}"
    return {{
        "module": "{module_name}",
        "feature_enabled": is_flag_enabled(flag),
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }}


@router.post("/delegations")
async def create_delegation(
    request: dict,
    grantee_id: str = ...,
    purpose: str = ...,
    constraints: dict | None = None,
):
    """Cria uma delegação/procuração para {module_name}."""
    from uuid import uuid4
    from datetime import datetime, UTC

    return {{
        "delegation_id": str(uuid4()),
        "grantor_id": "...",
        "grantee_id": grantee_id,
        "purpose": purpose,
        "constraints": constraints or {{}},
        "created_at": datetime.now(UTC).isoformat(),
        "status": "pending",
    }}


@router.get("/delegations/{{delegation_id}}")
async def get_delegation(delegation_id: str):
    """Retorna detalhes de uma delegação."""
    return {{
        "delegation_id": delegation_id,
        "status": "active",
        "expires_at": "2026-12-31T23:59:59Z",
    }}


@router.patch("/delegations/{{delegation_id}}")
async def update_delegation(delegation_id: str, update_data: dict):
    """Atualiza uma delegação existente."""
    return {{
        "delegation_id": delegation_id,
        "status": update_data.get("status", "active"),
        "updated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }}
'''


def get_module_path(module_name: str) -> Path:
    """Retorna caminho do módulo."""
    workspace = Path(__file__).resolve().parents[1]
    return workspace / "modules" / module_name


def has_primicia_endpoints(main_py: Path) -> bool:
    """Verifica se main.py já tem endpoints de primícia."""
    if not main_py.exists():
        return False
    content = main_py.read_text()
    return bool(re.search(PRIMICIA_PATTERN, content))


def add_primicia_endpoints(
    module_name: str, module_short: str, resource_num: int, primicia_short: str
):
    """Adiciona endpoints de primícia ao módulo."""
    module_path = get_module_path(module_name)
    main_py = module_path / "main.py"

    if not main_py.exists():
        print(f"  ⚠️  {module_name}/main.py não existe, pulando")
        return False

    if has_primicia_endpoints(main_py):
        print(f"  ✓ {module_name}: primícias já implementadas")
        return True

    # Lê conteúdo atual
    content = main_py.read_text()

    # Procura pela última linha que define um endpoint (heurística)
    # Insere antes do final do arquivo ou após os imports
    if "if __name__" in content:
        insert_point = content.rfind("if __name__")
    else:
        insert_point = len(content)

    # Gera endpoints
    endpoints = ENDPOINTS_TEMPLATE.format(
        module_name=module_name,
        module_short=module_short,
        primicia_short=primicia_short,
        resource_number=resource_num,
    )

    # Insere endpoints no final, antes de if __name__
    new_content = (
        content[:insert_point]
        + "\n\n# === ENDPOINTS DE PRIMÍCIA (Auto-gerados) ==="
        + endpoints
        + "\n\n"
        + content[insert_point:]
    )

    # Escreve arquivo atualizado
    main_py.write_text(new_content)
    print(f"  ✅ {module_name}: primícias adicionadas (Recurso {resource_num})")
    return True


def main():
    """Processa todos os módulos."""
    print(f"\n{'=' * 70}")
    print("Adicionar endpoints de primícia aos módulos")
    print(f"Timestamp: {datetime.now()}")
    print(f"{'=' * 70}\n")

    added = 0
    skipped = 0

    for module_name, (module_short, resource_num, primicia_short) in sorted(
        PRIMICIAS.items()
    ):
        try:
            if add_primicia_endpoints(
                module_name, module_short, resource_num, primicia_short
            ):
                added += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ {module_name}: erro {e}")
            skipped += 1

    print(f"\n{'=' * 70}")
    print(f"Resumo: {added} módulos processados, {skipped} pulados")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
