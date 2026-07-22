from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

ModuleState = Literal[
    "mandatory",
    "active",
    "recommended",
    "optional",
    "hidden",
    "disabled",
    "blocked_by_plan",
]
BusinessKind = Literal[
    "physical_store",
    "ecommerce",
    "dropshipping",
    "restaurant",
    "services_provider",
    "carrier",
    "clinic",
    "industry",
    "office",
    "autonomous",
    "rider",
    "driver_partner",
]

MODULE_NAMES: dict[str, str] = {
    "identity": "Identidade",
    "business": "Empresas",
    "permissions": "Permissoes",
    "finance": "Financeiro",
    "marketplace": "Marketplace",
    "stock": "Estoque",
    "delivery": "Entregas",
    "riders": "Entregadores e motoristas",
    "services": "Servicos",
    "mobility": "Mobilidade",
    "jobs": "Vagas e candidatos",
    "erp": "ERP",
    "wms": "Gestao de armazens",
    "tms": "Gestao de transportes",
    "crm": "Relacionamento com clientes",
    "bpm": "Fluxos de trabalho",
    "document": "Documentos",
    "hr": "Recursos humanos",
    "health": "Saude",
    "bi": "Analises e indicadores",
    "api_hub": "Integracoes e APIs",
}

PRESETS: dict[BusinessKind, dict[str, list[str]]] = {
    "physical_store": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["marketplace", "finance", "crm"],
        "recommended": ["stock", "bi"],
        "hidden": ["health", "mobility", "tms", "wms"],
    },
    "ecommerce": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["marketplace", "finance", "stock", "delivery", "crm"],
        "recommended": ["bi", "document"],
        "hidden": ["health", "mobility", "tms"],
    },
    "dropshipping": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["marketplace", "finance", "stock", "crm"],
        "recommended": ["tms", "bi", "document"],
        "hidden": ["health", "mobility", "jobs"],
    },
    "restaurant": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["marketplace", "delivery", "finance", "crm"],
        "recommended": ["stock", "bi"],
        "hidden": ["health", "tms", "wms", "jobs"],
    },
    "services_provider": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["services", "finance", "crm"],
        "recommended": ["document", "jobs", "bi"],
        "hidden": ["marketplace", "wms", "tms"],
    },
    "carrier": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["tms", "finance", "document"],
        "recommended": ["wms", "bi", "hr"],
        "hidden": ["health", "marketplace", "services"],
    },
    "clinic": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["health", "document", "finance"],
        "recommended": ["crm", "hr", "bi"],
        "hidden": ["marketplace", "tms", "wms"],
    },
    "industry": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["erp", "finance", "wms"],
        "recommended": ["tms", "bpm", "bi", "hr"],
        "hidden": ["health", "mobility", "services"],
    },
    "office": {
        "mandatory": ["identity", "business", "permissions"],
        "active": ["crm", "finance", "document"],
        "recommended": ["hr", "bi", "bpm"],
        "hidden": ["wms", "tms", "health"],
    },
    "autonomous": {
        "mandatory": ["identity"],
        "active": ["services", "finance"],
        "recommended": ["document", "crm"],
        "hidden": ["erp", "wms", "tms", "health"],
    },
    "rider": {
        "mandatory": ["identity"],
        "active": ["riders", "delivery", "finance"],
        "recommended": ["document"],
        "hidden": ["erp", "wms", "health", "crm"],
    },
    "driver_partner": {
        "mandatory": ["identity"],
        "active": ["riders", "mobility", "finance"],
        "recommended": ["document"],
        "hidden": ["erp", "wms", "health", "marketplace"],
    },
}


class BusinessClassificationInput(BaseModel):
    business_kind: BusinessKind = Field(alias="businessKind")
    cnae_primary: str | None = Field(default=None, alias="cnaePrimary")
    cnae_secondary: list[str] = Field(default_factory=list, alias="cnaeSecondary")
    has_physical_stock: bool = Field(default=False, alias="hasPhysicalStock")
    sells_online: bool = Field(default=False, alias="sellsOnline")
    performs_delivery: bool = Field(default=False, alias="performsDelivery")
    hires_people: bool = Field(default=False, alias="hiresPeople")
    issues_fiscal_documents: bool = Field(default=False, alias="issuesFiscalDocuments")
    operates_fleet: bool = Field(default=False, alias="operatesFleet")
    has_warehouse: bool = Field(default=False, alias="hasWarehouse")

    model_config = {"populate_by_name": True}


class ModuleRecommendation(BaseModel):
    module_slug: str
    title_pt_br: str
    state: ModuleState
    score: float
    reason_codes: list[str]
    explanation_pt_br: str
    dependencies: list[str]
    can_disable: bool


class ModulePatch(BaseModel):
    state: ModuleState
    reason: str = Field(min_length=3, max_length=500)


class BusinessClassificationRecord(BaseModel):
    company_id: UUID
    business_kind: BusinessKind
    cnae_primary: str | None
    cnae_secondary: list[str]
    operational_tags: list[str]
    confidence: float
    classifier_version: str = "business-module-rules-1.0.0"
    classified_at: str


class CompanyModuleSetting(BaseModel):
    id: UUID
    company_id: UUID
    module_slug: str
    title_pt_br: str
    state: ModuleState
    visibility: Literal["visible", "hidden"]
    source: Literal["automatic", "manual"]
    recommendation_score: float
    recommendation_reason: str
    dependencies: list[str]
    can_disable: bool
    updated_at: str
    updated_by: str


class ApplyRecommendationsPayload(BaseModel):
    classification: BusinessClassificationInput
    actor_id: str = Field(default="business-shell")


class ModuleSettingsResponse(BaseModel):
    company_id: UUID
    classification: BusinessClassificationRecord | None
    modules: list[CompanyModuleSetting]
    audit: list[dict[str, Any]]


_CLASSIFICATIONS: dict[UUID, BusinessClassificationRecord] = {}
_SETTINGS: dict[UUID, dict[str, CompanyModuleSetting]] = {}
_AUDIT: dict[UUID, list[dict[str, Any]]] = {}

router = APIRouter(prefix="/business-modules", tags=["business-modules"])


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _dependencies(module_slug: str) -> list[str]:
    if module_slug == "identity":
        return []
    if module_slug == "business":
        return ["identity"]
    if module_slug == "permissions":
        return ["identity", "business"]
    return [
        dep for dep in ["identity", "business", "permissions"] if dep != module_slug
    ]


def _explanation(
    module_slug: str, state: ModuleState, business_kind: BusinessKind
) -> str:
    module_name = MODULE_NAMES.get(module_slug, module_slug)
    if state == "mandatory":
        return f"{module_name} e obrigatorio para garantir identidade, empresa, permissoes e auditoria da operacao."
    if state == "active":
        return f"{module_name} foi ativado automaticamente porque combina com o perfil operacional {business_kind}."
    if state == "recommended":
        return f"{module_name} e recomendado, mas pode aguardar configuracao manual pela empresa."
    if state == "hidden":
        return f"{module_name} ficara oculto na navegacao inicial para reduzir complexidade sem apagar dados."
    if state == "disabled":
        return (
            f"{module_name} foi desativado manualmente e nao deve executar operacoes."
        )
    return f"{module_name} depende de plano, permissao, configuracao ou revisao administrativa."


def recommend_business_modules(
    input_data: BusinessClassificationInput,
) -> list[ModuleRecommendation]:
    preset = PRESETS[input_data.business_kind]
    dynamic_recommended = [
        *(["stock"] if input_data.has_physical_stock else []),
        *(["wms"] if input_data.has_warehouse else []),
        *(["delivery"] if input_data.performs_delivery else []),
        *(["tms"] if input_data.operates_fleet else []),
        *(["jobs", "hr"] if input_data.hires_people else []),
        *(["erp"] if input_data.issues_fiscal_documents else []),
        *(["marketplace"] if input_data.sells_online else []),
    ]
    mandatory = _unique(preset["mandatory"])
    active = _unique(
        [
            *preset["active"],
            *[module for module in dynamic_recommended if module not in mandatory],
        ]
    )
    recommended = [
        module
        for module in _unique(preset["recommended"])
        if module not in mandatory and module not in active
    ]
    hidden = [
        module
        for module in _unique(preset["hidden"])
        if module not in mandatory
        and module not in active
        and module not in recommended
    ]
    entries: list[tuple[str, ModuleState, float, bool]] = [
        *[(module, "mandatory", 1.0, False) for module in mandatory],
        *[(module, "active", 0.94, True) for module in active],
        *[(module, "recommended", 0.82, True) for module in recommended],
        *[(module, "hidden", 0.25, True) for module in hidden],
    ]
    return [
        ModuleRecommendation(
            module_slug=module,
            title_pt_br=MODULE_NAMES.get(module, module),
            state=state,
            score=score,
            reason_codes=[f"BUSINESS_KIND_{input_data.business_kind.upper()}"],
            explanation_pt_br=_explanation(module, state, input_data.business_kind),
            dependencies=_dependencies(module),
            can_disable=can_disable,
        )
        for module, state, score, can_disable in entries
    ]


def _classification(
    company_id: UUID, input_data: BusinessClassificationInput
) -> BusinessClassificationRecord:
    operational_tags = [
        tag
        for tag, enabled in {
            "HAS_PHYSICAL_STOCK": input_data.has_physical_stock,
            "SELLS_ONLINE": input_data.sells_online,
            "PERFORMS_DELIVERY": input_data.performs_delivery,
            "HIRES_PEOPLE": input_data.hires_people,
            "ISSUES_FISCAL_DOCUMENTS": input_data.issues_fiscal_documents,
            "OPERATES_FLEET": input_data.operates_fleet,
            "HAS_WAREHOUSE": input_data.has_warehouse,
        }.items()
        if enabled
    ]
    return BusinessClassificationRecord(
        company_id=company_id,
        business_kind=input_data.business_kind,
        cnae_primary=input_data.cnae_primary,
        cnae_secondary=input_data.cnae_secondary,
        operational_tags=operational_tags,
        confidence=0.91 if operational_tags else 0.78,
        classified_at=_now(),
    )


def _audit(company_id: UUID, action: str, payload: dict[str, Any]) -> None:
    _AUDIT.setdefault(company_id, []).insert(
        0,
        {
            "id": str(uuid4()),
            "action": action,
            "payload": payload,
            "created_at": _now(),
        },
    )


@router.post("/recommendations", response_model=list[ModuleRecommendation])
def preview_recommendations(
    body: BusinessClassificationInput,
) -> list[ModuleRecommendation]:
    return recommend_business_modules(body)


@router.post(
    "/companies/{company_id}/classification",
    response_model=BusinessClassificationRecord,
)
def classify_company(
    company_id: UUID, body: BusinessClassificationInput
) -> BusinessClassificationRecord:
    record = _classification(company_id, body)
    _CLASSIFICATIONS[company_id] = record
    _audit(
        company_id, "business.classification.generated", record.model_dump(mode="json")
    )
    return record


@router.post(
    "/companies/{company_id}/apply-recommendations",
    response_model=ModuleSettingsResponse,
)
def apply_recommendations(
    company_id: UUID, body: ApplyRecommendationsPayload
) -> ModuleSettingsResponse:
    classification = _classification(company_id, body.classification)
    _CLASSIFICATIONS[company_id] = classification
    recommendations = recommend_business_modules(body.classification)
    settings: dict[str, CompanyModuleSetting] = {}
    for recommendation in recommendations:
        settings[recommendation.module_slug] = CompanyModuleSetting(
            id=uuid4(),
            company_id=company_id,
            module_slug=recommendation.module_slug,
            title_pt_br=recommendation.title_pt_br,
            state=recommendation.state,
            visibility="hidden" if recommendation.state == "hidden" else "visible",
            source="automatic",
            recommendation_score=recommendation.score,
            recommendation_reason=recommendation.explanation_pt_br,
            dependencies=recommendation.dependencies,
            can_disable=recommendation.can_disable,
            updated_at=_now(),
            updated_by=body.actor_id,
        )
    _SETTINGS[company_id] = settings
    _audit(
        company_id,
        "business.module.recommendations_applied",
        {"modules": [item.model_dump(mode="json") for item in settings.values()]},
    )
    return ModuleSettingsResponse(
        company_id=company_id,
        classification=classification,
        modules=list(settings.values()),
        audit=_AUDIT.get(company_id, []),
    )


@router.get("/companies/{company_id}/modules", response_model=ModuleSettingsResponse)
def get_company_modules(company_id: UUID) -> ModuleSettingsResponse:
    return ModuleSettingsResponse(
        company_id=company_id,
        classification=_CLASSIFICATIONS.get(company_id),
        modules=list(_SETTINGS.get(company_id, {}).values()),
        audit=_AUDIT.get(company_id, []),
    )


@router.patch(
    "/companies/{company_id}/modules/{module_slug}", response_model=CompanyModuleSetting
)
def patch_company_module(
    company_id: UUID, module_slug: str, body: ModulePatch
) -> CompanyModuleSetting:
    settings = _SETTINGS.setdefault(company_id, {})
    current = settings.get(module_slug)
    if (
        current
        and not current.can_disable
        and body.state not in {"mandatory", "active"}
    ):
        raise HTTPException(
            status_code=409,
            detail="Modulo obrigatorio nao pode ser ocultado, desativado ou bloqueado manualmente.",
        )
    if current is None:
        current = CompanyModuleSetting(
            id=uuid4(),
            company_id=company_id,
            module_slug=module_slug,
            title_pt_br=MODULE_NAMES.get(module_slug, module_slug),
            state=body.state,
            visibility="hidden" if body.state == "hidden" else "visible",
            source="manual",
            recommendation_score=0.5,
            recommendation_reason="Configuracao manual criada sem recomendacao previa.",
            dependencies=_dependencies(module_slug),
            can_disable=module_slug not in {"identity", "business", "permissions"},
            updated_at=_now(),
            updated_by="business-shell",
        )
    updated = current.model_copy(
        update={
            "state": body.state,
            "visibility": "hidden" if body.state == "hidden" else "visible",
            "source": "manual",
            "recommendation_reason": body.reason,
            "updated_at": _now(),
            "updated_by": "business-shell",
        }
    )
    settings[module_slug] = updated
    _audit(
        company_id,
        "business.module.configuration_updated",
        updated.model_dump(mode="json"),
    )
    return updated


@router.get("/companies/{company_id}/modules/{module_slug}/change-impact")
def get_change_impact(
    company_id: UUID, module_slug: str, next_state: ModuleState = "hidden"
) -> dict[str, Any]:
    current = _SETTINGS.get(company_id, {}).get(module_slug)
    if (
        current
        and not current.can_disable
        and next_state not in {"mandatory", "active"}
    ):
        return {
            "allowed": False,
            "reason_code": "MANDATORY_MODULE",
            "explanation": "Modulo obrigatorio protege identidade, empresa, permissoes e auditoria.",
            "dependencies": current.dependencies,
        }
    return {
        "allowed": True,
        "reason_code": "MANUAL_CHANGE_ALLOWED",
        "explanation": "A alteracao preserva dados existentes e registra auditoria. Operacoes futuras obedecem ao novo estado do modulo.",
        "dependencies": _dependencies(module_slug),
        "preserved_data": True,
        "requires_audit_reason": True,
    }
