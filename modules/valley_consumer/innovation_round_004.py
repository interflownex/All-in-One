from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

DecisionState = Literal["approved", "approved_p0", "rejected"]
CoverageState = Literal["full", "partial", "not_eligible"]
PaymentMethod = Literal["nfc", "qr_code", "account_credit", "cash", "other"]

router = APIRouter(prefix="/innovation/round-004", tags=["valley-innovation-round-004"])


class IdeaDecision(BaseModel):
    idea_id: int
    code: str
    module: str
    title: str
    decision: DecisionState
    target_module: str
    priority: Literal["P0", "P1", "P2", "blocked"]
    implementation_notes: list[str] = Field(default_factory=list)


IDEAS: dict[int, IdeaDecision] = {
    1: IdeaDecision(idea_id=1, code="VLY-20260727-01", module="identity", title="Carteira de Contextos Isolados", decision="approved", target_module="identity", priority="P1"),
    2: IdeaDecision(idea_id=2, code="VLY-20260727-02", module="business", title="Atendimento Adaptado sem Diagnóstico", decision="approved", target_module="business", priority="P1"),
    3: IdeaDecision(idea_id=3, code="VLY-20260727-03", module="permissions", title="Orçamento Pessoal de Dados", decision="approved", target_module="permissions", priority="P1"),
    4: IdeaDecision(idea_id=4, code="VLY-20260727-04", module="finance", title="Cofre de Objetivo Compartilhado por Regras", decision="approved", target_module="finance", priority="P1"),
    5: IdeaDecision(idea_id=5, code="VLY-20260727-05", module="marketplace", title="Conserte, Alugue ou Compre", decision="approved_p0", target_module="marketplace", priority="P0", implementation_notes=["Prioridade máxima da rodada.", "Comparar reparo, aluguel, recondicionado e compra nova por custo total, prazo e garantia."]),
    6: IdeaDecision(idea_id=6, code="VLY-20260727-06", module="stock", title="Bolsa Segura de Sobras Produtivas", decision="approved", target_module="marketplace", priority="P1", implementation_notes=["Implantar no Marketplace, não no módulo STOCK.", "Bloquear materiais perigosos, contaminados ou regulados."]),
    7: IdeaDecision(idea_id=7, code="VLY-20260727-07", module="delivery", title="Ponto Móvel de Encontro Seguro", decision="approved", target_module="delivery", priority="P1"),
    8: IdeaDecision(idea_id=8, code="VLY-20260727-08", module="riders", title="Rider Mentor em Modo Sombra", decision="approved", target_module="riders", priority="P1"),
    9: IdeaDecision(idea_id=9, code="VLY-20260727-09", module="services", title="Contrato por Resultado Medido", decision="approved", target_module="services", priority="P1", implementation_notes=["Definir prazo máximo de validação.", "Após o prazo, liberar o pagamento se o cliente não apresentar evidência suficiente de falha.", "Preservar direito do cliente ao serviço e do profissional ao pagamento."]),
    10: IdeaDecision(idea_id=10, code="VLY-20260727-10", module="mobility", title="Crédito de Contingência Multimodal", decision="approved", target_module="mobility", priority="P1", implementation_notes=["Ativar somente onde houver API operacional e método de pagamento compatível.", "Publicar abrangência real, ainda que parcial, sem alegar cobertura nacional sem evidência."]),
    11: IdeaDecision(idea_id=11, code="VLY-20260727-11", module="jobs", title="Prévia Realista da Vaga", decision="approved", target_module="jobs", priority="P1", implementation_notes=["Programa opt-in para empresas.", "Não pode ser obrigatório nem usado como trabalho produtivo gratuito."]),
    12: IdeaDecision(idea_id=12, code="VLY-20260727-12", module="erp", title="Modo Continuidade do Pequeno Negócio", decision="approved", target_module="erp", priority="P1"),
    13: IdeaDecision(idea_id=13, code="VLY-20260727-13", module="wms", title="Despensa Valley Doméstica e Lista de Compras", decision="approved", target_module="wms", priority="P1", implementation_notes=["Incluir lista contínua de compras.", "Sugerir revisão da lista quando houver saldo disponível ou data de compra.", "Marcar automaticamente itens comprados após confirmação da transação."]),
    14: IdeaDecision(idea_id=14, code="VLY-20260727-14", module="tms", title="Cadeia de Custódia Sensorial", decision="rejected", target_module="tms", priority="blocked", implementation_notes=["Não implantar nesta rodada."]),
    15: IdeaDecision(idea_id=15, code="VLY-20260727-15", module="crm", title="CRM por Intenção Declarada", decision="approved", target_module="crm", priority="P1"),
    16: IdeaDecision(idea_id=16, code="VLY-20260727-16", module="bpm", title="Pausa Humana Obrigatória", decision="approved", target_module="bpm", priority="P1"),
    17: IdeaDecision(idea_id=17, code="VLY-20260727-17", module="document", title="Documento em Áudio Navegável e Verificável", decision="approved", target_module="document", priority="P1"),
    18: IdeaDecision(idea_id=18, code="VLY-20260727-18", module="hr", title="Mapa Transparente de Crescimento", decision="approved", target_module="hr", priority="P1"),
    19: IdeaDecision(idea_id=19, code="VLY-20260727-19", module="health", title="Acompanhamento Pós-Consulta e Agenda de Medicação", decision="approved", target_module="health", priority="P1", implementation_notes=["Gerar agenda somente a partir de prescrição registrada.", "O usuário confirma cada dose; o aplicativo não diagnostica nem altera a prescrição."]),
    20: IdeaDecision(idea_id=20, code="VLY-20260727-20", module="legal", title="Jornada Guiada de Direito do Consumidor", decision="approved", target_module="legal", priority="P1"),
    21: IdeaDecision(idea_id=21, code="VLY-20260727-21", module="property", title="Manual Portátil da Casa", decision="approved", target_module="property", priority="P1"),
    22: IdeaDecision(idea_id=22, code="VLY-20260727-22", module="bi", title="Índice de Fricção do Usuário", decision="approved", target_module="bi", priority="P1"),
    23: IdeaDecision(idea_id=23, code="VLY-20260727-23", module="ai_core", title="Orçamento de Autonomia da Helena", decision="approved", target_module="ai_core", priority="P1"),
    24: IdeaDecision(idea_id=24, code="VLY-20260727-24", module="api_hub", title="Malha Offline de Continuidade", decision="approved", target_module="api_hub", priority="P1"),
}


class CapabilityRecordInput(BaseModel):
    owner_id: UUID
    payload: dict[str, Any] = Field(default_factory=dict)


class CapabilityRecord(BaseModel):
    id: UUID
    idea_id: int
    target_module: str
    owner_id: UUID
    payload: dict[str, Any]
    created_at: datetime


class MarketplaceSolutionRequest(BaseModel):
    user_id: UUID
    need: str = Field(min_length=3, max_length=300)
    usage_days: int = Field(ge=1, le=3650)
    budget_brl: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    accepted_modes: list[Literal["repair", "rent", "borrow", "reconditioned", "buy_new"]] = Field(min_length=1)


class ProductiveSurplusCreate(BaseModel):
    seller_id: UUID
    title: str = Field(min_length=3, max_length=200)
    category: Literal["clean_wood", "cardboard", "clean_packaging", "non_hazardous_component", "other_reviewed"]
    quantity: Decimal = Field(gt=0)
    unit: str = Field(min_length=1, max_length=32)
    condition: str = Field(min_length=3, max_length=300)
    evidence_urls: list[str] = Field(default_factory=list, max_length=10)
    regulated_or_hazardous: bool = False


class ServiceOutcomeContractCreate(BaseModel):
    client_id: UUID
    professional_id: UUID
    service_description: str = Field(min_length=5, max_length=500)
    expected_result: str = Field(min_length=5, max_length=500)
    amount_brl: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    max_validation_hours: int = Field(default=72, ge=1, le=720)


class ServiceValidationInput(BaseModel):
    actor: Literal["client", "professional", "system"]
    accepted: bool | None = None
    evidence: list[str] = Field(default_factory=list, max_length=20)
    reason: str | None = Field(default=None, max_length=1000)
    evaluated_at: datetime | None = None


class MobilityProviderCreate(BaseModel):
    provider_name: str = Field(min_length=2, max_length=200)
    state_code: str = Field(min_length=2, max_length=2)
    cities: list[str] = Field(min_length=1)
    transport_modes: list[Literal["bus", "metro", "train", "ferry", "other"]] = Field(min_length=1)
    realtime_api_available: bool
    ticketing_api_available: bool
    payment_methods: list[PaymentMethod] = Field(default_factory=list)
    production_verified: bool = False
    evidence_urls: list[str] = Field(default_factory=list)


class JobsPilotCompanyCreate(BaseModel):
    company_id: UUID
    opted_in: bool
    vacancies: list[UUID] = Field(default_factory=list)
    consent_text_version: str = Field(min_length=1, max_length=40)


class ShoppingItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    quantity: Decimal = Field(default=Decimal("1"), gt=0)
    estimated_price_brl: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    desired_by: datetime | None = None


class ShoppingListCreate(BaseModel):
    user_id: UUID
    items: list[ShoppingItemCreate] = Field(default_factory=list)


class ShoppingSuggestionRequest(BaseModel):
    available_balance_brl: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    evaluated_at: datetime | None = None


class ShoppingPurchaseConfirmation(BaseModel):
    purchased_item_names: list[str] = Field(min_length=1)
    transaction_id: str = Field(min_length=3, max_length=120)


class MedicationPrescriptionCreate(BaseModel):
    patient_id: UUID
    prescription_id: str = Field(min_length=3, max_length=120)
    medication_name: str = Field(min_length=2, max_length=200)
    interval_hours: int = Field(ge=1, le=168)
    duration_days: int = Field(ge=1, le=90)
    first_dose_at: datetime
    prescribed_by: str = Field(min_length=3, max_length=200)
    prescription_verified: bool


class DoseConfirmation(BaseModel):
    taken: bool
    confirmed_at: datetime | None = None


class AutonomyBudgetCreate(BaseModel):
    user_id: UUID
    module: str = Field(min_length=2, max_length=80)
    action: str = Field(min_length=2, max_length=120)
    level: Literal["suggest", "prepare", "execute"]
    max_amount_brl: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    valid_until: datetime | None = None


class OfflineEventCreate(BaseModel):
    device_id: str = Field(min_length=3, max_length=160)
    module: str = Field(min_length=2, max_length=80)
    event_type: str = Field(min_length=3, max_length=160)
    idempotency_key: str = Field(min_length=3, max_length=160)
    payload: dict[str, Any] = Field(default_factory=dict)
    expires_at: datetime
    signature: str = Field(min_length=8, max_length=512)


_CAPABILITY_RECORDS: dict[UUID, CapabilityRecord] = {}
_SURPLUSES: dict[UUID, dict[str, Any]] = {}
_SERVICE_CONTRACTS: dict[UUID, dict[str, Any]] = {}
_MOBILITY_PROVIDERS: dict[UUID, dict[str, Any]] = {}
_JOBS_PILOTS: dict[UUID, dict[str, Any]] = {}
_SHOPPING_LISTS: dict[UUID, dict[str, Any]] = {}
_MEDICATION_PLANS: dict[UUID, dict[str, Any]] = {}
_AUTONOMY_BUDGETS: dict[UUID, dict[str, Any]] = {}
_OFFLINE_EVENTS: dict[str, dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(UTC)


def _approved_idea(idea_id: int) -> IdeaDecision:
    idea = IDEAS.get(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
    if idea.decision == "rejected":
        raise HTTPException(status_code=409, detail="Ideia bloqueada por decisão do aprovador.")
    return idea


@router.get("")
def list_ideas() -> dict[str, Any]:
    ordered = [IDEAS[index] for index in sorted(IDEAS)]
    return {
        "round": 4,
        "approved": sum(idea.decision != "rejected" for idea in ordered),
        "rejected": sum(idea.decision == "rejected" for idea in ordered),
        "p0": [idea.idea_id for idea in ordered if idea.priority == "P0"],
        "ideas": ordered,
    }


@router.get("/{idea_id}")
def get_idea(idea_id: int) -> IdeaDecision:
    idea = IDEAS.get(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
    return idea


@router.post("/{idea_id}/records", status_code=201)
def create_capability_record(idea_id: int, body: CapabilityRecordInput) -> CapabilityRecord:
    idea = _approved_idea(idea_id)
    record = CapabilityRecord(
        id=uuid4(),
        idea_id=idea_id,
        target_module=idea.target_module,
        owner_id=body.owner_id,
        payload=body.payload,
        created_at=_now(),
    )
    _CAPABILITY_RECORDS[record.id] = record
    return record


@router.post("/marketplace/solution-options", status_code=201)
def marketplace_solution_options(body: MarketplaceSolutionRequest) -> dict[str, Any]:
    _approved_idea(5)
    order = {"repair": 0, "rent": 1, "borrow": 2, "reconditioned": 3, "buy_new": 4}
    options = [
        {
            "mode": mode,
            "eligible": True,
            "ranking_basis": ["total_cost", "availability", "warranty", "declared_usage_period"],
        }
        for mode in sorted(set(body.accepted_modes), key=order.get)
    ]
    return {
        "priority": "P0",
        "user_id": body.user_id,
        "need": body.need,
        "usage_days": body.usage_days,
        "budget_brl": body.budget_brl,
        "options": options,
    }


@router.post("/marketplace/productive-surpluses", status_code=201)
def create_productive_surplus(body: ProductiveSurplusCreate) -> dict[str, Any]:
    idea = _approved_idea(6)
    if idea.target_module != "marketplace":
        raise HTTPException(status_code=500, detail="Destino inválido para a ideia 6.")
    if body.regulated_or_hazardous:
        raise HTTPException(status_code=422, detail="Material perigoso ou regulado não pode ser publicado.")
    surplus_id = uuid4()
    row = {"id": surplus_id, **body.model_dump(), "status": "pending_safety_review", "module": "marketplace", "created_at": _now()}
    _SURPLUSES[surplus_id] = row
    return row


@router.post("/services/outcome-contracts", status_code=201)
def create_service_outcome_contract(body: ServiceOutcomeContractCreate) -> dict[str, Any]:
    _approved_idea(9)
    created_at = _now()
    contract_id = uuid4()
    row = {
        "id": contract_id,
        **body.model_dump(),
        "status": "awaiting_service_delivery",
        "created_at": created_at,
        "delivered_at": None,
        "validation_deadline_at": None,
        "client_evidence": [],
        "professional_evidence": [],
        "payment_status": "escrowed",
    }
    _SERVICE_CONTRACTS[contract_id] = row
    return row


@router.post("/services/outcome-contracts/{contract_id}/mark-delivered")
def mark_service_delivered(contract_id: UUID, body: ServiceValidationInput) -> dict[str, Any]:
    contract = _SERVICE_CONTRACTS.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    if body.actor != "professional":
        raise HTTPException(status_code=403, detail="Somente o profissional pode marcar a entrega.")
    delivered_at = body.evaluated_at or _now()
    contract.update(
        status="awaiting_client_validation",
        delivered_at=delivered_at,
        validation_deadline_at=delivered_at + timedelta(hours=contract["max_validation_hours"]),
        professional_evidence=body.evidence,
    )
    return contract


@router.post("/services/outcome-contracts/{contract_id}/validate")
def validate_service_outcome(contract_id: UUID, body: ServiceValidationInput) -> dict[str, Any]:
    contract = _SERVICE_CONTRACTS.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado.")
    if contract["status"] not in {"awaiting_client_validation", "under_review"}:
        raise HTTPException(status_code=409, detail="Contrato não está em validação.")
    evaluated_at = body.evaluated_at or _now()
    deadline = contract["validation_deadline_at"]

    if body.actor == "client" and body.accepted is True:
        contract.update(status="completed", payment_status="released_to_professional", resolved_at=evaluated_at)
        return contract

    if body.actor == "client" and body.accepted is False:
        contract["client_evidence"] = body.evidence
        contract["client_reason"] = body.reason
        if body.evidence:
            contract.update(status="under_review", payment_status="escrowed")
        elif evaluated_at >= deadline:
            contract.update(status="completed", payment_status="released_to_professional", resolution="deadline_elapsed_without_client_proof", resolved_at=evaluated_at)
        else:
            contract.update(status="awaiting_client_validation", payment_status="escrowed", resolution="rejection_without_evidence_pending_deadline")
        return contract

    if body.actor == "system":
        if evaluated_at < deadline:
            raise HTTPException(status_code=409, detail="Prazo máximo de validação ainda não expirou.")
        if contract["client_evidence"]:
            contract.update(status="under_review", payment_status="escrowed", resolution="client_evidence_requires_review")
        else:
            contract.update(status="completed", payment_status="released_to_professional", resolution="automatic_release_after_deadline", resolved_at=evaluated_at)
        return contract

    raise HTTPException(status_code=422, detail="Validação inválida para o ator informado.")


@router.post("/mobility/providers", status_code=201)
def register_mobility_provider(body: MobilityProviderCreate) -> dict[str, Any]:
    _approved_idea(10)
    provider_id = uuid4()
    supports_digital_fare = any(method in {"nfc", "qr_code", "account_credit"} for method in body.payment_methods)
    api_ready = body.realtime_api_available and body.ticketing_api_available
    if body.production_verified and api_ready and supports_digital_fare:
        coverage: CoverageState = "full"
    elif body.realtime_api_available or body.ticketing_api_available or supports_digital_fare:
        coverage = "partial"
    else:
        coverage = "not_eligible"
    row = {"id": provider_id, **body.model_dump(), "coverage": coverage, "created_at": _now()}
    _MOBILITY_PROVIDERS[provider_id] = row
    return row


@router.get("/mobility/coverage")
def mobility_coverage(state_code: str | None = Query(default=None, min_length=2, max_length=2)) -> dict[str, Any]:
    providers = list(_MOBILITY_PROVIDERS.values())
    if state_code:
        providers = [item for item in providers if item["state_code"].casefold() == state_code.casefold()]
    eligible = [item for item in providers if item["coverage"] in {"full", "partial"}]
    return {
        "national_claim_allowed": False,
        "coverage_policy": "Somente publicar localidades com integração e pagamento comprovados.",
        "providers": eligible,
    }


@router.post("/jobs/pilot-companies", status_code=201)
def register_jobs_pilot_company(body: JobsPilotCompanyCreate) -> dict[str, Any]:
    _approved_idea(11)
    if not body.opted_in:
        raise HTTPException(status_code=422, detail="A participação no piloto exige adesão voluntária da empresa.")
    row = {"id": uuid4(), **body.model_dump(), "status": "pilot_opted_in", "created_at": _now()}
    _JOBS_PILOTS[body.company_id] = row
    return row


@router.post("/shopping-lists", status_code=201)
def create_shopping_list(body: ShoppingListCreate) -> dict[str, Any]:
    _approved_idea(13)
    row = {
        "id": uuid4(),
        "user_id": body.user_id,
        "items": [{**item.model_dump(), "status": "pending"} for item in body.items],
        "created_at": _now(),
        "updated_at": _now(),
    }
    _SHOPPING_LISTS[body.user_id] = row
    return row


@router.post("/shopping-lists/{user_id}/items")
def add_shopping_item(user_id: UUID, body: ShoppingItemCreate) -> dict[str, Any]:
    shopping_list = _SHOPPING_LISTS.get(user_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    shopping_list["items"].append({**body.model_dump(), "status": "pending"})
    shopping_list["updated_at"] = _now()
    return shopping_list


@router.post("/shopping-lists/{user_id}/suggest")
def suggest_shopping_list(user_id: UUID, body: ShoppingSuggestionRequest) -> dict[str, Any]:
    shopping_list = _SHOPPING_LISTS.get(user_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    evaluated_at = body.evaluated_at or _now()
    pending = [item for item in shopping_list["items"] if item["status"] == "pending"]
    due = [item for item in pending if item["desired_by"] is None or item["desired_by"] <= evaluated_at]
    total = sum((item["estimated_price_brl"] * item["quantity"] for item in due), Decimal("0"))
    return {
        "should_suggest_review": bool(due) and body.available_balance_brl > 0,
        "estimated_total_brl": total,
        "fits_available_balance": total <= body.available_balance_brl,
        "items": due,
        "message": "Você tem itens pendentes na sua lista de compras. Deseja revisar antes de concluir as compras do mês?" if due else None,
    }


@router.post("/shopping-lists/{user_id}/confirm-purchase")
def confirm_shopping_purchase(user_id: UUID, body: ShoppingPurchaseConfirmation) -> dict[str, Any]:
    shopping_list = _SHOPPING_LISTS.get(user_id)
    if not shopping_list:
        raise HTTPException(status_code=404, detail="Lista de compras não encontrada.")
    names = {name.casefold() for name in body.purchased_item_names}
    matched = 0
    for item in shopping_list["items"]:
        if item["status"] == "pending" and item["name"].casefold() in names:
            item.update(status="purchased", transaction_id=body.transaction_id, purchased_at=_now())
            matched += 1
    shopping_list["updated_at"] = _now()
    return {"matched_items": matched, "shopping_list": shopping_list}


@router.post("/health/medication-plans", status_code=201)
def create_medication_plan(body: MedicationPrescriptionCreate) -> dict[str, Any]:
    _approved_idea(19)
    if not body.prescription_verified:
        raise HTTPException(status_code=422, detail="A agenda exige prescrição verificada e registrada.")
    first = body.first_dose_at
    if first.tzinfo is None:
        first = first.replace(tzinfo=UTC)
    max_end = first + timedelta(days=body.duration_days)
    doses: list[dict[str, Any]] = []
    cursor = first
    while cursor < max_end and len(doses) < 1000:
        doses.append({"id": uuid4(), "scheduled_at": cursor, "status": "pending", "confirmed_at": None})
        cursor += timedelta(hours=body.interval_hours)
    plan_id = uuid4()
    row = {
        "id": plan_id,
        **body.model_dump(exclude={"first_dose_at"}),
        "first_dose_at": first,
        "doses": doses,
        "clinical_notice": "Agenda operacional baseada na prescrição registrada; não altera dose, intervalo ou duração.",
        "created_at": _now(),
    }
    _MEDICATION_PLANS[plan_id] = row
    return row


@router.post("/health/medication-plans/{plan_id}/doses/{dose_id}/confirm")
def confirm_medication_dose(plan_id: UUID, dose_id: UUID, body: DoseConfirmation) -> dict[str, Any]:
    plan = _MEDICATION_PLANS.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano de medicação não encontrado.")
    for dose in plan["doses"]:
        if dose["id"] == dose_id:
            dose.update(status="taken" if body.taken else "not_taken", confirmed_at=body.confirmed_at or _now())
            return dose
    raise HTTPException(status_code=404, detail="Dose não encontrada.")


@router.post("/ai/autonomy-budgets", status_code=201)
def create_autonomy_budget(body: AutonomyBudgetCreate) -> dict[str, Any]:
    _approved_idea(23)
    budget_id = uuid4()
    row = {"id": budget_id, **body.model_dump(), "revoked": False, "created_at": _now()}
    _AUTONOMY_BUDGETS[budget_id] = row
    return row


@router.post("/offline/events", status_code=201)
def enqueue_offline_event(body: OfflineEventCreate) -> dict[str, Any]:
    _approved_idea(24)
    now = _now()
    expires_at = body.expires_at if body.expires_at.tzinfo else body.expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise HTTPException(status_code=422, detail="Evento offline expirado.")
    existing = _OFFLINE_EVENTS.get(body.idempotency_key)
    if existing:
        return {**existing, "deduplicated": True}
    row = {
        "id": uuid4(),
        **body.model_dump(exclude={"expires_at"}),
        "expires_at": expires_at,
        "status": "queued_for_reconciliation",
        "deduplicated": False,
        "created_at": now,
    }
    _OFFLINE_EVENTS[body.idempotency_key] = row
    return row
