from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel
from shared.erp_postgres_store import ErpPostgresStore
from shared.integration_sandbox import (
    FiscalDocumentSandbox,
    local_fiscal_document_simulator,
)
from shared.runtime import create_module_app, get_erp_store
from shared.units_tax import TaxRule, calculate_tax

app = create_module_app("erp")


class InvoiceItemSchema(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price_brl: str
    total_price_brl: str
    tax_amount_brl: str = "0.00"


class BillingRequest(BaseModel):
    document_number: str | None = None
    amount_brl: str
    tax_amount_brl: str
    document_type: str = "nfe"
    items: list[InvoiceItemSchema]
    pepitas_reward: int | None = None


class CancelRequest(BaseModel):
    reason: str


class SandboxFiscalInvoiceRequest(BaseModel):
    invoice_id: str
    document_type: str
    amount_brl: str
    issuer_document: str


class TaxCalculationRequest(BaseModel):
    taxable_base: str
    rate: str
    base_reduction: str = "0"
    precision: int = 2
    rounding_mode: str = "half_up"
    legal_basis: str
    effective_from: datetime
    effective_to: datetime | None = None
    approved: bool


@app.post("/calculations/tax")
def calculate_tax_preview(
    request: TaxCalculationRequest,
    x_actor_user_id: str = Header(..., alias="X-Actor-User-Id"),
):
    """Recalcula o tributo no backend e devolve valores decimais serializados."""
    try:
        reduced_base, amount = calculate_tax(
            request.taxable_base,
            TaxRule(**request.model_dump(exclude={"taxable_base"})),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return {
        "taxable_base": request.taxable_base,
        "reduced_base": format(reduced_base, "f"),
        "tax_amount": format(amount, "f"),
        "legal_basis": request.legal_basis,
        "calculated_by": x_actor_user_id,
    }


@app.get("/erp/billing/{document_id}")
async def get_billing(
    document_id: str, store: ErpPostgresStore = Depends(get_erp_store)
):
    doc = store.get_billing_detail(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento fiscal não encontrado.")

    return doc


@app.post("/erp/billing")
async def create_billing(
    request: BillingRequest,
    x_actor_user_id: str = Header(...),
    x_actor_company_id: str = Header(...),
    x_idempotency_key: str | None = Header(None),
    store: ErpPostgresStore = Depends(get_erp_store),
):
    try:
        payload = request.model_dump(exclude={"items"})
        items = [item.model_dump() for item in request.items]

        if request.pepitas_reward and request.pepitas_reward not in {1, 10, 100}:
            raise HTTPException(
                status_code=422,
                detail="Gamificação inválida. Escolha 1, 10 ou 100 Pepitas.",
            )

        doc = store.create_billing_document(
            user_id=x_actor_user_id,
            company_id=x_actor_company_id,
            payload=payload,
            items=items,
            idempotency_key=x_idempotency_key,
        )

        if os.getenv("ALL_IN_ONE_ERP_FISCAL_SANDBOX", "true").lower() == "true":
            sandbox_result = local_fiscal_document_simulator(
                document_id=doc["id"],
                amount_brl=doc["payload"]["amount_brl"],
                company_id=x_actor_company_id,
            )
            doc["fiscal_authorization"] = sandbox_result

        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/erp/billing/{document_id}/cancel")
async def cancel_billing(
    document_id: str,
    request: CancelRequest,
    x_actor_user_id: str = Header(...),
    store: ErpPostgresStore = Depends(get_erp_store),
):
    try:
        doc = store.cancel_billing_document(
            document_id=document_id, user_id=x_actor_user_id, reason=request.reason
        )

        if os.getenv("ALL_IN_ONE_ERP_FISCAL_SANDBOX", "true").lower() == "true":
            sandbox_result = local_fiscal_document_simulator(
                document_id=document_id,
                action="cancel",
                reason=request.reason,
                company_id=doc.get("company_id") or doc.get("entity_id"),
            )
            doc["fiscal_cancellation"] = sandbox_result

        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/integrations/sandbox/fiscal/invoices")
async def sandbox_fiscal_invoice(
    request: SandboxFiscalInvoiceRequest,
    x_actor_user_id: str = Header(...),
):
    result = FiscalDocumentSandbox().issue_invoice(
        request.invoice_id,
        request.document_type,
        request.amount_brl,
        request.issuer_document,
    )
    return result.to_response()


# ---------------------------------------------------------------------------
# Recurso 12: Fechamento Contínuo por Exceção (Primícia 12)
# ---------------------------------------------------------------------------

from datetime import UTC
from datetime import datetime as _edatetime
from typing import Any as _Any
from uuid import uuid4 as _euuid4

from fastapi import Body as _Body
from shared.feature_flags import is_flag_enabled, require_flag
from ._primicias import router as primacia_router

_ERP_FLAG = "primicia.erp.continuous_close"


def _enow() -> str:
    return _edatetime.now(UTC).isoformat()


def _require_erp_flag(actor) -> None:
    require_flag(_ERP_FLAG, tenant_id=str(actor.business_id) if actor.business_id else None, user_id=str(actor.user_id))


@app.post("/close/exceptions", status_code=201)
async def register_close_exception(
    body: _Any = _Body(...),
    actor=Depends(actor_from_headers),
) -> dict:
    """Detecta e registra inconsistência real no fechamento."""
    _require_erp_flag(actor)
    period = body.get("period")
    exception_type = body.get("exception_type")
    description = body.get("description")
    if not period or not exception_type or not description:
        raise HTTPException(status_code=422, detail="period, exception_type e description são obrigatórios.")
    eid = str(_euuid4())
    payload = {"id": eid, "tenant_id": str(actor.business_id) if actor.business_id else None, "period": str(period), "exception_type": str(exception_type), "description": str(description), "evidence": body.get("evidence", {}), "status": "open", "detected_at": _enow()}
    store = app.extra["store"]
    try:
        return store.create("close_exceptions", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "open", payload, str(actor.user_id), ("id",), "erp.close_exception.detected", body.get("idempotency_key"))
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/close/exceptions/{exception_id}/resolve", status_code=200)
async def resolve_exception(
    exception_id,
    body: _Any = _Body(...),
    actor=Depends(actor_from_headers),
) -> dict:
    """Resolve exceção de fechamento com evidência e nota."""
    _require_erp_flag(actor)
    resolution_note = body.get("resolution_note", "").strip()
    if not resolution_note:
        raise HTTPException(status_code=422, detail="resolution_note é obrigatório.")
    store = app.extra["store"]
    try:
        exc_record = store.get("close_exceptions", str(exception_id))
    except Exception:
        raise HTTPException(status_code=404, detail="Exceção não encontrada.")
    return store.update(exc_record, {"status": "resolved", "resolved_at": _enow(), "resolved_by": str(actor.user_id), "resolution_note": resolution_note}, "resolved", str(actor.user_id), "erp.close_exception.resolved")


@app.post("/close/periods/{period}/ready", status_code=200)
async def mark_period_ready(period: str, actor=Depends(actor_from_headers)) -> dict:
    """Marca período como pronto para fechamento (snapshot reproduzível)."""
    _require_erp_flag(actor)
    sid = str(_euuid4())
    payload = {"id": sid, "tenant_id": str(actor.business_id) if actor.business_id else None, "period": period, "ready": True, "closed": False, "taken_at": _enow()}
    store = app.extra["store"]
    try:
        return store.create("close_period_snapshots", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "ready", payload, str(actor.user_id), ("id",), "erp.close_period.ready", f"close-ready-{period}")
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/close/periods/{period}/approve", status_code=200)
async def approve_period_close(period: str, body: _Any = _Body({}), actor=Depends(actor_from_headers)) -> dict:
    """Aprova e fecha período contábil. Período fechado fica protegido."""
    _require_erp_flag(actor)
    if "finance_manager" not in actor.roles and "administrator" not in actor.roles:
        raise HTTPException(status_code=403, detail="Apenas gestores financeiros podem fechar períodos.")
    aid = str(_euuid4())
    payload = {"id": aid, "period": period, "tenant_id": str(actor.business_id) if actor.business_id else None, "approved_by": str(actor.user_id), "approved_at": _enow(), "notes": body.get("notes", "")}
    store = app.extra["store"]
    try:
        return store.create("close_approvals", str(actor.user_id), str(actor.business_id) if actor.business_id else None, "approved", payload, str(actor.user_id), ("id",), "erp.close_period.approved", f"close-approve-{period}")
    except Exception as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/close/feature-status")
async def erp_feature_status() -> dict:
    return {"flag": _ERP_FLAG, "enabled": is_flag_enabled(_ERP_FLAG), "description": "Fechamento Contínuo por Exceção – Primícia 12"}

app.include_router(primacia_router)