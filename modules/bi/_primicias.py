"""Endpoints de primícia para o módulo bi.

Recurso 22: Perguntas Não Feitas
Gerado automaticamente em 2026-07-26T14:39:59.398044
"""

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from shared.feature_flags import is_flag_enabled, require_flag
from shared.delegation_service import DelegationService

router = APIRouter(tags=["bi-primicias"])
FLAG = "primicia.bi.unasked_questions"
delegation_service = DelegationService()


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
    """Retorna status da primícia para bi."""
    return FeatureStatusResponse(
        flag=FLAG,
        enabled=is_flag_enabled(FLAG),
        resource=22,
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check do módulo bi."""
    return HealthResponse(
        status="healthy",
        module="bi",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Status geral do módulo bi."""
    return StatusResponse(
        module="bi",
        feature_enabled=is_flag_enabled(FLAG),
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/delegations", response_model=DelegationResponse, status_code=201)
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


@router.get("/delegations/{delegation_id}", response_model=DelegationResponse)
async def get_delegation(delegation_id: str) -> DelegationResponse:
    """Retorna detalhes de uma delegação específica."""
    require_flag(FLAG)
    
    # Buscar do banco de dados
    result = delegation_service.get_delegation(delegation_id)
    return DelegationResponse(**result)


@router.patch("/delegations/{delegation_id}", response_model=DelegationResponse)
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
