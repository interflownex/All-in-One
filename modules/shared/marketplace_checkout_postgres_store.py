from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .audit_contract import insert_postgres_audit
from .event_contract import EVENT_SCHEMA_VERSION, build_event_envelope


class MarketplaceCheckoutError(RuntimeError):
    """Erro base do checkout transacional."""


class MarketplaceCheckoutNotFoundError(MarketplaceCheckoutError):
    """Checkout, carrinho ou recurso dependente não encontrado."""


class MarketplaceCheckoutConflictError(MarketplaceCheckoutError):
    """Estado, preço, estoque ou corpo incompatível com a operação."""


class MarketplaceCheckoutIdempotencyConflictError(MarketplaceCheckoutConflictError):
    """A mesma chave idempotente foi reutilizada com outro corpo."""


class MarketplaceCheckoutPaymentError(MarketplaceCheckoutConflictError):
    """A autorização financeira falhou e as reservas foram compensadas."""


class MarketplaceCheckoutPostgresStore:
    """Orquestra checkout, reservas, pedido e Wallet em uma transação PostgreSQL."""

    backend = "postgres_marketplace_checkout_store"
    _MONEY = Decimal("0.01")
    _PUBLIC_PRODUCT_STATUSES = frozenset({"active", "published"})
    _PUBLIC_STORE_STATUSES = frozenset({"active", "approved"})

    def __init__(self, dsn: str) -> None:
        self.connection: Connection = psycopg.connect(dsn, row_factory=dict_row)

    def close(self) -> None:
        self.connection.close()

    @contextmanager
    def transaction(self) -> Iterator[Connection]:
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    @classmethod
    def _money(cls, value: Decimal | str | int | float) -> Decimal:
        return Decimal(str(value)).quantize(cls._MONEY, rounding=ROUND_HALF_UP)

    @staticmethod
    def _runtime_payload(row: dict[str, Any]) -> dict[str, Any]:
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, dict):
            return {}
        payload = metadata.get("runtime_payload") or {}
        return dict(payload) if isinstance(payload, dict) else {}

    @staticmethod
    def _stable_hash(payload: dict[str, Any]) -> str:
        encoded = json.dumps(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    @classmethod
    def checkout_request_hash(
        cls,
        *,
        cart_id: str,
        currency: str,
        expected_total_brl: Decimal,
        payment_method: str,
    ) -> str:
        return cls._stable_hash(
            {
                "cart_id": cart_id,
                "currency": currency,
                "expected_total_brl": str(cls._money(expected_total_brl)),
                "payment_method": payment_method,
            }
        )

    @classmethod
    def confirmation_request_hash(
        cls,
        *,
        checkout_id: str,
        payment_method: str,
    ) -> str:
        return cls._stable_hash(
            {"checkout_id": checkout_id, "payment_method": payment_method}
        )

    @classmethod
    def reservation_request_hash(
        cls,
        *,
        inventory_item_id: str,
        order_id: str,
        quantity: Decimal,
        expires_in_seconds: int,
    ) -> str:
        return cls._stable_hash(
            {
                "inventory_item_id": inventory_item_id,
                "order_id": order_id,
                "quantity": format(Decimal(str(quantity)).normalize(), "f"),
                "expires_in_seconds": expires_in_seconds,
            }
        )

    @staticmethod
    def _checkout_view(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "checkout_id": str(row["id"]),
            "order_id": str(row["order_id"]),
            "cart_id": str(row["cart_id"]),
            "user_id": str(row["user_id"]),
            "company_id": str(row["company_id"]),
            "store_id": str(row["store_id"]),
            "status": row["status"],
            "payment_status": row["payment_status"],
            "payment_method": row["payment_method"],
            "currency": row["currency"],
            "expected_total_brl": str(row["expected_total_brl"]),
            "total_brl": str(row["total_brl"]),
            "reservation_ids": [str(item) for item in (row.get("reservation_ids") or [])],
            "reservation_expires_at": row["expires_at"].isoformat(),
            "escrow_id": str(row["escrow_id"]) if row.get("escrow_id") else None,
            "snapshot": dict(row.get("snapshot") or {}),
            "correlation_id": str(row["correlation_id"]),
            "confirmed_at": row["confirmed_at"].isoformat()
            if row.get("confirmed_at")
            else None,
            "cancelled_at": row["cancelled_at"].isoformat()
            if row.get("cancelled_at")
            else None,
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }

    @staticmethod
    def _reservation_view(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "reservation_id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "company_id": str(row["company_id"]),
            "order_id": str(row["order_id"]),
            "inventory_item_id": str(row["inventory_item_id"]),
            "quantity": str(row["quantity"]),
            "status": row["status"],
            "expires_at": row["expires_at"].isoformat(),
            "release_reason": row.get("release_reason"),
        }

    @staticmethod
    def _event_item(
        *,
        aggregate_id: str,
        resource_type: str,
        user_id: str,
        company_id: str | None,
        status: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "id": aggregate_id,
            "resource_type": resource_type,
            "user_id": user_id,
            "entity_id": company_id,
            "status": status,
            "payload": payload,
        }

    def _emit_event(
        self,
        connection: Connection,
        *,
        module: str,
        routing_key: str,
        actor: str,
        aggregate_id: str,
        resource_type: str,
        user_id: str,
        company_id: str | None,
        status: str,
        payload: dict[str, Any],
        correlation_id: str,
        causation_id: str | None,
    ) -> None:
        item = self._event_item(
            aggregate_id=aggregate_id,
            resource_type=resource_type,
            user_id=user_id,
            company_id=company_id,
            status=status,
            payload=payload,
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
                resource_type,
                aggregate_id,
                correlation_id,
                EVENT_SCHEMA_VERSION,
                Jsonb(envelope),
                actor,
            ),
        )

    @staticmethod
    def _audit(
        connection: Connection,
        *,
        module: str,
        actor: str,
        action: str,
        resource_type: str,
        resource_id: str,
        before: Any,
        after: Any,
        user_id: str | None,
        company_id: str | None,
    ) -> None:
        insert_postgres_audit(
            connection,
            module=module,
            actor_user_id=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before=before,
            after=after,
            user_id=user_id,
            company_id=company_id,
        )

    def get_checkout(self, *, checkout_id: str, user_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            """SELECT * FROM marketplace.checkout_attempts
               WHERE id = %s AND user_id = %s""",
            (checkout_id, user_id),
        ).fetchone()
        return self._checkout_view(row) if row else None

    def create_checkout(
        self,
        *,
        user_id: str,
        cart_id: str,
        currency: str,
        expected_total_brl: Decimal,
        payment_method: str,
        actor: str,
        idempotency_key: str,
        correlation_id: str,
        causation_id: str | None,
        reservation_ttl_seconds: int = 900,
    ) -> dict[str, Any]:
        normalized_currency = currency.upper()
        normalized_method = payment_method.casefold()
        request_hash = self.checkout_request_hash(
            cart_id=cart_id,
            currency=normalized_currency,
            expected_total_brl=expected_total_brl,
            payment_method=normalized_method,
        )
        conflict_id: str | None = None

        with self.transaction() as connection:
            previous = connection.execute(
                """SELECT * FROM marketplace.checkout_attempts
                   WHERE user_id = %s AND idempotency_key = %s
                   FOR UPDATE""",
                (user_id, idempotency_key),
            ).fetchone()
            if previous is not None:
                if previous["request_hash"] == request_hash:
                    return self._checkout_view(previous)
                conflict_id = str(previous["id"])
                self._audit(
                    connection,
                    module="marketplace",
                    actor=actor,
                    action="checkout_idempotency_conflict",
                    resource_type="checkout_attempts",
                    resource_id=conflict_id,
                    before=self._checkout_view(previous),
                    after={"request_hash_mismatch": True},
                    user_id=user_id,
                    company_id=str(previous["company_id"]),
                )
            else:
                if normalized_currency != "BRL":
                    raise MarketplaceCheckoutConflictError(
                        "Somente BRL é permitido neste incremento."
                    )
                if normalized_method != "wallet":
                    raise MarketplaceCheckoutConflictError(
                        "Somente Wallet interna é permitida neste incremento."
                    )

                cart = connection.execute(
                    """SELECT * FROM marketplace.carts
                       WHERE id = %s AND user_id = %s AND deleted_at IS NULL
                       FOR UPDATE""",
                    (cart_id, user_id),
                ).fetchone()
                if cart is None:
                    raise MarketplaceCheckoutNotFoundError(
                        "Carrinho não encontrado para o consumidor autenticado."
                    )
                cart_payload = self._runtime_payload(cart)
                if cart_payload.get("cart_type") != "cart":
                    raise MarketplaceCheckoutConflictError("Recurso informado não é um carrinho.")
                raw_items = cart_payload.get("items")
                if not isinstance(raw_items, list) or not raw_items:
                    raise MarketplaceCheckoutConflictError("Carrinho vazio.")

                locked_items: list[dict[str, Any]] = []
                snapshot_items: list[dict[str, Any]] = []
                total = Decimal("0.00")
                selected_store_id: str | None = None
                selected_company_id: str | None = None
                merchant_user_id: str | None = None

                for position, raw_item in enumerate(raw_items):
                    if not isinstance(raw_item, dict):
                        raise MarketplaceCheckoutConflictError("Item de carrinho inválido.")
                    product_id = str(raw_item.get("product_id") or "")
                    quantity = raw_item.get("quantity")
                    if not product_id or not isinstance(quantity, int) or not 1 <= quantity <= 99:
                        raise MarketplaceCheckoutConflictError(
                            "Produto e quantidade válidos são obrigatórios."
                        )
                    product = connection.execute(
                        """SELECT
                               p.id AS product_id,
                               p.user_id AS product_owner_id,
                               p.store_id,
                               p.sku,
                               p.name,
                               p.price_brl,
                               p.status AS product_status,
                               p.metadata AS product_metadata,
                               p.updated_at AS product_updated_at,
                               p.deleted_at AS product_deleted_at,
                               s.user_id AS merchant_user_id,
                               s.company_id,
                               s.status AS store_status,
                               s.deleted_at AS store_deleted_at
                           FROM marketplace.products p
                           JOIN marketplace.stores s ON s.id = p.store_id
                           WHERE p.id = %s
                           FOR SHARE OF p, s""",
                        (product_id,),
                    ).fetchone()
                    if product is None:
                        raise MarketplaceCheckoutNotFoundError(
                            f"Produto {product_id} não encontrado."
                        )
                    if (
                        product["product_deleted_at"] is not None
                        or product["store_deleted_at"] is not None
                        or product["product_status"] not in self._PUBLIC_PRODUCT_STATUSES
                        or product["store_status"] not in self._PUBLIC_STORE_STATUSES
                    ):
                        raise MarketplaceCheckoutConflictError(
                            f"Produto {product_id} ou loja indisponível."
                        )
                    product_payload = self._runtime_payload(
                        {"metadata": product["product_metadata"]}
                    )
                    item_currency = str(product_payload.get("currency") or "BRL").upper()
                    if item_currency != "BRL":
                        raise MarketplaceCheckoutConflictError(
                            f"Produto {product_id} possui moeda incompatível."
                        )
                    store_id = str(product["store_id"])
                    company_id = str(product["company_id"])
                    if selected_store_id is None:
                        selected_store_id = store_id
                        selected_company_id = company_id
                        merchant_user_id = str(product["merchant_user_id"])
                    elif store_id != selected_store_id or company_id != selected_company_id:
                        raise MarketplaceCheckoutConflictError(
                            "O primeiro checkout aceita itens de uma única loja e empresa."
                        )
                    unit_price = self._money(product["price_brl"])
                    subtotal = self._money(unit_price * quantity)
                    inventory = connection.execute(
                        """SELECT * FROM stock.inventory_items
                           WHERE product_id = %s
                             AND company_id = %s
                             AND status IN ('active', 'depleted')
                             AND available_quantity >= %s
                           ORDER BY available_quantity DESC, id
                           LIMIT 1
                           FOR UPDATE""",
                        (product_id, company_id, quantity),
                    ).fetchone()
                    if inventory is None:
                        raise MarketplaceCheckoutConflictError(
                            f"Saldo Stock insuficiente para o produto {product_id}."
                        )
                    snapshot_item = {
                        "position": position,
                        "product_id": product_id,
                        "inventory_item_id": str(inventory["id"]),
                        "store_id": store_id,
                        "company_id": company_id,
                        "sku": product["sku"],
                        "name": product["name"],
                        "quantity": quantity,
                        "unit_price_brl": str(unit_price),
                        "subtotal_brl": str(subtotal),
                        "currency": "BRL",
                        "promotion": product_payload.get("promotion")
                        if isinstance(product_payload.get("promotion"), dict)
                        else None,
                        "catalog_updated_at": product["product_updated_at"].isoformat(),
                    }
                    snapshot_items.append(snapshot_item)
                    locked_items.append(
                        {
                            "inventory": inventory,
                            "quantity": Decimal(quantity),
                            "snapshot": snapshot_item,
                        }
                    )
                    total += subtotal

                total = self._money(total)
                expected = self._money(expected_total_brl)
                if total != expected:
                    raise MarketplaceCheckoutConflictError(
                        f"Preço divergente: esperado {expected}, atual {total}."
                    )
                if selected_store_id is None or selected_company_id is None or merchant_user_id is None:
                    raise MarketplaceCheckoutConflictError("Carrinho sem loja elegível.")

                checkout_id = str(uuid4())
                order_id = str(uuid4())
                expires_at = datetime.now(UTC) + timedelta(seconds=reservation_ttl_seconds)
                reservation_ids = [str(uuid4()) for _ in locked_items]
                snapshot = {
                    "cart_id": cart_id,
                    "store_id": selected_store_id,
                    "company_id": selected_company_id,
                    "currency": "BRL",
                    "total_brl": str(total),
                    "items": snapshot_items,
                }
                order_payload = {
                    "checkout_id": checkout_id,
                    "cart_id": cart_id,
                    "store_id": selected_store_id,
                    "company_id": selected_company_id,
                    "currency": "BRL",
                    "total_brl": str(total),
                    "payment_method": "wallet",
                    "payment_status": "not_started",
                    "reservation_ids": reservation_ids,
                    "snapshot_hash": self._stable_hash(snapshot),
                    "correlation_id": correlation_id,
                }
                connection.execute(
                    """INSERT INTO marketplace.orders
                       (id, user_id, store_id, escrow_id, total_brl, commission_brl,
                        status, metadata, created_by, updated_by, idempotency_key,
                        offer_id, company_id)
                       VALUES (%s, %s, %s, NULL, %s, 0, 'pending', %s, %s, %s, %s, NULL, %s)""",
                    (
                        order_id,
                        user_id,
                        selected_store_id,
                        total,
                        Jsonb({"runtime_payload": order_payload}),
                        actor,
                        actor,
                        idempotency_key,
                        selected_company_id,
                    ),
                )
                checkout_row = connection.execute(
                    """INSERT INTO marketplace.checkout_attempts
                       (id, user_id, company_id, store_id, cart_id, order_id,
                        status, payment_status, payment_method, currency,
                        expected_total_brl, total_brl, idempotency_key, request_hash,
                        snapshot, reservation_ids, correlation_id, causation_id,
                        expires_at, metadata, created_by, updated_by)
                       VALUES (%s, %s, %s, %s, %s, %s,
                               'pending_payment', 'not_started', 'wallet', 'BRL',
                               %s, %s, %s, %s, %s, %s, %s, %s, %s,
                               '{}'::jsonb, %s, %s)
                       RETURNING *""",
                    (
                        checkout_id,
                        user_id,
                        selected_company_id,
                        selected_store_id,
                        cart_id,
                        order_id,
                        expected,
                        total,
                        idempotency_key,
                        request_hash,
                        Jsonb(snapshot),
                        Jsonb(reservation_ids),
                        correlation_id,
                        causation_id,
                        expires_at,
                        actor,
                        actor,
                    ),
                ).fetchone()
                checkout_view = self._checkout_view(checkout_row)
                self._audit(
                    connection,
                    module="marketplace",
                    actor=actor,
                    action="checkout_start",
                    resource_type="checkout_attempts",
                    resource_id=checkout_id,
                    before=None,
                    after=checkout_view,
                    user_id=user_id,
                    company_id=selected_company_id,
                )
                self._audit(
                    connection,
                    module="marketplace",
                    actor=actor,
                    action="create",
                    resource_type="orders",
                    resource_id=order_id,
                    before=None,
                    after=order_payload,
                    user_id=user_id,
                    company_id=selected_company_id,
                )
                self._emit_event(
                    connection,
                    module="marketplace",
                    routing_key="marketplace.checkout.started",
                    actor=actor,
                    aggregate_id=checkout_id,
                    resource_type="checkout_attempts",
                    user_id=user_id,
                    company_id=selected_company_id,
                    status="pending_payment",
                    payload={"order_id": order_id, "total_brl": str(total)},
                    correlation_id=correlation_id,
                    causation_id=causation_id,
                )
                self._emit_event(
                    connection,
                    module="marketplace",
                    routing_key="marketplace.order.created",
                    actor=actor,
                    aggregate_id=order_id,
                    resource_type="orders",
                    user_id=user_id,
                    company_id=selected_company_id,
                    status="pending",
                    payload={"checkout_id": checkout_id, "total_brl": str(total)},
                    correlation_id=correlation_id,
                    causation_id=checkout_id,
                )

                for position, item in enumerate(locked_items):
                    inventory = item["inventory"]
                    quantity = item["quantity"]
                    reservation_id = reservation_ids[position]
                    connection.execute(
                        """UPDATE stock.inventory_items
                           SET reserved_quantity = reserved_quantity + %s,
                               version = version + 1,
                               status = CASE
                                   WHEN physical_quantity = reserved_quantity + %s THEN 'depleted'
                                   ELSE 'active'
                               END,
                               updated_at = NOW(), updated_by = %s
                           WHERE id = %s AND company_id = %s""",
                        (
                            quantity,
                            quantity,
                            actor,
                            inventory["id"],
                            selected_company_id,
                        ),
                    )
                    reservation_key = f"{idempotency_key}:stock:{position}"
                    reservation_hash = self.reservation_request_hash(
                        inventory_item_id=str(inventory["id"]),
                        order_id=order_id,
                        quantity=quantity,
                        expires_in_seconds=reservation_ttl_seconds,
                    )
                    reservation_row = connection.execute(
                        """INSERT INTO stock.stock_reservations
                           (id, user_id, company_id, order_id, inventory_item_id,
                            quantity, status, idempotency_key, request_hash,
                            correlation_id, causation_id, expires_at, metadata,
                            created_by, updated_by)
                           VALUES (%s, %s, %s, %s, %s, %s, 'reserved', %s, %s,
                                   %s, %s, %s, '{}'::jsonb, %s, %s)
                           RETURNING *""",
                        (
                            reservation_id,
                            user_id,
                            selected_company_id,
                            order_id,
                            inventory["id"],
                            quantity,
                            reservation_key,
                            reservation_hash,
                            correlation_id,
                            checkout_id,
                            expires_at,
                            actor,
                            actor,
                        ),
                    ).fetchone()
                    reservation_view = self._reservation_view(reservation_row)
                    self._audit(
                        connection,
                        module="stock",
                        actor=actor,
                        action="reserve",
                        resource_type="stock_reservations",
                        resource_id=reservation_id,
                        before=None,
                        after=reservation_view,
                        user_id=user_id,
                        company_id=selected_company_id,
                    )
                    self._emit_event(
                        connection,
                        module="stock",
                        routing_key="stock.reservation.created",
                        actor=actor,
                        aggregate_id=reservation_id,
                        resource_type="stock_reservations",
                        user_id=user_id,
                        company_id=selected_company_id,
                        status="reserved",
                        payload={
                            "checkout_id": checkout_id,
                            "order_id": order_id,
                            "inventory_item_id": str(inventory["id"]),
                            "quantity": str(quantity),
                            "expires_at": expires_at.isoformat(),
                        },
                        correlation_id=correlation_id,
                        causation_id=checkout_id,
                    )
                return checkout_view

        if conflict_id is not None:
            raise MarketplaceCheckoutIdempotencyConflictError(
                f"Chave idempotente já usada pelo checkout {conflict_id} com outro corpo."
            )
        raise MarketplaceCheckoutError("Checkout não produziu resultado.")

    def _release_reservation_locked(
        self,
        connection: Connection,
        *,
        reservation: dict[str, Any],
        actor: str,
        reason: str,
        terminal_status: str,
        routing_key: str,
        correlation_id: str,
        causation_id: str | None,
    ) -> dict[str, Any]:
        if reservation["status"] in {"released", "expired"}:
            return reservation
        if reservation["status"] != "reserved":
            raise MarketplaceCheckoutConflictError(
                f"Reserva {reservation['id']} incompatível: {reservation['status']}."
            )
        inventory = connection.execute(
            "SELECT * FROM stock.inventory_items WHERE id = %s FOR UPDATE",
            (reservation["inventory_item_id"],),
        ).fetchone()
        if inventory is None:
            raise MarketplaceCheckoutNotFoundError("Inventário da reserva não encontrado.")
        updated = connection.execute(
            """UPDATE stock.inventory_items
               SET reserved_quantity = reserved_quantity - %s,
                   version = version + 1,
                   status = CASE
                       WHEN physical_quantity - (reserved_quantity - %s) = 0 THEN 'depleted'
                       ELSE 'active'
                   END,
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s AND reserved_quantity >= %s
               RETURNING id""",
            (
                reservation["quantity"],
                reservation["quantity"],
                actor,
                inventory["id"],
                reservation["quantity"],
            ),
        ).fetchone()
        if updated is None:
            raise MarketplaceCheckoutConflictError(
                "Saldo reservado inconsistente durante compensação."
            )
        row = connection.execute(
            """UPDATE stock.stock_reservations
               SET status = %s, released_at = NOW(), release_reason = %s,
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s AND status = 'reserved'
               RETURNING *""",
            (terminal_status, reason, actor, reservation["id"]),
        ).fetchone()
        before = self._reservation_view(reservation)
        after = self._reservation_view(row)
        self._audit(
            connection,
            module="stock",
            actor=actor,
            action="expire" if terminal_status == "expired" else "release",
            resource_type="stock_reservations",
            resource_id=str(reservation["id"]),
            before=before,
            after=after,
            user_id=str(reservation["user_id"]),
            company_id=str(reservation["company_id"]),
        )
        self._emit_event(
            connection,
            module="stock",
            routing_key=routing_key,
            actor=actor,
            aggregate_id=str(reservation["id"]),
            resource_type="stock_reservations",
            user_id=str(reservation["user_id"]),
            company_id=str(reservation["company_id"]),
            status=terminal_status,
            payload={"reason": reason, "order_id": str(reservation["order_id"])},
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        return row

    def _commit_reservation_locked(
        self,
        connection: Connection,
        *,
        reservation: dict[str, Any],
        actor: str,
        correlation_id: str,
        causation_id: str | None,
    ) -> dict[str, Any]:
        if reservation["status"] == "committed":
            return reservation
        if reservation["status"] != "reserved":
            raise MarketplaceCheckoutConflictError(
                f"Reserva {reservation['id']} incompatível: {reservation['status']}."
            )
        inventory = connection.execute(
            "SELECT * FROM stock.inventory_items WHERE id = %s FOR UPDATE",
            (reservation["inventory_item_id"],),
        ).fetchone()
        if inventory is None:
            raise MarketplaceCheckoutNotFoundError("Inventário da reserva não encontrado.")
        updated_inventory = connection.execute(
            """UPDATE stock.inventory_items
               SET physical_quantity = physical_quantity - %s,
                   reserved_quantity = reserved_quantity - %s,
                   version = version + 1,
                   status = CASE
                       WHEN physical_quantity - %s = 0 THEN 'depleted'
                       ELSE 'active'
                   END,
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s
                 AND physical_quantity >= %s
                 AND reserved_quantity >= %s
               RETURNING id""",
            (
                reservation["quantity"],
                reservation["quantity"],
                reservation["quantity"],
                actor,
                inventory["id"],
                reservation["quantity"],
                reservation["quantity"],
            ),
        ).fetchone()
        if updated_inventory is None:
            raise MarketplaceCheckoutConflictError("Saldo reservado inconsistente.")
        row = connection.execute(
            """UPDATE stock.stock_reservations
               SET status = 'committed', committed_at = NOW(),
                   updated_at = NOW(), updated_by = %s
               WHERE id = %s AND status = 'reserved'
               RETURNING *""",
            (actor, reservation["id"]),
        ).fetchone()
        before = self._reservation_view(reservation)
        after = self._reservation_view(row)
        self._audit(
            connection,
            module="stock",
            actor=actor,
            action="commit",
            resource_type="stock_reservations",
            resource_id=str(reservation["id"]),
            before=before,
            after=after,
            user_id=str(reservation["user_id"]),
            company_id=str(reservation["company_id"]),
        )
        self._emit_event(
            connection,
            module="stock",
            routing_key="stock.reservation.committed",
            actor=actor,
            aggregate_id=str(reservation["id"]),
            resource_type="stock_reservations",
            user_id=str(reservation["user_id"]),
            company_id=str(reservation["company_id"]),
            status="committed",
            payload={"order_id": str(reservation["order_id"])},
            correlation_id=correlation_id,
            causation_id=causation_id,
        )
        return row

    def confirm_checkout(
        self,
        *,
        checkout_id: str,
        user_id: str,
        payment_method: str,
        actor: str,
        idempotency_key: str,
        correlation_id: str,
        causation_id: str | None,
    ) -> dict[str, Any]:
        normalized_method = payment_method.casefold()
        request_hash = self.confirmation_request_hash(
            checkout_id=checkout_id, payment_method=normalized_method
        )
        failure_message: str | None = None
        conflict_message: str | None = None
        result: dict[str, Any] | None = None

        with self.transaction() as connection:
            checkout = connection.execute(
                """SELECT * FROM marketplace.checkout_attempts
                   WHERE id = %s AND user_id = %s
                   FOR UPDATE""",
                (checkout_id, user_id),
            ).fetchone()
            if checkout is None:
                raise MarketplaceCheckoutNotFoundError("Checkout não encontrado.")
            if checkout["status"] == "confirmed":
                return self._checkout_view(checkout)
            if checkout["status"] == "payment_failed":
                failure_message = "Checkout já falhou financeiramente; crie uma nova tentativa."
                result = self._checkout_view(checkout)
            elif checkout["status"] in {"cancelled", "expired", "rejected"}:
                conflict_message = f"Checkout em estado terminal: {checkout['status']}."
                result = self._checkout_view(checkout)
            elif normalized_method != "wallet":
                raise MarketplaceCheckoutConflictError(
                    "Somente Wallet interna é permitida neste incremento."
                )
            elif checkout.get("confirmation_idempotency_key") is not None:
                if checkout["confirmation_request_hash"] != request_hash:
                    self._audit(
                        connection,
                        module="marketplace",
                        actor=actor,
                        action="checkout_confirmation_idempotency_conflict",
                        resource_type="checkout_attempts",
                        resource_id=checkout_id,
                        before=self._checkout_view(checkout),
                        after={"request_hash_mismatch": True},
                        user_id=user_id,
                        company_id=str(checkout["company_id"]),
                    )
                    conflict_message = (
                        "A confirmação já usou outra chave ou outro corpo."
                    )
                    result = self._checkout_view(checkout)
            else:
                order = connection.execute(
                    "SELECT * FROM marketplace.orders WHERE id = %s FOR UPDATE",
                    (checkout["order_id"],),
                ).fetchone()
                if order is None:
                    raise MarketplaceCheckoutNotFoundError("Pedido do checkout não encontrado.")
                reservations: list[dict[str, Any]] = []
                for reservation_id in checkout["reservation_ids"]:
                    reservation = connection.execute(
                        "SELECT * FROM stock.stock_reservations WHERE id = %s FOR UPDATE",
                        (reservation_id,),
                    ).fetchone()
                    if reservation is None:
                        raise MarketplaceCheckoutNotFoundError(
                            "Reserva vinculada ao checkout não encontrada."
                        )
                    reservations.append(reservation)

                if checkout["expires_at"] <= datetime.now(UTC):
                    for reservation in reservations:
                        if reservation["status"] == "reserved":
                            self._release_reservation_locked(
                                connection,
                                reservation=reservation,
                                actor=actor,
                                reason="reservation_expired",
                                terminal_status="expired",
                                routing_key="stock.reservation.expired",
                                correlation_id=correlation_id,
                                causation_id=checkout_id,
                            )
                    checkout = connection.execute(
                        """UPDATE marketplace.checkout_attempts
                           SET status = 'expired', payment_status = 'cancelled',
                               confirmation_idempotency_key = %s,
                               confirmation_request_hash = %s,
                               cancelled_at = NOW(), updated_by = %s
                           WHERE id = %s
                           RETURNING *""",
                        (idempotency_key, request_hash, actor, checkout_id),
                    ).fetchone()
                    connection.execute(
                        """UPDATE marketplace.orders
                           SET status = 'cancelled', updated_at = NOW(), updated_by = %s
                           WHERE id = %s""",
                        (actor, order["id"]),
                    )
                    conflict_message = "Reserva expirada; crie um novo checkout."
                    result = self._checkout_view(checkout)
                else:
                    wallet = connection.execute(
                        """SELECT * FROM finance.wallets
                           WHERE user_id = %s AND wallet_type = 'personal' AND status = 'active'
                           ORDER BY created_at, id
                           LIMIT 1
                           FOR UPDATE""",
                        (user_id,),
                    ).fetchone()
                    if wallet is None or wallet["brl_available"] < checkout["total_brl"]:
                        for reservation in reservations:
                            if reservation["status"] == "reserved":
                                self._release_reservation_locked(
                                    connection,
                                    reservation=reservation,
                                    actor=actor,
                                    reason="payment_failed",
                                    terminal_status="released",
                                    routing_key="stock.reservation.released",
                                    correlation_id=correlation_id,
                                    causation_id=checkout_id,
                                )
                        checkout = connection.execute(
                            """UPDATE marketplace.checkout_attempts
                               SET status = 'payment_failed', payment_status = 'failed',
                                   confirmation_idempotency_key = %s,
                                   confirmation_request_hash = %s,
                                   cancelled_at = NOW(), updated_by = %s
                               WHERE id = %s
                               RETURNING *""",
                            (idempotency_key, request_hash, actor, checkout_id),
                        ).fetchone()
                        connection.execute(
                            """UPDATE marketplace.orders
                               SET status = 'cancelled', updated_at = NOW(), updated_by = %s
                               WHERE id = %s""",
                            (actor, order["id"]),
                        )
                        self._audit(
                            connection,
                            module="finance",
                            actor=actor,
                            action="payment_failed",
                            resource_type="checkout_attempts",
                            resource_id=checkout_id,
                            before=None,
                            after={"reason": "wallet_not_found_or_insufficient"},
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                        )
                        self._emit_event(
                            connection,
                            module="finance",
                            routing_key="finance.payment.failed",
                            actor=actor,
                            aggregate_id=checkout_id,
                            resource_type="checkout_attempts",
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                            status="failed",
                            payload={
                                "order_id": str(checkout["order_id"]),
                                "reason": "wallet_not_found_or_insufficient",
                            },
                            correlation_id=correlation_id,
                            causation_id=causation_id or checkout_id,
                        )
                        self._emit_event(
                            connection,
                            module="marketplace",
                            routing_key="marketplace.checkout.cancelled",
                            actor=actor,
                            aggregate_id=checkout_id,
                            resource_type="checkout_attempts",
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                            status="payment_failed",
                            payload={"order_id": str(checkout["order_id"])},
                            correlation_id=correlation_id,
                            causation_id=checkout_id,
                        )
                        failure_message = (
                            "Wallet não encontrada ou saldo insuficiente; reservas liberadas."
                        )
                        result = self._checkout_view(checkout)
                    else:
                        merchant = connection.execute(
                            "SELECT user_id FROM marketplace.stores WHERE id = %s",
                            (checkout["store_id"],),
                        ).fetchone()
                        if merchant is None:
                            raise MarketplaceCheckoutNotFoundError(
                                "Responsável da loja não encontrado."
                            )
                        escrow_id = str(uuid4())
                        ledger_id = str(uuid4())
                        total = checkout["total_brl"]
                        connection.execute(
                            """UPDATE finance.wallets
                               SET brl_available = brl_available - %s,
                                   brl_held = brl_held + %s,
                                   updated_at = NOW(), updated_by = %s
                               WHERE id = %s""",
                            (total, total, actor, wallet["id"]),
                        )
                        connection.execute(
                            """INSERT INTO finance.escrows
                               (id, user_id, wallet_id, beneficiary_user_id,
                                amount_brl, release_condition, status, created_by)
                               VALUES (%s, %s, %s, %s, %s, %s, 'held', %s)""",
                            (
                                escrow_id,
                                user_id,
                                wallet["id"],
                                merchant["user_id"],
                                total,
                                Jsonb(
                                    {
                                        "checkout_id": checkout_id,
                                        "order_id": str(checkout["order_id"]),
                                        "release_after": "delivery_or_completion",
                                        "automatic_release": False,
                                    }
                                ),
                                actor,
                            ),
                        )
                        connection.execute(
                            """INSERT INTO finance.ledger_entries
                               (id, user_id, wallet_id, currency, amount_brl,
                                entry_type, idempotency_key, metadata, created_by)
                               VALUES (%s, %s, %s, 'BRL', %s, 'escrow_hold', %s, %s, %s)""",
                            (
                                ledger_id,
                                user_id,
                                wallet["id"],
                                total,
                                idempotency_key,
                                Jsonb(
                                    {
                                        "checkout_id": checkout_id,
                                        "order_id": str(checkout["order_id"]),
                                        "escrow_id": escrow_id,
                                        "settled": False,
                                    }
                                ),
                                actor,
                            ),
                        )
                        for reservation in reservations:
                            self._commit_reservation_locked(
                                connection,
                                reservation=reservation,
                                actor=actor,
                                correlation_id=correlation_id,
                                causation_id=checkout_id,
                            )
                        order_payload = self._runtime_payload(order)
                        order_payload.update(
                            {
                                "payment_status": "authorized",
                                "payment_method": "wallet",
                                "escrow_id": escrow_id,
                                "ledger_entry_id": ledger_id,
                                "settled": False,
                                "confirmed_at": datetime.now(UTC).isoformat(),
                            }
                        )
                        connection.execute(
                            """UPDATE marketplace.orders
                               SET escrow_id = %s, status = 'paid', metadata = %s,
                                   updated_at = NOW(), updated_by = %s
                               WHERE id = %s""",
                            (
                                escrow_id,
                                Jsonb({"runtime_payload": order_payload}),
                                actor,
                                order["id"],
                            ),
                        )
                        checkout = connection.execute(
                            """UPDATE marketplace.checkout_attempts
                               SET escrow_id = %s, status = 'confirmed',
                                   payment_status = 'authorized',
                                   confirmation_idempotency_key = %s,
                                   confirmation_request_hash = %s,
                                   confirmed_at = NOW(), updated_by = %s
                               WHERE id = %s
                               RETURNING *""",
                            (
                                escrow_id,
                                idempotency_key,
                                request_hash,
                                actor,
                                checkout_id,
                            ),
                        ).fetchone()
                        cart = connection.execute(
                            "SELECT * FROM marketplace.carts WHERE id = %s FOR UPDATE",
                            (checkout["cart_id"],),
                        ).fetchone()
                        if cart is not None:
                            cart_payload = self._runtime_payload(cart)
                            cart_payload["items"] = []
                            connection.execute(
                                """UPDATE marketplace.carts
                                   SET metadata = %s, updated_at = NOW(), updated_by = %s
                                   WHERE id = %s""",
                                (
                                    Jsonb({"runtime_payload": cart_payload}),
                                    actor,
                                    cart["id"],
                                ),
                            )
                        checkout_view = self._checkout_view(checkout)
                        self._audit(
                            connection,
                            module="finance",
                            actor=actor,
                            action="payment_authorize",
                            resource_type="ledger_entries",
                            resource_id=ledger_id,
                            before=None,
                            after={
                                "checkout_id": checkout_id,
                                "order_id": str(checkout["order_id"]),
                                "amount_brl": str(total),
                                "escrow_id": escrow_id,
                                "settled": False,
                            },
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                        )
                        self._audit(
                            connection,
                            module="marketplace",
                            actor=actor,
                            action="checkout_confirm",
                            resource_type="checkout_attempts",
                            resource_id=checkout_id,
                            before=self._checkout_view(
                                {**checkout, "status": "pending_payment", "payment_status": "not_started", "escrow_id": None, "confirmed_at": None}
                            ),
                            after=checkout_view,
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                        )
                        self._emit_event(
                            connection,
                            module="finance",
                            routing_key="finance.payment.authorized",
                            actor=actor,
                            aggregate_id=ledger_id,
                            resource_type="ledger_entries",
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                            status="authorized",
                            payload={
                                "checkout_id": checkout_id,
                                "order_id": str(checkout["order_id"]),
                                "escrow_id": escrow_id,
                                "amount_brl": str(total),
                                "settled": False,
                            },
                            correlation_id=correlation_id,
                            causation_id=causation_id or checkout_id,
                        )
                        self._emit_event(
                            connection,
                            module="marketplace",
                            routing_key="marketplace.checkout.confirmed",
                            actor=actor,
                            aggregate_id=checkout_id,
                            resource_type="checkout_attempts",
                            user_id=user_id,
                            company_id=str(checkout["company_id"]),
                            status="confirmed",
                            payload={
                                "order_id": str(checkout["order_id"]),
                                "escrow_id": escrow_id,
                            },
                            correlation_id=correlation_id,
                            causation_id=checkout_id,
                        )
                        result = checkout_view

        if failure_message is not None:
            raise MarketplaceCheckoutPaymentError(failure_message)
        if conflict_message is not None:
            raise MarketplaceCheckoutIdempotencyConflictError(conflict_message)
        if result is None:
            raise MarketplaceCheckoutError("Confirmação não produziu resultado.")
        return result

    def cancel_checkout(
        self,
        *,
        checkout_id: str,
        user_id: str,
        actor: str,
        correlation_id: str,
        causation_id: str | None,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            checkout = connection.execute(
                """SELECT * FROM marketplace.checkout_attempts
                   WHERE id = %s AND user_id = %s
                   FOR UPDATE""",
                (checkout_id, user_id),
            ).fetchone()
            if checkout is None:
                raise MarketplaceCheckoutNotFoundError("Checkout não encontrado.")
            if checkout["status"] == "cancelled":
                return self._checkout_view(checkout)
            if checkout["status"] == "confirmed":
                raise MarketplaceCheckoutConflictError(
                    "Checkout confirmado não pode ser cancelado por este fluxo."
                )
            if checkout["status"] in {"payment_failed", "expired", "rejected"}:
                return self._checkout_view(checkout)
            for reservation_id in checkout["reservation_ids"]:
                reservation = connection.execute(
                    "SELECT * FROM stock.stock_reservations WHERE id = %s FOR UPDATE",
                    (reservation_id,),
                ).fetchone()
                if reservation is None:
                    raise MarketplaceCheckoutNotFoundError(
                        "Reserva vinculada ao checkout não encontrada."
                    )
                if reservation["status"] == "reserved":
                    self._release_reservation_locked(
                        connection,
                        reservation=reservation,
                        actor=actor,
                        reason="checkout_cancelled",
                        terminal_status="released",
                        routing_key="stock.reservation.released",
                        correlation_id=correlation_id,
                        causation_id=checkout_id,
                    )
            checkout = connection.execute(
                """UPDATE marketplace.checkout_attempts
                   SET status = 'cancelled', payment_status = 'cancelled',
                       cancelled_at = NOW(), updated_by = %s
                   WHERE id = %s
                   RETURNING *""",
                (actor, checkout_id),
            ).fetchone()
            connection.execute(
                """UPDATE marketplace.orders
                   SET status = 'cancelled', updated_at = NOW(), updated_by = %s
                   WHERE id = %s""",
                (actor, checkout["order_id"]),
            )
            view = self._checkout_view(checkout)
            self._audit(
                connection,
                module="marketplace",
                actor=actor,
                action="checkout_cancel",
                resource_type="checkout_attempts",
                resource_id=checkout_id,
                before=None,
                after=view,
                user_id=user_id,
                company_id=str(checkout["company_id"]),
            )
            self._emit_event(
                connection,
                module="marketplace",
                routing_key="marketplace.checkout.cancelled",
                actor=actor,
                aggregate_id=checkout_id,
                resource_type="checkout_attempts",
                user_id=user_id,
                company_id=str(checkout["company_id"]),
                status="cancelled",
                payload={"order_id": str(checkout["order_id"])},
                correlation_id=correlation_id,
                causation_id=causation_id or checkout_id,
            )
            return view
