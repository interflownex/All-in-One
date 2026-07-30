from __future__ import annotations

import hashlib
import json
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from psycopg import Connection
from psycopg.types.json import Jsonb

from .event_contract import EVENT_SCHEMA_VERSION, build_event_envelope
from .postgres_store import BasePostgresStore

MONEY = Decimal("0.01")
CHECKOUT_STATUSES_TERMINAL = frozenset(
    {"confirmed", "rejected", "payment_failed", "cancelled", "expired", "compensated"}
)


class CheckoutNotFoundError(RuntimeError):
    """Checkout, carrinho, produto, loja, carteira ou inventário não localizado."""


class CheckoutConflictError(RuntimeError):
    """Estado, preço, disponibilidade ou transição incompatível."""


class CheckoutIdempotencyConflictError(CheckoutConflictError):
    """Uma chave idempotente foi reutilizada com outro corpo."""


class MarketplaceCheckoutBase(BasePostgresStore):
    """Base compartilhada do checkout Marketplace transacional."""

    module = "marketplace"
    backend = "postgres_marketplace_checkout_store"
    tables = {
        "checkouts": "marketplace.checkouts",
        "checkout_items": "marketplace.checkout_items",
        "checkout_operations": "marketplace.checkout_operations",
    }
    soft_deletable = frozenset()

    @staticmethod
    def _money(value: Decimal | str | int) -> Decimal:
        return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)

    @staticmethod
    def _decimal_text(value: Decimal | Any) -> str:
        return format(Decimal(str(value)).normalize(), "f")

    @classmethod
    def request_hash(
        cls,
        *,
        cart_id: str,
        currency: str,
        expected_total_brl: Decimal,
        wallet_id: str,
        payment_method: str,
    ) -> str:
        normalized = json.dumps(
            {
                "cart_id": cart_id,
                "currency": currency,
                "expected_total_brl": cls._decimal_text(
                    cls._money(expected_total_brl)
                ),
                "payment_method": payment_method,
                "wallet_id": wallet_id,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def operation_hash(payload: dict[str, Any]) -> str:
        normalized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @classmethod
    def _checkout_view(
        cls, row: dict[str, Any], items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "checkout_id": str(row["id"]),
            "order_id": str(row["order_id"]),
            "cart_id": str(row["cart_id"]),
            "user_id": str(row["user_id"]),
            "company_id": str(row["company_id"]),
            "store_id": str(row["store_id"]),
            "wallet_id": str(row["wallet_id"]),
            "status": row["status"],
            "payment_status": row["payment_status"],
            "currency": row["currency"],
            "total_brl": cls._decimal_text(row["total_brl"]),
            "expected_total_brl": cls._decimal_text(row["expected_total_brl"]),
            "reservation_expires_at": row["reservation_expires_at"].isoformat()
            if row.get("reservation_expires_at")
            else None,
            "failure_reason": row.get("failure_reason"),
            "correlation_id": str(row["correlation_id"]),
            "items": items,
            "snapshot": dict(row.get("snapshot") or {}),
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }

    @classmethod
    def _item_view(cls, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "product_id": str(row["product_id"]),
            "store_id": str(row["store_id"]),
            "company_id": str(row["company_id"]),
            "inventory_item_id": str(row["inventory_item_id"]),
            "reservation_id": str(row["reservation_id"]),
            "sku": row["sku"],
            "name": row["product_name"],
            "quantity": cls._decimal_text(row["quantity"]),
            "unit_price_brl": cls._decimal_text(row["unit_price_brl"]),
            "subtotal_brl": cls._decimal_text(row["subtotal_brl"]),
            "currency": row["currency"],
            "promotion": dict(row.get("promotion_snapshot") or {}),
            "catalog_version": row["catalog_version"].isoformat(),
        }

    def _load_checkout_locked(
        self, connection: Connection, checkout_id: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        row = connection.execute(
            "SELECT * FROM marketplace.checkouts WHERE id = %s FOR UPDATE",
            (checkout_id,),
        ).fetchone()
        if row is None:
            raise CheckoutNotFoundError("Checkout não encontrado.")
        item_rows = connection.execute(
            """SELECT * FROM marketplace.checkout_items
               WHERE checkout_id = %s ORDER BY created_at, id""",
            (checkout_id,),
        ).fetchall()
        return row, [self._item_view(item) for item in item_rows]

    def get_checkout(self, checkout_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM marketplace.checkouts WHERE id = %s", (checkout_id,)
        ).fetchone()
        if row is None:
            return None
        item_rows = self.connection.execute(
            """SELECT * FROM marketplace.checkout_items
               WHERE checkout_id = %s ORDER BY created_at, id""",
            (checkout_id,),
        ).fetchall()
        return self._checkout_view(row, [self._item_view(item) for item in item_rows])

    @staticmethod
    def _event_item(
        *,
        aggregate_type: str,
        aggregate_id: str,
        user_id: str,
        company_id: str,
        status: str,
        payload: dict[str, Any],
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        return {
            "id": aggregate_id,
            "resource_type": aggregate_type,
            "user_id": user_id,
            "entity_id": company_id,
            "status": status,
            "idempotency_key": idempotency_key,
            "payload": payload,
        }

    def _emit_event(
        self,
        connection: Connection,
        *,
        module: str,
        routing_key: str,
        actor: str,
        aggregate_type: str,
        aggregate_id: str,
        user_id: str,
        company_id: str,
        status: str,
        payload: dict[str, Any],
        idempotency_key: str | None,
        correlation_id: str,
        causation_id: str | None,
    ) -> None:
        item = self._event_item(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            user_id=user_id,
            company_id=company_id,
            status=status,
            payload=payload,
            idempotency_key=idempotency_key,
        )
        envelope = build_event_envelope(
            module=module,
            routing_key=routing_key,
            actor_user_id=actor,
            item=item,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        connection.execute(
            """INSERT INTO audit.domain_events
               (id, user_id, actor_user_id, entity_id, routing_key, aggregate_type,
                aggregate_id, correlation_id, schema_version, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                envelope["event_id"],
                user_id,
                actor,
                company_id,
                routing_key,
                aggregate_type,
                aggregate_id,
                correlation_id,
                EVENT_SCHEMA_VERSION,
                Jsonb(envelope),
                actor,
            ),
        )

    @staticmethod
    def _cart_items(cart: dict[str, Any]) -> list[dict[str, Any]]:
        payload = dict((cart.get("metadata") or {}).get("runtime_payload") or {})
        if payload.get("cart_type") != "cart":
            raise CheckoutConflictError(
                "O recurso informado não é um carrinho de compras."
            )
        raw_items = payload.get("items")
        if not isinstance(raw_items, list) or not raw_items:
            raise CheckoutConflictError("Carrinho vazio não pode ser confirmado.")
        normalized: list[dict[str, Any]] = []
        seen: set[str] = set()
        for raw in raw_items:
            if not isinstance(raw, dict):
                raise CheckoutConflictError("Carrinho contém item inválido.")
            product_id = str(raw.get("product_id") or "")
            quantity = raw.get("quantity")
            if not product_id or not isinstance(quantity, int) or quantity < 1:
                raise CheckoutConflictError(
                    "Carrinho contém produto ou quantidade inválida."
                )
            if product_id in seen:
                raise CheckoutConflictError("Carrinho contém produto duplicado.")
            seen.add(product_id)
            normalized.append(
                {"product_id": product_id, "quantity": Decimal(quantity)}
            )
        return normalized
