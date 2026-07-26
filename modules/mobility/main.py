"""Módulo Mobility – Primícia 10: Rota de Intenções Premium.

Serviço Premium com tarifação diferenciada configurável.
Nenhum valor fixo. Preços, franquias e impostos são configuráveis.
Nunca expor custo interno, margem ou lucro.
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from fastapi import Body, Depends, HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.feature_flags import check_premium_entitlement, is_flag_enabled
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers
from ._primicias import router as primacia_router

app = create_module_app("mobility")

_FLAG = "primicia.mobility.intention_route_premium"
_MIN_INTENTIONS = 3  # Rota combina pelo menos 3 intenções


def _store():
    return app.extra["store"]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _require_premium(actor: Actor) -> None:
    """Verifica entitlement Premium. Usuário sem direito recebe oferta clara."""
    check_premium_entitlement(
        _FLAG,
        user_id=str(actor.user_id),
        tenant_id=str(actor.business_id) if actor.business_id else None,
    )


@app.post("/intention-plans/quote", status_code=200)
async def quote_intention_plan(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Gera cotação para plano de rota de intenções Premium.

    Usuário sem entitlement recebe 402 com oferta clara.
    Exibe valor, moeda e validade da cotação.
    Nunca expor custo interno, margem ou lucro.
    """
    _require_premium(actor)

    intentions = body.get("intentions", [])
    if len(intentions) < _MIN_INTENTIONS:
        raise HTTPException(status_code=422, detail=f"Rota Premium requer pelo menos {_MIN_INTENTIONS} intenções.")

    # Tarifação via configável (sem valores fixos)
    from shared.runtime import get_config
    pricing_config_id = get_config("MOBILITY_PREMIUM_PRICING_CONFIG_ID", "default")
    per_plan_charge = get_config("MOBILITY_PREMIUM_PER_PLAN_CHARGE", None)
    tax_pct = float(get_config("MOBILITY_PREMIUM_TAX_PCT", "0"))
    currency = get_config("MOBILITY_PREMIUM_CURRENCY", "BRL")

    if per_plan_charge is None:
        raise HTTPException(status_code=503, detail="Configuração de tarifa Premium não encontrada. Contate o suporte.")

    base = float(per_plan_charge)
    tax = round(base * (tax_pct / 100), 2)
    total = round(base + tax, 2)

    from datetime import timedelta
    quote_valid_minutes = int(get_config("MOBILITY_PREMIUM_QUOTE_VALID_MINUTES", "30"))
    valid_until = (datetime.now(UTC) + timedelta(minutes=quote_valid_minutes)).isoformat()

    return {
        "pricing_config_id": pricing_config_id,
        "base_amount": base,
        "tax_amount": tax,
        "total_amount": total,
        "currency": currency,
        "valid_until": valid_until,
        "intentions_count": len(intentions),
        "plan_type": "premium",
    }


@app.post("/intention-plans", status_code=201)
async def create_intention_plan(
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Cria plano de jornada por intenções, compromissos, horários e meios."""
    _require_premium(actor)

    intentions = body.get("intentions", [])
    if len(intentions) < _MIN_INTENTIONS:
        raise HTTPException(status_code=422, detail=f"Rota Premium requer pelo menos {_MIN_INTENTIONS} intenções.")

    plan_id = str(uuid4())
    payload = {"id": plan_id, "user_id": str(actor.user_id), "title": body.get("title", "Plano Premium")[:256], "status": "draft", "premium": True, "intentions": intentions, "constraints": body.get("constraints", []), "created_at": _now(), "idempotency_key": body.get("idempotency_key")}
    try:
        return _store().create("mobility_intention_plans", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "draft", payload, str(actor.user_id), ("id",), "mobility.intention_plan.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/intention-plans/{plan_id}/confirm", status_code=200)
async def confirm_intention_plan(
    plan_id: UUID,
    body: dict[str, Any] = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict[str, Any]:
    """Confirma plano e autoriza cobrança. Cobrança ocorre UMA única vez."""
    _require_premium(actor)
    store = _store()
    try:
        plan = store.get("mobility_intention_plans", str(plan_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")

    if plan.get("status") == "confirmed":
        raise HTTPException(status_code=409, detail="Plano já confirmado. Cobrança já autorizada.")
    if plan.get("status") != "draft":
        raise HTTPException(status_code=409, detail=f"Plano em estado '{plan.get('status')}' não pode ser confirmado.")

    charge_ref = body.get("charge_authorization_ref")
    if not charge_ref:
        raise HTTPException(status_code=422, detail="charge_authorization_ref é obrigatório para confirmar o plano Premium.")

    updated = store.update(plan, {"status": "confirmed", "confirmed_at": _now(), "charge_ref": str(charge_ref)}, "confirmed", str(actor.user_id), "mobility.intention_plan.confirmed")
    store.audit_external("mobility_intention_plans", str(plan_id), str(actor.user_id), "mobility.intention_plan.charge_authorized", {"charge_ref": charge_ref})
    return updated


@app.get("/intention-plans/{plan_id}/billing")
async def get_billing(plan_id: UUID, actor: Actor = Depends(actor_from_headers)) -> dict[str, Any]:
    """Consulta histórico de cobrança do plano. Nunca expor custo interno."""
    _require_premium(actor)
    store = _store()
    try:
        plan = store.get("mobility_intention_plans", str(plan_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")
    payload = plan.get("payload", {})
    if str(actor.user_id) != str(payload.get("user_id") or plan.get("user_id")):
        raise HTTPException(status_code=403, detail="Acesso negado a este plano.")
    return {"plan_id": str(plan_id), "status": plan.get("status"), "charge_ref": payload.get("charge_ref"), "confirmed_at": payload.get("confirmed_at"), "currency": "BRL"}


@app.get("/intention-plans/feature-status")
async def feature_status() -> dict[str, Any]:
    return {"flag": _FLAG, "enabled": is_flag_enabled(_FLAG), "description": "Rota de Intenções Premium – Primícia 10", "premium": True}

app.include_router(primacia_router)