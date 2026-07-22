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
            return self.get_billing_detail(self.idempotency[idempotency_key])
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

    def cancel_billing_document(
        self, document_id: str, user_id: str, reason: str
    ) -> dict[str, Any]:
        document = self.documents.get(document_id)
        if not document:
            raise ValueError("Documento fiscal não encontrado.")
        payload = {**document.get("payload", {}), "cancel_reason": reason}
        document.update(
            {"status": "cancelled", "payload": payload, "cancelled_by": user_id}
        )
        return self.get_billing_detail(document_id)


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
    soft_deletable = frozenset(
        {
            "fiscal_documents",
            "accounts",
            "payables",
            "receivables",
            "cost_centers",
            "invoice_items",
        }
    )

    def create_billing_document(
        self,
        user_id: str,
        company_id: str,
        payload: dict[str, Any],
        items: list[dict[str, Any]] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Cria um documento fiscal (faturamento) garantindo a integridade e auditoria.
        Utiliza o correlation_id indexado para permitir conciliação futura.
        """
        resource_type = "fiscal_documents"
        event = "erp.invoice.created"
        materialized_payload = dict(payload)
        materialized_payload.setdefault("tax_amount_brl", "0.00")

        previous = self.find_idempotent(resource_type, idempotency_key)
        if previous:
            return self.get_billing_detail(previous["id"]) or previous

        resource_id = str(uuid4())
        with self.transaction() as conn:
            row = self._insert(
                conn,
                resource_type,
                resource_id,
                user_id,
                company_id,
                "pending",
                materialized_payload,
                user_id,
                idempotency_key,
            )
            document = self._resource(resource_type, row)
            if document is None:
                raise RuntimeError("PostgreSQL nao retornou documento fiscal criado.")

            for item in items or []:
                item_id = str(uuid4())
                conn.execute(
                    f"""INSERT INTO {self.tables["invoice_items"]}
                        (id, fiscal_document_id, description, quantity, unit_price_brl, total_price_brl, tax_amount_brl)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",  # nosec B608
                    (
                        item_id,
                        document["id"],
                        item["description"],
                        item.get("quantity", 1),
                        item["unit_price_brl"],
                        item["total_price_brl"],
                        item.get("tax_amount_brl", "0.00"),
                    ),
                )

            document["items_count"] = len(items or [])
            document["items"] = self._fetch_invoice_items(conn, document["id"])
            self._audit(
                conn,
                user_id,
                "create",
                resource_type,
                document["id"],
                None,
                document,
                user_id,
                company_id,
            )
            self._event(conn, event, user_id, document)
            return document

    def get_billing_detail(self, document_id: str) -> dict[str, Any] | None:
        """
        Recupera os detalhes de um faturamento, incluindo seus itens.
        """
        doc = self.get("fiscal_documents", document_id)
        if not doc:
            return None

        with self.transaction() as conn:
            items = self._fetch_invoice_items(conn, document_id)
        doc["items"] = items
        doc["items_count"] = len(items)

        return doc

    def cancel_billing_document(
        self, document_id: str, user_id: str, reason: str
    ) -> dict[str, Any]:
        """
        Cancela um documento fiscal mudando seu status para 'cancelled'.
        Garante auditoria imutável do motivo do cancelamento.
        """
        doc = self.get("fiscal_documents", document_id)
        if not doc:
            raise ValueError("Documento fiscal não encontrado.")

        updated = self.update(
            item=doc,
            payload={**doc["payload"], "cancel_reason": reason},
            status="cancelled",
            actor=user_id,
            action="cancel",
            event="erp.invoice.cancelled",
        )
        refreshed = self.get_billing_detail(updated["id"])
        return refreshed or updated

    def get_billing_by_correlation(self, correlation_id: str) -> list[dict[str, Any]]:
        """
        Recupera documentos fiscais usando o índice idx_audit_events_correlation da migration 016.
        """
        rows = self.connection.execute(
            """SELECT aggregate_id
               FROM audit.domain_events
               WHERE aggregate_type = 'fiscal_documents' AND correlation_id = %s
               ORDER BY created_at DESC""",
            (correlation_id,),
        ).fetchall()
        documents: list[dict[str, Any]] = []
        for row in rows:
            doc = self.get_billing_detail(str(row["aggregate_id"]))
            if doc is not None:
                documents.append(doc)
        return documents

    def _fetch_invoice_items(
        self, connection: Connection, document_id: str
    ) -> list[dict[str, Any]]:
        rows = connection.execute(
            f"""SELECT id, fiscal_document_id, description, quantity, unit_price_brl, total_price_brl,
                       tax_amount_brl, created_at, updated_at
                FROM {self.tables["invoice_items"]}
                WHERE fiscal_document_id = %s
                ORDER BY created_at ASC""",  # nosec B608
            (document_id,),
        ).fetchall()
        return [
            {
                "id": str(row["id"]),
                "fiscal_document_id": str(row["fiscal_document_id"]),
                "description": row["description"],
                "quantity": str(row["quantity"]),
                "unit_price_brl": str(row["unit_price_brl"]),
                "total_price_brl": str(row["total_price_brl"]),
                "tax_amount_brl": str(row["tax_amount_brl"]),
                "created_at": row["created_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat(),
            }
            for row in rows
        ]
