#!/usr/bin/env python3
"""Gera arquivos de primícia para cada módulo backend.

Cria um arquivo _primicias.py em cada módulo com:
  - Endpoints de feature-status
  - Endpoints de delegação
  - Endpoints de health/status
  - Integração com shared.feature_flags
"""

import sys
from datetime import datetime
from pathlib import Path

# Mapeamento de módulo → (module_short, resource_number, primicia_short)
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

PRIMACIA_FILE_TEMPLATE = '''"""Endpoints de primícia para o módulo {module_name}.

Recurso {resource_number}: {primicia_name}
Gerado automaticamente em {timestamp}
"""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from shared.feature_flags import is_flag_enabled, require_flag

router = APIRouter(tags=["{module_name}-primicias"])
FLAG = "primicia.{module_short}.{primicia_short}"


# === Modelos Pydantic ===

class FeatureStatusResponse(BaseModel):
    """Resposta de status da feature."""
    flag: str
    enabled: bool
    resource: int
    version: str = "1.0.0"


class DelegationConstraints(BaseModel):
    """Restrições de uma delegação."""
    max_amount: float | None = None
    allowed_actions: list[str] = Field(default_factory=list)
    single_use: bool = False
    valid_from: datetime | None = None
    valid_until: datetime | None = None


class DelegationRequest(BaseModel):
    """Request para criar delegação."""
    grantee_id: str = Field(..., min_length=1)
    purpose: str = Field(..., min_length=1)
    constraints: DelegationConstraints | None = None


class DelegationResponse(BaseModel):
    """Resposta de delegação."""
    delegation_id: str
    grantor_id: str | None = None
    grantee_id: str
    purpose: str
    constraints: dict | None = None
    created_at: str
    status: str


class DelegationUpdate(BaseModel):
    """Update para delegação existente."""
    status: str | None = None
    constraints: dict | None = None


class HealthResponse(BaseModel):
    """Resposta de health check."""
    status: str
    module: str
    timestamp: str


class StatusResponse(BaseModel):
    """Resposta de status."""
    module: str
    feature_enabled: bool
    timestamp: str


# === Endpoints ===

@router.get("/feature-status", response_model=FeatureStatusResponse)
async def get_feature_status() -> FeatureStatusResponse:
    """Retorna status da primícia para {module_name}."""
    return FeatureStatusResponse(
        flag=FLAG,
        enabled=is_flag_enabled(FLAG),
        resource={resource_number},
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check do módulo {module_name}."""
    return HealthResponse(
        status="healthy",
        module="{module_name}",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Status geral do módulo {module_name}."""
    return StatusResponse(
        module="{module_name}",
        feature_enabled=is_flag_enabled(FLAG),
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/delegations", response_model=DelegationResponse, status_code=201)
async def create_delegation(request: DelegationRequest) -> DelegationResponse:
    """Cria uma delegação/procuração para {module_name}.

    A feature flag deve estar habilitada para este endpoint estar disponível.
    """
    require_flag(FLAG)

    # Validações básicas
    if request.constraints:
        if request.constraints.max_amount is not None and request.constraints.max_amount < 0:
            raise HTTPException(status_code=422, detail="max_amount deve ser positivo")

        if (request.constraints.valid_from and request.constraints.valid_until):
            if request.constraints.valid_until <= request.constraints.valid_from:
                raise HTTPException(
                    status_code=422,
                    detail="valid_until deve ser após valid_from"
                )

    return DelegationResponse(
        delegation_id=str(uuid4()),
        grantee_id=request.grantee_id,
        purpose=request.purpose,
        constraints=request.constraints.dict() if request.constraints else {{}},
        created_at=datetime.now(UTC).isoformat(),
        status="pending",
    )


@router.get("/delegations/{{delegation_id}}", response_model=DelegationResponse)
async def get_delegation(delegation_id: str) -> DelegationResponse:
    """Retorna detalhes de uma delegação específica."""
    require_flag(FLAG)

    # Placeholder - em produção, consultar banco de dados
    return DelegationResponse(
        delegation_id=delegation_id,
        grantee_id="grantee-placeholder",
        purpose="Delegação de exemplo",
        created_at=datetime.now(UTC).isoformat(),
        status="active",
    )


@router.patch("/delegations/{{delegation_id}}", response_model=DelegationResponse)
async def update_delegation(
    delegation_id: str,
    update: DelegationUpdate,
) -> DelegationResponse:
    """Atualiza uma delegação existente."""
    require_flag(FLAG)

    # Placeholder - em produção, consultar e atualizar banco de dados
    return DelegationResponse(
        delegation_id=delegation_id,
        grantee_id="grantee-placeholder",
        purpose="Delegação atualizada",
        created_at=datetime.now(UTC).isoformat(),
        status=update.status or "active",
    )
'''


def generate_primacia_file(
    module_name: str, module_short: str, resource_num: int, primicia_short: str
):
    """Gera arquivo _primicias.py para um módulo."""
    workspace = Path(__file__).resolve().parents[1]
    module_path = workspace / "modules" / module_name

    if not module_path.exists():
        print(f"  ⚠️  {module_name} não existe")
        return False

    primacia_file = module_path / "_primicias.py"

    # Primeiro nome mais amigável para a primícia
    primicia_names = {
        1: "Prova de Identidade Mínima",
        2: "Consórcio Flash",
        3: "Procuração Operacional Expirável",
        4: "Dinheiro Earmarked",
        5: "Coligação de Compra Local",
        7: "Capacidade de Rota",
        8: "Passaporte de Evidência",
        9: "Contrato de Resultado",
        10: "Rota Intencional Premium",
        11: "Disponibilidade Reversa",
        12: "Encerramento Contínuo",
        13: "Confiança de Inventário",
        14: "Câmbio Cego de Capacidade",
        15: "Promessas ao Cliente",
        16: "Laboratório de Processos",
        17: "Obrigações Vivas",
        18: "Agendamento de Afinidade Justa",
        19: "Cápsula de Continuidade",
        20: "Radar de Impacto",
        21: "Capacidade Compartilhada",
        22: "Perguntas Não Feitas",
        23: "Recibo de Memória",
        24: "Contrato Adaptativo",
    }

    primicia_name = primicia_names.get(resource_num, f"Recurso {resource_num}")

    content = PRIMACIA_FILE_TEMPLATE.format(
        module_name=module_name,
        module_short=module_short,
        resource_number=resource_num,
        primicia_short=primicia_short,
        primicia_name=primicia_name,
        timestamp=datetime.now().isoformat(),
    )

    primacia_file.write_text(content)
    print(f"  ✅ {module_name}: Recurso {resource_num} ({primicia_name})")
    return True


def main():
    """Processa todos os módulos."""
    print(f"\n{'=' * 80}")
    print(f"{'GERAR ARQUIVOS DE PRIMÍCIA PARA TODOS OS MÓDULOS':^80}")
    print(f"{'=' * 80}\n")

    generated = 0
    skipped = 0

    for module_name, (module_short, resource_num, primicia_short) in sorted(
        PRIMICIAS.items()
    ):
        try:
            if generate_primacia_file(
                module_name, module_short, resource_num, primicia_short
            ):
                generated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ {module_name}: erro {type(e).__name__}: {e}")
            skipped += 1

    print(f"\n{'=' * 80}")
    print(f"Resumo: {generated} módulos processados, {skipped} pulados")
    print(f"{'=' * 80}\n")

    return 0 if skipped == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
