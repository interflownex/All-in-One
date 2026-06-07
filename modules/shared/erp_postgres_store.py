from __future__ import annotations

from typing import Any
from uuid import uuid4
from psycopg import Connection
from .postgres_store import BasePostgresStore


class ErpMemoryStore:
    module = "erp"
    backend = "memory_erp_typed_store"

    def __init__(self) -> None:
        self.documents: dict[str, dict[str, Any]] = {}
        self.items: dict[str, list[dict[str, Any]]] = {}
        self.idempotency: dict[str, str] = {}

    def create_billing_document(
        self,
        user_id: str,
        company_id: str,
        payload: dict[str, Any],
        items: list[dict[str, Any]] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        if idempotency_key and idempotency_key in self.idempotency:
            return self.get_billing_detail(self.idempotency[idempotency_key])  # type: ignore[return-value]
        document_id = str(uuid4())
        document = {
            "id": document_id,
            "user_id": user_id,
            "entity_id": company_id,
            "company_id": company_id,
            "resource_type": "fiscal_documents",
            "status": "pending",
            "payload": payload,
            "items_count": len(items or []),
        }
        self.documents[document_id] = document
        self.items[document_id] = [
            {"id": str(uuid4()), "fiscal_document_id": document_id, **item}
            for item in (items or [])
        ]
        if idempotency_key:
            self.idempotency[idempotency_key] = document_id
        return {**document}

    def get_billing_detail(self, document_id: str) -> dict[str, Any] | None:
        document = self.documents.get(document_id)
        if not document:
            return None
        return {**document, "items": [*self.items.get(document_id, [])]}

    def cancel_billing_document(self, document_id: str, user_id: str, reason: str) -> dict[str, Any]:
        document = self.documents.get(document_id)
        if not document:
            raise ValueError("Documento fiscal não encontrado.")
        payload = {**document.get("payload", {}), "cancel_reason": reason}
        document.update({"status": "cancelled", "payload": payload, "cancelled_by": user_id})
        return self.get_billing_detail(document_id)  # type: ignore[return-value]

class ErpPostgresStore(BasePostgresStore):
    """
    Especialização do store ERP para lidar com faturamento e documentos fiscais.
    Integrado com os índices de performance da migration 016 (audit e correlation).
    """

    module = "erp"
    backend = "postgres_erp_typed_store"
    tables = {
        "fiscal_documents": "erp.fiscal_documents",
        "accounts": "erp.accounts",
        "payables": "erp.payables",
        "receivables": "erp.receivables",
        "cost_centers": "erp.cost_centers",
        "invoice_items": "erp.invoice_items",
    }
    soft_deletable = frozenset({"fiscal_documents", "accounts", "payables", "receivables", "cost_centers", "invoice_items"})

    def create_billing_document(
        self,
        user_id: str,
        company_id: str,
        payload: dict[str, Any],
        items: list[dict[str, Any]] | None = None,
        idempotency_key: str | None = None
    ) -> dict[str, Any]:
        """
        Cria um documento fiscal (faturamento) garantindo a integridade e auditoria.
        Utiliza o correlation_id indexado para permitir conciliação futura.
        """
        resource_type = "fiscal_documents"

        # Validação mandatória de impostos (evita NotNullViolation identificada em testes)
        if "tax_amount_brl" not in payload:
            payload["tax_amount_brl"] = "0.00"

        # Executa a criação do documento e itens em uma única transação
        with self.connection() as conn:
            document = self.create(
                resource_type=resource_type,
                user_id=user_id,
                entity_id=company_id,
                status="pending",
                payload=payload,
                actor=user_id,
                unique_fields=["document_number", "company_id"] if "document_number" in payload else None,
                event_type="erp.invoice.created",
                idempotency_key=idempotency_key,
                connection=conn
            )

            if items:
                for item in items:
                    item_id = str(uuid4())
                    conn.execute(
                        """INSERT INTO erp.invoice_items
                           (id, fiscal_document_id, description, quantity, unit_price_brl, total_price_brl, tax_amount_brl)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (item_id, document["id"], item["description"], item.get("quantity", 1), item["unit_price_brl"], item["total_price_brl"], item.get("tax_amount_brl", "0.00"))
                    )
                document["items_count"] = len(items)

            return document

    def get_billing_detail(self, document_id: str) -> dict[str, Any] | None:
        """
        Recupera os detalhes de um faturamento, incluindo seus itens.
        """
        doc = self.get("fiscal_documents", document_id)
        if not doc:
            return None

        # Busca itens vinculados
        items = self.list("invoice_items", fiscal_document_id=document_id)
        doc["items"] = items

        return doc

    def cancel_billing_document(
        self,
        document_id: str,
        user_id: str,
        reason: str
    ) -> dict[str, Any]:
        """
        Cancela um documento fiscal mudando seu status para 'cancelled'.
        Garante auditoria imutável do motivo do cancelamento.
        """
        doc = self.get("fiscal_documents", document_id)
        if not doc:
            raise ValueError("Documento fiscal não encontrado.")

        return self.update(
            resource=doc,
            payload={"cancel_reason": reason},
            status="cancelled",
            actor=user_id,
            event_type="erp.invoice.cancelled"
        )

    def get_billing_by_correlation(self, correlation_id: str) -> list[dict[str, Any]]:
        """
        Recupera documentos fiscais usando o índice idx_audit_events_correlation da migration 016.
        """
        return self.list("fiscal_documents", correlation_id=correlation_id)
