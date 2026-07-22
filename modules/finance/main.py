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
