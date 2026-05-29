from pathlib import Path
import sys
from fastapi import Request, HTTPException, Depends
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.runtime import create_module_app
from shared.security import Actor, actor_from_headers
from finance_models import TransferRequest, PixRequest, EscrowRequest

app = create_module_app("finance")

@app.post("/transfers", status_code=201)
async def transfer(body: TransferRequest, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]

    # Validações de segurança
    if str(body.source_wallet_id) == str(body.destination_wallet_id):
        raise HTTPException(status_code=422, detail="Carteiras de origem e destino devem ser diferentes.")

    # Em um cenário real, buscaríamos a carteira de destino se apenas destination_user_id fosse fornecido
    if not body.destination_wallet_id:
        raise HTTPException(status_code=422, detail="destination_wallet_id e obrigatorio neste baseline.")

    try:
        result = store.execute_transfer(
            str(actor.user_id),
            str(body.source_wallet_id),
            str(body.destination_wallet_id),
            body.amount,
            body.currency,
            body.description,
            body.idempotency_key
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro interno na transacao: {exc}")

@app.post("/pix/out", status_code=201)
async def pix_out(body: PixRequest, actor: Actor = Depends(actor_from_headers)):
    # Simulação de saída Pix (Débito na carteira e registro no Ledger)
    store = app.extra["store"]
    # Aqui usaríamos uma lógica similar à transferência, mas para uma "carteira de clearing" do sistema
    return {"status": "processing", "pix_key": body.pix_key, "amount": str(body.amount)}

@app.post("/escrows/hold", status_code=201)
async def hold_funds(body: EscrowRequest, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]
    try:
        return store.create_escrow(
            str(actor.user_id),
            str(actor.user_id), # O pagador é o ator autenticado
            str(body.wallet_id),
            str(body.beneficiary_user_id),
            body.amount,
            body.release_condition,
            body.idempotency_key
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

@app.post("/escrows/{escrow_id}/release")
async def release_funds(escrow_id: str, actor: Actor = Depends(actor_from_headers)):
    store = app.extra["store"]
    # Em produção, validaríamos se o ator tem permissão (é o pagador, sistema ou auditor)
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

