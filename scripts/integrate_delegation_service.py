#!/usr/bin/env python3
"""Integrar DelegationService nos endpoints de primícia.

Onda 2: Persistência
Data: 26/07/2026
Branch: feature/primicias-selecionadas-v1
"""

import re
from pathlib import Path

# Mapping de recursos
PRIMICIAS = {
    "ai_core": ("ai_core", 23, "Recibo de Memória"),
    "api_hub": ("api_hub", 24, "Contrato Adaptativo"),
    "bi": ("bi", 22, "Perguntas Não Feitas"),
    "bpm": ("bpm", 16, "Laboratório de Processos"),
    "business": ("business", 2, "Consórcio Flash"),
    "crm": ("crm", 15, "Promessas ao Cliente"),
    "delivery": ("delivery", 7, "Capacidade de Rota"),
    "document": ("document", 17, "Obrigações Vivas"),
    "erp": ("erp", 12, "Encerramento Contínuo"),
    "finance": ("finance", 4, "Dinheiro Earmarked"),
    "health": ("health", 19, "Cápsula de Continuidade"),
    "hr": ("hr", 18, "Agendamento de Afinidade Justa"),
    "identity": ("identity", 1, "Prova de Identidade Mínima"),
    "jobs": ("jobs", 11, "Disponibilidade Reversa"),
    "legal": ("legal", 20, "Radar de Impacto"),
    "marketplace": ("marketplace", 5, "Coligação de Compra Local"),
    "mobility": ("mobility", 10, "Rota Intencional Premium"),
    "permissions": ("permissions", 3, "Procuração Operacional Expirável"),
    "property": ("property", 21, "Capacidade Compartilhada"),
    "riders": ("riders", 8, "Passaporte de Evidência"),
    "services": ("services", 9, "Contrato de Resultado"),
    "tms": ("tms", 14, "Câmbio Cego de Capacidade"),
    "wms": ("wms", 13, "Confiança de Inventário"),
}

MODULES_DIR = Path(__file__).parent.parent / "modules"

def update_primicias_file(module_name: str, resource_num: int, resource_name: str):
    """Atualizar arquivo _primicias.py com persistência."""

    file_path = MODULES_DIR / module_name / "_primicias.py"

    if not file_path.exists():
        print(f"❌ {module_name}: arquivo não encontrado")
        return

    with open(file_path) as f:
        content = f.read()

    # Adicionar import do service se não existir
    if "from shared.delegation_service import DelegationService" not in content:
        # Encontrar a última importação de shared
        import_match = re.search(r"(from shared\.[^\n]+\n)", content)
        if import_match:
            last_import_end = import_match.end()
            content = (
                content[:last_import_end] +
                "from shared.delegation_service import DelegationService\n" +
                content[last_import_end:]
            )

    # Inicializar service após router
    if "delegation_service = DelegationService()" not in content:
        router_match = re.search(r"(router = APIRouter\([^)]+\)\n)", content)
        if router_match:
            router_end = router_match.end()
            content = (
                content[:router_end] +
                "delegation_service = DelegationService()\n" +
                content[router_end:]
            )

    # Atualizar create_delegation
    old_create = r'@router\.post\("/delegations".*?\n    return DelegationResponse\([^)]*\)'
    new_create = '''@router.post("/delegations", response_model=DelegationResponse, status_code=201)
async def create_delegation(request: DelegationRequest) -> DelegationResponse:
    """Cria uma delegação/procuração.

    A feature flag deve estar habilitada para este endpoint estar disponível.
    """
    require_flag(FLAG)

    # Delegar validações e persistência ao service
    return delegation_service.create_delegation(
        grantor_id="system",  # Em produção, usar X-Actor-User-Id
        grantee_id=request.grantee_id,
        purpose=request.purpose,
        constraints=request.constraints.dict() if request.constraints else None,
    )'''

    content = re.sub(old_create, new_create, content, flags=re.DOTALL)

    # Atualizar get_delegation
    old_get = r'@router\.get\("/delegations/{delegation_id}".*?\n    return DelegationResponse\([^)]*\)'
    new_get = '''@router.get("/delegations/{delegation_id}", response_model=DelegationResponse)
async def get_delegation(delegation_id: str) -> DelegationResponse:
    """Retorna detalhes de uma delegação específica."""
    require_flag(FLAG)

    # Buscar do banco de dados
    result = delegation_service.get_delegation(delegation_id)
    return DelegationResponse(**result)'''

    content = re.sub(old_get, new_get, content, flags=re.DOTALL)

    # Atualizar update_delegation
    old_patch = r'@router\.patch\("/delegations/{delegation_id}".*?\n    return DelegationResponse\([^)]*\)'
    new_patch = '''@router.patch("/delegations/{delegation_id}", response_model=DelegationResponse)
async def update_delegation(
    delegation_id: str,
    update: DelegationUpdate,
) -> DelegationResponse:
    """Atualiza uma delegação existente."""
    require_flag(FLAG)

    # Atualizar status no banco de dados
    result = delegation_service.update_delegation(
        delegation_id=delegation_id,
        status=update.status,
        updated_by="system",  # Em produção, usar X-Actor-User-Id
    )
    return DelegationResponse(**result)'''

    content = re.sub(old_patch, new_patch, content, flags=re.DOTALL)

    with open(file_path, "w") as f:
        f.write(content)

    print(f"✅ {module_name}: endpoints integrados com DelegationService")


def main():
    """Processar todos os módulos."""
    print("=" * 70)
    print("Onda 2: Integrar DelegationService nos endpoints de primícia")
    print("=" * 70)

    success_count = 0
    failed_count = 0

    for module_name, (_, resource_num, resource_name) in PRIMICIAS.items():
        try:
            update_primicias_file(module_name, resource_num, resource_name)
            success_count += 1
        except Exception as e:
            print(f"❌ {module_name}: {str(e)}")
            failed_count += 1

    print("\n" + "=" * 70)
    print(f"Resumo: {success_count} módulos integrados, {failed_count} falharam")
    print("=" * 70)


if __name__ == "__main__":
    main()
