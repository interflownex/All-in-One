import sys
from pathlib import Path

from fastapi import Body, Depends, HTTPException, Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from finance_models import EscrowRequest, PixRequest, TransferRequest
from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers, demand_active_business

app = create_module_app("finance")


@app.post("/transfers", status_code=201)
async def transfer(body: TransferRequest, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]

    if str(body.source_wallet_id) == str(body.destination_wallet_id):
        raise HTTPException(
            status_code=422,
            detail="Carteiras de origem e destino devem ser diferentes.",
        )

    if not body.destination_wallet_id:
        raise HTTPException(
            status_code=422,
            detail="destination_wallet_id e obrigatorio neste baseline.",
        )

    try:
        result = store.execute_transfer(
            str(actor.user_id),
            str(body.source_wallet_id),
            str(body.destination_wallet_id),
            body.amount,
            body.currency,
            body.description,
            body.idempotency_key,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro interno na transacao: {exc}")


@app.post("/pix/out", status_code=201)
async def pix_out(body: PixRequest, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]
    return {"status": "processing", "pix_key": body.pix_key, "amount": str(body.amount)}


@app.post("/escrows/hold", status_code=201)
async def hold_funds(body: EscrowRequest, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]
    try:
        return store.create_escrow(
            str(actor.user_id),
            str(actor.user_id),
            str(body.wallet_id),
            str(body.beneficiary_user_id),
            body.amount,
            body.release_condition,
            body.idempotency_key,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/escrows/{escrow_id}/release")
async def release_funds(escrow_id: str, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]
    try:
        return store.release_escrow(str(actor.user_id), escrow_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.get("/wallets/{user_id}")
async def get_user_wallets(user_id: str, actor: Actor = Depends(actor_from_headers)):
    if str(actor.user_id) != user_id and "auditor" not in actor.roles:
        raise HTTPException(status_code=403, detail="Acesso nao autorizado.")
    store = app.extra["store"]
    return store.list("wallets", user_id)


@app.get("/valley/gold/balance")
async def valley_gold_balance(actor: Actor = Depends(actor_from_headers)):
    demand_active_business(actor, "consultar saldo Gold Valley")
    store = app.extra["store"]
    entries = store.list("valley_gold_ledger_entries", str(actor.user_id))
    business_id = str(actor.business_id)
    relevant_entries = [
        entry
        for entry in entries
        if str(entry["payload"].get("merchant_business_id")) == business_id
    ]
    balance = sum(
        int(entry["payload"]["amount_gold_delta"]) for entry in relevant_entries
    )
    return {
        "merchant_business_id": business_id,
        "balance_gold": balance,
        "entry_count": len(relevant_entries),
        "source": "finance.valley_gold_ledger_entries",
        "derived": True,
    }


@app.post("/webhooks/cash-in", status_code=200)
async def mock_cash_in(request: Request, body: dict):
    """
    Mock de Webhook de Cash-in (ex: Stripe, MercadoPago, PIX).
    Recebe um payload do provedor e deposita na carteira do usuário.
    """
    user_id = body.get("user_id")
    amount = body.get("amount", 0)

    if not user_id or amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid payload")

    return {
        "status": "success",
        "deposited_amount": amount,
        "user_id": user_id,
        "message": "Depósito mockado processado via Webhook",
    }


@app.post("/gateways/cash-out", status_code=200)
async def mock_cash_out(
    actor: Actor = Depends(actor_from_headers), body: dict = Body(...)
):
    """
    Mock de Gateway de Cash-out (ex: TED/PIX via Banco parceiro).
    Subtrai o saldo da carteira local e chama API do banco para repassar valor real.
    """
    amount = body.get("amount", 0)
    bank_account = body.get("bank_account")

    if amount <= 0 or not bank_account:
        raise HTTPException(status_code=400, detail="Invalid withdrawal request")

    return {
        "status": "processing",
        "withdrawal_amount": amount,
        "destination": bank_account,
        "message": "Saque solicitado, aguardando liquidação bancária simulada.",
    }


# ---------------------------------------------------------------------------
# Recurso 4: Dinheiro com Destino (Primícia 4)
# ---------------------------------------------------------------------------

from datetime import UTC
from datetime import datetime as _datetime
from uuid import uuid4 as _uuid4

from shared.feature_flags import is_flag_enabled, require_flag
from _primicias import router as primacia_router

_FINANCE_FLAG = "primicia.finance.earmarked_money"


def _fnow() -> str:
    return _datetime.now(UTC).isoformat()


def _require_finance_flag(actor: Actor) -> None:
    require_flag(_FINANCE_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/allocation-rules", status_code=201)
async def create_allocation_rule(
    body: dict = Body(...),
    actor: Actor = Depends(actor_from_headers),
) -> dict:
    """Cria regra de distribuição de receita por finalidade."""
    _require_finance_flag(actor)
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=422, detail="name é obrigatório.")

    conditions = body.get("conditions", [])
    total_pct = sum(float(c.get("percentage", 0)) for c in conditions)
    if conditions and total_pct > 100.01:
        raise HTTPException(status_code=422, detail=f"Percentuais somam {total_pct}%. Máximo é 100%.")

    rule_id = str(_uuid4())
    payload = {"id": rule_id, "name": str(name)[:256], "tenant_id": str(actor.business_id) if actor.business_id else None, "status": "draft", "description": body.get("description", ""), "conditions": conditions, "created_by": str(actor.user_id), "created_at": _fnow()}
    store = app.extra["store"]
    try:
        return store.create("allocation_rules", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "draft", payload, str(actor.user_id), ("id",), "finance.allocation_rule.created", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/allocation-rules/{rule_id}/activate", status_code=200)
async def activate_allocation_rule(rule_id, body: dict = Body({}), actor: Actor = Depends(actor_from_headers)) -> dict:
    """Ativa regra após simulação e aprovação."""
    _require_finance_flag(actor)
    store = app.extra["store"]
    try:
        rule = store.get("allocation_rules", str(rule_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Regra não encontrada.")
    if rule.get("status") == "active":
        raise HTTPException(status_code=409, detail="Regra já está ativa.")
    return store.update(rule, {"status": "active", "activated_at": _fnow()}, "active", str(actor.user_id), "finance.allocation_rule.activated")


@app.post("/allocation-rules/{rule_id}/execute", status_code=201)
async def execute_allocation(rule_id, body: dict = Body(...), actor: Actor = Depends(actor_from_headers)) -> dict:
    """Executa alocação de entrada financeira pela regra. Idempotente."""
    _require_finance_flag(actor)
    income_ref = body.get("income_ref")
    total_amount = body.get("total_amount")
    if not income_ref or total_amount is None:
        raise HTTPException(status_code=422, detail="income_ref e total_amount são obrigatórios.")

    store = app.extra["store"]
    try:
        rule = store.get("allocation_rules", str(rule_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Regra não encontrada.")

    if rule.get("status") != "active":
        raise HTTPException(status_code=409, detail="Regra não está ativa.")

    conditions = rule.get("payload", {}).get("conditions", [])
    items = []
    remaining = float(total_amount)
    for cond in conditions:
        pct = float(cond.get("percentage", 0))
        amount = round(float(total_amount) * (pct / 100), 2)
        remaining -= amount
        items.append({"account_code": cond.get("account_code"), "amount": amount})

    exec_id = str(_uuid4())
    payload = {"id": exec_id, "rule_id": str(rule_id), "income_ref": str(income_ref), "total_amount": float(total_amount), "status": "completed", "items": items, "executed_at": _fnow()}
    try:
        return store.create("allocation_executions", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "completed", payload, str(actor.user_id), ("id",), "finance.income.allocated", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/allocation-executions/{execution_id}/reverse", status_code=200)
async def reverse_allocation(execution_id, body: dict = Body(...), actor: Actor = Depends(actor_from_headers)) -> dict:
    """Reverte alocação via lançamentos compensatórios. Auditável."""
    _require_finance_flag(actor)
    reason = body.get("reason", "").strip()
    if not reason:
        raise HTTPException(status_code=422, detail="reason é obrigatório para reversão.")
    store = app.extra["store"]
    try:
        execution = store.get("allocation_executions", str(execution_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Execução não encontrada.")
    if execution.get("status") == "reversed":
        raise HTTPException(status_code=409, detail="Alocação já foi revertida.")
    return store.update(execution, {"status": "reversed", "reversed_at": _fnow(), "reversed_by": str(actor.user_id), "reversal_reason": reason}, "reversed", str(actor.user_id), "finance.allocation.reversed")


@app.get("/allocation-rules/feature-status")
async def finance_feature_status() -> dict:
    return {"flag": _FINANCE_FLAG, "enabled": is_flag_enabled(_FINANCE_FLAG), "description": "Dinheiro com Destino – Primícia 4"}

app.include_router(primacia_router)