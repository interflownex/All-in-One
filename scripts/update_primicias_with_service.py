#!/usr/bin/env python3
"""Atualizar todos os módulos para usar DelegationService.

Onda 2: Persistência
Data: 26/07/2026
Branch: feature/primicias-selecionadas-v1
"""

from pathlib import Path

# Mapping de módulos
MODULES = [
    "ai_core", "api_hub", "bi", "bpm", "business", "crm", "delivery",
    "document", "erp", "finance", "health", "hr", "identity", "jobs",
    "legal", "marketplace", "mobility", "permissions", "property", "riders",
    "services", "tms", "wms",
]

MODULES_DIR = Path(__file__).parent.parent / "modules"

# Template de header para arquivo _primicias.py com DelegationService
HEADER_TEMPLATE = '''"""Endpoints de primícia para o módulo {module}.

Recurso {resource}: {primacia}
Gerado automaticamente em 2026-07-26T14:39:59.407431

Onda 2: Persistência em PostgreSQL
Data: 26/07/2026
Branch: feature/primicias-selecionadas-v1
"""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from shared.feature_flags import is_flag_enabled, require_flag
from shared.delegation_service import DelegationService

router = APIRouter(tags=["{module}-primicias"])
FLAG = "primicia.{module}.{flag_name}"
delegation_service = DelegationService()
'''

# Template de método do endpoint
CREATE_DELEGATION_TEMPLATE = '''@router.post("/delegations", response_model=DelegationResponse, status_code=201)
async def create_delegation(request: DelegationRequest) -> DelegationResponse:
    """Cria uma delegação/procuração.

    A feature flag deve estar habilitada para este endpoint estar disponível.
    """
    require_flag(FLAG)

    # Delegar validações e persistência ao service
    result = delegation_service.create_delegation(
        grantor_id="system",  # Em produção, usar X-Actor-User-Id
        grantee_id=request.grantee_id,
        purpose=request.purpose,
        constraints=request.constraints.dict() if request.constraints else None,
    )

    return DelegationResponse(**result)
'''

GET_DELEGATION_TEMPLATE = '''@router.get("/delegations/{delegation_id}", response_model=DelegationResponse)
async def get_delegation(delegation_id: str) -> DelegationResponse:
    """Retorna detalhes de uma delegação específica."""
    require_flag(FLAG)

    # Buscar do banco de dados
    result = delegation_service.get_delegation(delegation_id)
    return DelegationResponse(**result)
'''

UPDATE_DELEGATION_TEMPLATE = '''@router.patch("/delegations/{delegation_id}", response_model=DelegationResponse)
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
    return DelegationResponse(**result)
'''

def update_module_primicias(module_name: str):
    """Atualizar arquivo _primicias.py de um módulo."""
    file_path = MODULES_DIR / module_name / "_primicias.py"

    if not file_path.exists():
        return False, "arquivo não encontrado"

    try:
        with open(file_path) as f:
            content = f.read()

        # Adicionar import do service se não existir
        if "from shared.delegation_service import DelegationService" not in content:
            # Encontrar última importação de shared
            if "from shared.feature_flags import" in content:
                content = content.replace(
                    "from shared.feature_flags import is_flag_enabled, require_flag",
                    "from shared.feature_flags import is_flag_enabled, require_flag\nfrom shared.delegation_service import DelegationService"
                )

        # Inicializar service após router
        if "delegation_service = DelegationService()" not in content:
            if "FLAG = \"primicia." in content:
                # Encontrar a linha FLAG e adicionar delegation_service depois
                lines = content.split("\n")
                new_lines = []
                for line in lines:
                    new_lines.append(line)
                    if line.startswith("FLAG = \"primicia."):
                        new_lines.append("delegation_service = DelegationService()")
                content = "\n".join(new_lines)

        # Atualizar endpoints para usar o service
        # Substituir mock responses por calls ao service

        # POST /delegations
        if 'return DelegationResponse(' in content and 'delegation_service.create_delegation' not in content:
            # Encontrar e substituir a primeira ocorrência em POST
            post_start = content.find('@router.post("/delegations"')
            if post_start != -1:
                post_end = content.find('@router.get("/delegations/{delegation_id}"', post_start)
                if post_end != -1:
                    post_section = content[post_start:post_end]

                    # Substituir o corpo da função
                    new_post_section = '''@router.post("/delegations", response_model=DelegationResponse, status_code=201)
async def create_delegation(request: DelegationRequest) -> DelegationResponse:
    """Cria uma delegação/procuração.

    A feature flag deve estar habilitada para este endpoint estar disponível.
    """
    require_flag(FLAG)

    # Delegar validações e persistência ao service
    result = delegation_service.create_delegation(
        grantor_id="system",  # Em produção, usar X-Actor-User-Id
        grantee_id=request.grantee_id,
        purpose=request.purpose,
        constraints=request.constraints.dict() if request.constraints else None,
    )

    return DelegationResponse(**result)


'''
                    content = content[:post_start] + new_post_section + content[post_end:]

        # GET /delegations/{id}
        if '@router.get("/delegations/{delegation_id}"' in content and 'delegation_service.get_delegation' not in content:
            get_start = content.find('@router.get("/delegations/{delegation_id}"')
            if get_start != -1:
                get_end = content.find('@router.patch("/delegations/{delegation_id}"', get_start)
                if get_end != -1:
                    new_get_section = '''@router.get("/delegations/{delegation_id}", response_model=DelegationResponse)
async def get_delegation(delegation_id: str) -> DelegationResponse:
    """Retorna detalhes de uma delegação específica."""
    require_flag(FLAG)

    # Buscar do banco de dados
    result = delegation_service.get_delegation(delegation_id)
    return DelegationResponse(**result)


'''
                    content = content[:get_start] + new_get_section + content[get_end:]

        # PATCH /delegations/{id}
        if '@router.patch("/delegations/{delegation_id}"' in content and 'delegation_service.update_delegation' not in content:
            patch_start = content.find('@router.patch("/delegations/{delegation_id}"')
            if patch_start != -1:
                # Encontrar o final do arquivo ou próxima função
                patch_end = content.find('@router.', patch_start + 1)
                if patch_end == -1:
                    patch_end = len(content)

                new_patch_section = '''@router.patch("/delegations/{delegation_id}", response_model=DelegationResponse)
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
    return DelegationResponse(**result)
'''
                content = content[:patch_start] + new_patch_section

        with open(file_path, "w") as f:
            f.write(content)

        return True, "atualizado com sucesso"
    except Exception as e:
        return False, str(e)


def main():
    """Processar todos os módulos."""
    print("=" * 70)
    print("Onda 2: Atualizar endpoints para usar DelegationService")
    print("=" * 70)

    success_count = 0
    failed_count = 0

    for module_name in MODULES:
        success, message = update_module_primicias(module_name)
        if success:
            print(f"✅ {module_name:20} {message}")
            success_count += 1
        else:
            print(f"❌ {module_name:20} {message}")
            failed_count += 1

    print("\n" + "=" * 70)
    print(f"Resumo: {success_count}/{len(MODULES)} módulos processados, {failed_count} falharam")
    print("=" * 70)


if __name__ == "__main__":
    main()
