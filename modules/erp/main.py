from __future__ import annotations
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import Header, HTTPException, Depends
from typing import Any, Optional
from pydantic import BaseModel
from shared.erp_postgres_store import ErpPostgresStore
from shared.runtime import create_module_app, get_erp_store
from shared.integration_sandbox import FiscalDocumentSandbox, local_fiscal_document_simulator
from shared.units_tax import TaxRule, calculate_tax

app = create_module_app("erp")

class InvoiceItemSchema(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price_brl: str
    total_price_brl: str
    tax_amount_brl: str = "0.00"

class BillingRequest(BaseModel):
    document_number: Optional[str] = None
    amount_brl: str
    tax_amount_brl: str
    document_type: str = "nfe"
    items: list[InvoiceItemSchema]
    pepitas_reward: Optional[int] = None

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
    document_id: str,
    store: ErpPostgresStore = Depends(get_erp_store)
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
    x_idempotency_key: Optional[str] = Header(None),
    store: ErpPostgresStore = Depends(get_erp_store)
):
    try:
        payload = request.model_dump(exclude={"items"})
        items = [item.model_dump() for item in request.items]

        if request.pepitas_reward and request.pepitas_reward not in {1, 10, 100}:
            raise HTTPException(status_code=422, detail="Gamificação inválida. Escolha 1, 10 ou 100 Pepitas.")

        doc = store.create_billing_document(
            user_id=x_actor_user_id,
            company_id=x_actor_company_id,
            payload=payload,
            items=items,
            idempotency_key=x_idempotency_key
        )

        if os.getenv("ALL_IN_ONE_ERP_FISCAL_SANDBOX", "true").lower() == "true":
            sandbox_result = local_fiscal_document_simulator(
                document_id=doc["id"],
                amount_brl=doc["payload"]["amount_brl"],
                company_id=x_actor_company_id
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
    store: ErpPostgresStore = Depends(get_erp_store)
):
    try:
        doc = store.cancel_billing_document(
            document_id=document_id,
            user_id=x_actor_user_id,
            reason=request.reason
        )

        if os.getenv("ALL_IN_ONE_ERP_FISCAL_SANDBOX", "true").lower() == "true":
            sandbox_result = local_fiscal_document_simulator(
                document_id=document_id,
                action="cancel",
                reason=request.reason,
                company_id=doc.get("company_id") or doc.get("entity_id")
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
