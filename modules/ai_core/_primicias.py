"""Endpoints de primícia para o módulo ai_core.

Recurso 23: Recibo de Memória
Gerado automaticamente em 2026-07-26T14:39:59.390350
"""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from shared.feature_flags import is_flag_enabled, require_flag

router = APIRouter(tags=["ai_core-primicias"])
FLAG = "primicia.ai.memory_receipt"


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
    """Retorna status da primícia para ai_core."""
    return FeatureStatusResponse(
        flag=FLAG,
        enabled=is_flag_enabled(FLAG),
        resource=23,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check do módulo ai_core."""
    return HealthResponse(
        status="healthy",
        module="ai_core",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Status geral do módulo ai_core."""
    return StatusResponse(
        module="ai_core",
        feature_enabled=is_flag_enabled(FLAG),
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/delegations", response_model=DelegationResponse, status_code=201)
async def create_delegation(request: DelegationRequest) -> DelegationResponse:
    """Cria uma delegação/procuração para ai_core.
    
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
        constraints=request.constraints.dict() if request.constraints else {},
        created_at=datetime.now(UTC).isoformat(),
        status="pending",
    )


@router.get("/delegations/{delegation_id}", response_model=DelegationResponse)
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


@router.patch("/delegations/{delegation_id}", response_model=DelegationResponse)
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
