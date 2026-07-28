from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

Priority = Literal["P0", "P1", "P2"]
router = APIRouter(prefix="/innovation/round-005", tags=["valley-innovation-round-005"])


class Idea(BaseModel):
    idea_id: int
    code: str
    module: str
    title: str
    priority: Priority
    feature_flag: str


class ActionRequest(BaseModel):
    owner_id: UUID
    action: str = Field(min_length=2, max_length=80)
    payload: dict[str, Any] = Field(default_factory=dict)


class FlagUpdate(BaseModel):
    enabled: bool
    rollout_stage: Literal["contract_ready", "pilot", "production"] = "contract_ready"


_RAW_IDEAS = [
    (1, "identity", "Chave de Recuperação por Rede de Confiança", "P0"),
    (2, "business", "Vitrine de Compromissos Verificáveis", "P1"),
    (3, "permissions", "Modo Privacidade em Viagem", "P1"),
    (4, "finance", "Recibo Financeiro Explicável", "P0"),
    (5, "marketplace", "Compra com Critério Ético Configurável", "P1"),
    (6, "stock", "Garantia de Compatibilidade Reversa", "P0"),
    (7, "delivery", "Entrega por Missão Encadeada", "P1"),
    (8, "riders", "Mapa de Pausas e Apoio", "P1"),
    (9, "services", "Diagnóstico Colaborativo com Limite", "P1"),
    (10, "mobility", "Companheiro de Embarque Acessível", "P1"),
    (11, "jobs", "Portfólio de Decisões Profissionais", "P1"),
    (12, "erp", "Simulador de Consequência Operacional", "P1"),
    (13, "wms", "Reserva Doméstica para Emergências Cotidianas", "P2"),
    (14, "tms", "Rota por Janela de Impacto Urbano", "P2"),
    (15, "crm", "Canal de Reconciliação após Falha", "P1"),
    (16, "bpm", "Processo com Saída Segura", "P0"),
    (17, "document", "Cofre de Originais com Cópias Sanitizadas", "P0"),
    (18, "hr", "Banco de Tempo de Aprendizagem", "P1"),
    (19, "health", "Janela de Compartilhamento Clínico ao Vivo", "P0"),
    (20, "legal", "Consentimento Negociável por Finalidade", "P0"),
    (21, "property", "Mapa de Convivência do Condomínio", "P2"),
    (22, "bi", "Painel de Valor Entregue ao Usuário", "P1"),
    (23, "ai_core", "Memória com Data de Validade Semântica", "P0"),
    (24, "api_hub", "Contrato de Dados Testável pelo Usuário", "P1"),
]

IDEAS = {
    idea_id: Idea(
        idea_id=idea_id,
        code=f"VLY-20260728-{idea_id:02d}",
        module=module,
        title=title,
        priority=priority,
        feature_flag=f"VALLEY_ROUND_005_{module.upper()}_{idea_id:02d}",
    )
    for idea_id, module, title, priority in _RAW_IDEAS
}

FLAGS: dict[int, dict[str, Any]] = {
    idea_id: {"enabled": False, "rollout_stage": "contract_ready"}
    for idea_id in IDEAS
}
RECORDS: dict[int, list[dict[str, Any]]] = {idea_id: [] for idea_id in IDEAS}


def _now() -> datetime:
    return datetime.now(UTC)


def _idea(idea_id: int) -> Idea:
    idea = IDEAS.get(idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
    return idea


def _require_write(idea_id: int, sandbox: bool) -> Idea:
    idea = _idea(idea_id)
    if not sandbox and not FLAGS[idea_id]["enabled"]:
        raise HTTPException(
            status_code=409,
            detail="Feature flag desligada. Use sandbox autorizado ou habilite a ideia após homologação.",
        )
    return idea


def _require(payload: dict[str, Any], *fields: str) -> None:
    missing = [field for field in fields if payload.get(field) in (None, "", [])]
    if missing:
        raise HTTPException(status_code=422, detail=f"Campos obrigatórios ausentes: {', '.join(missing)}.")


def _decimal(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"{field} deve ser numérico.") from exc
    if result < 0:
        raise HTTPException(status_code=422, detail=f"{field} não pode ser negativo.")
    return result


def _future(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise HTTPException(status_code=422, detail=f"{field} deve usar data ISO 8601.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"{field} inválido.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    if parsed <= _now():
        raise HTTPException(status_code=422, detail=f"{field} deve estar no futuro.")
    return parsed


def _validate(idea_id: int, action: str, payload: dict[str, Any]) -> dict[str, Any]:
    if idea_id == 1:
        _require(payload, "guardian_ids", "quorum")
        guardians = list(dict.fromkeys(payload["guardian_ids"]))
        quorum = int(payload["quorum"])
        if len(guardians) < 2 or quorum < 2 or quorum > len(guardians):
            raise HTTPException(status_code=422, detail="Rede de confiança exige ao menos dois guardiões e quórum válido.")
        return {"guardian_count": len(guardians), "quorum": quorum, "content_exposed": False}
    if idea_id == 2:
        _require(payload, "statement", "metric", "valid_until")
        return {"status": "pending_evidence_review", "valid_until": _future(payload["valid_until"], "valid_until")}
    if idea_id == 3:
        _require(payload, "starts_at", "ends_at")
        starts = datetime.fromisoformat(str(payload["starts_at"]).replace("Z", "+00:00"))
        ends = datetime.fromisoformat(str(payload["ends_at"]).replace("Z", "+00:00"))
        if ends <= starts:
            raise HTTPException(status_code=422, detail="A viagem deve terminar após o início.")
        return {"status": "scheduled", "auto_expire": True, "exact_location_required": False}
    if idea_id == 4:
        _require(payload, "total_brl", "beneficiaries")
        total = _decimal(payload["total_brl"], "total_brl")
        parts = sum((_decimal(item.get("amount_brl", 0), "amount_brl") for item in payload["beneficiaries"]), Decimal("0"))
        if parts != total:
            raise HTTPException(status_code=422, detail="A soma dos beneficiários deve ser igual ao total do recibo.")
        return {"status": "explained", "total_brl": total, "timeline_enabled": True}
    if idea_id == 5:
        _require(payload, "criteria", "offers")
        criteria = payload["criteria"]
        offers = payload["offers"]
        ranked = sorted(offers, key=lambda offer: sum(float(offer.get(c, 0)) for c in criteria), reverse=True)
        return {"ranking_controlled_by_user": True, "criteria": criteria, "ranked_offers": ranked}
    if idea_id == 6:
        _require(payload, "owned_model", "candidate_model", "rules")
        failed = [rule for rule in payload["rules"] if rule.get("required") and not rule.get("matched")]
        return {"compatible": not failed, "failed_rules": failed, "manual_review": bool(payload.get("uncertain"))}
    if idea_id == 7:
        _require(payload, "steps")
        steps = payload["steps"]
        if len(steps) < 2:
            raise HTTPException(status_code=422, detail="A missão encadeada exige pelo menos duas etapas.")
        return {"status": "planned", "step_count": len(steps), "proof_required_each_step": True}
    if idea_id == 8:
        _require(payload, "name", "services", "latitude", "longitude")
        return {"status": "pending_verification", "continuous_rider_tracking": False}
    if idea_id == 9:
        _require(payload, "evidence", "category")
        opinions = payload.get("opinions", [])
        if len(opinions) > 3:
            raise HTTPException(status_code=422, detail="O diagnóstico colaborativo aceita no máximo três opiniões.")
        return {"status": "triage_open", "opinion_count": len(opinions), "productive_work_allowed": False}
    if idea_id == 10:
        _require(payload, "stop_id", "vehicle_id", "accessibility_mode")
        return {"status": "boarding_guidance_ready", "fallback_offline": True, "operator_data_verified": False}
    if idea_id == 11:
        _require(payload, "context", "decision", "learning")
        return {"status": "draft", "shared_by_default": False, "productive_work": False}
    if idea_id == 12:
        _require(payload, "scenario", "assumptions")
        return {"status": "simulated", "not_a_forecast_guarantee": True, "affected_modules": payload.get("affected_modules", [])}
    if idea_id == 13:
        _require(payload, "item", "minimum_quantity", "current_quantity")
        minimum = _decimal(payload["minimum_quantity"], "minimum_quantity")
        current = _decimal(payload["current_quantity"], "current_quantity")
        return {"below_reserve": current < minimum, "automatic_purchase": False}
    if idea_id == 14:
        _require(payload, "routes", "impact_weights")
        routes = payload["routes"]
        weights = payload["impact_weights"]

        def score(route: dict[str, Any]) -> float:
            return sum(float(route.get(key, 0)) * float(weight) for key, weight in weights.items())

        return {"ranked_routes": sorted(routes, key=score), "multiobjective": True}
    if idea_id == 15:
        _require(payload, "incident", "facts", "proposed_remedies")
        return {"status": "awaiting_user_decision", "legal_admission": False, "remedies": payload["proposed_remedies"]}
    if idea_id == 16:
        _require(payload, "process_type", "preserved_fields", "retention_reason")
        return {"status": "exit_prepared", "export_available": bool(payload.get("export_requested", True)), "receipt_required": True}
    if idea_id == 17:
        _require(payload, "document_id", "purpose", "hidden_fields", "expires_at")
        expires = _future(payload["expires_at"], "expires_at")
        return {"status": "sanitization_requested", "expires_at": expires, "original_untouched": True, "manual_review_required": True}
    if idea_id == 18:
        _require(payload, "employee_id", "hours", "learning_goal")
        hours = _decimal(payload["hours"], "hours")
        if hours <= 0:
            raise HTTPException(status_code=422, detail="A reserva de aprendizagem deve ser positiva.")
        return {"status": "allocated", "hours": hours, "outside_personal_time": False}
    if idea_id == 19:
        _require(payload, "professional_id", "data_types", "starts_at", "ends_at")
        starts = datetime.fromisoformat(str(payload["starts_at"]).replace("Z", "+00:00"))
        ends = datetime.fromisoformat(str(payload["ends_at"]).replace("Z", "+00:00"))
        if ends <= starts:
            raise HTTPException(status_code=422, detail="A janela clínica deve terminar após o início.")
        return {"status": "scheduled", "temporary": True, "clinical_interpretation_performed": False}
    if idea_id == 20:
        _require(payload, "purposes")
        purposes = payload["purposes"]
        rejected_required = [item for item in purposes if item.get("required") and not item.get("accepted")]
        if rejected_required:
            raise HTTPException(status_code=422, detail="Finalidades obrigatórias precisam ser aceitas ou o fluxo deve ser encerrado.")
        return {"accepted_optional": [p.get("id") for p in purposes if not p.get("required") and p.get("accepted")], "modular": True}
    if idea_id == 21:
        _require(payload, "property_id", "area", "starts_at", "ends_at")
        return {"status": "scheduled", "individual_routine_exposed": False, "moderation_required": True}
    if idea_id == 22:
        _require(payload, "kind", "amount", "unit", "methodology")
        return {"status": "recorded", "contestable": True, "methodology_visible": True}
    if idea_id == 23:
        _require(payload, "memory_type", "content", "confirmed_at")
        ttl = int(payload.get("ttl_days", {"address": 90, "preference": 365, "goal": 30, "health_statement": 30}.get(payload["memory_type"], 60)))
        confirmed = datetime.fromisoformat(str(payload["confirmed_at"]).replace("Z", "+00:00"))
        if confirmed.tzinfo is None:
            confirmed = confirmed.replace(tzinfo=UTC)
        expires = confirmed + timedelta(days=ttl)
        return {"status": "fresh" if expires > _now() else "stale", "expires_at": expires, "requires_confirmation": expires <= _now()}
    if idea_id == 24:
        _require(payload, "scopes", "outbound_fields", "inbound_fields", "retention_days")
        if payload.get("synthetic_only") is not True:
            raise HTTPException(status_code=422, detail="O contrato testável exige dados sintéticos.")
        return {"status": "simulation_completed", "external_call_performed": False, "steps": ["authorize", "send", "receive", "retain"]}
    raise HTTPException(status_code=500, detail=f"Regra não implementada para a ideia {idea_id} e ação {action}.")


@router.get("")
def list_ideas() -> dict[str, Any]:
    ideas = [IDEAS[index] for index in sorted(IDEAS)]
    return {
        "round": 5,
        "approved": 24,
        "p0": [idea.idea_id for idea in ideas if idea.priority == "P0"],
        "feature_flags_enabled": [idea_id for idea_id, state in FLAGS.items() if state["enabled"]],
        "ideas": ideas,
    }


@router.get("/flags")
def list_flags() -> dict[int, dict[str, Any]]:
    return FLAGS


@router.put("/flags/{idea_id}")
def update_flag(idea_id: int, body: FlagUpdate) -> dict[str, Any]:
    _idea(idea_id)
    if body.rollout_stage == "production" and body.enabled:
        raise HTTPException(status_code=409, detail="Habilitação de produção exige homologação externa e não pode ocorrer por esta rota.")
    FLAGS[idea_id] = body.model_dump()
    return {"idea_id": idea_id, **FLAGS[idea_id]}


@router.get("/{idea_id}")
def get_idea(idea_id: int) -> Idea:
    return _idea(idea_id)


@router.post("/{idea_id}/execute", status_code=201)
def execute_idea(
    idea_id: int,
    body: ActionRequest,
    sandbox: bool = Header(default=False, alias="X-Innovation-Sandbox"),
) -> dict[str, Any]:
    idea = _require_write(idea_id, sandbox)
    result = _validate(idea_id, body.action, body.payload)
    record = {
        "id": uuid4(),
        "idea_id": idea_id,
        "code": idea.code,
        "module": idea.module,
        "owner_id": body.owner_id,
        "action": body.action,
        "payload": body.payload,
        "result": result,
        "sandbox": sandbox,
        "created_at": _now(),
    }
    RECORDS[idea_id].append(record)
    return record


@router.get("/{idea_id}/records")
def list_records(idea_id: int) -> list[dict[str, Any]]:
    _idea(idea_id)
    return RECORDS[idea_id]
