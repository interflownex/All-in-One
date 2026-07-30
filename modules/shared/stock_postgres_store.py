from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from psycopg import Connection
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb

from .correlation import get_correlation_id
from .event_contract import EVENT_SCHEMA_VERSION, build_event_envelope
from .postgres_store import BasePostgresStore
from .store import DuplicateValueError


class StockNotFoundError(RuntimeError):
    """Recurso Stock não localizado no escopo informado."""


class StockConflictError(RuntimeError):
    """Transição ou versão incompatível com o estado atual."""


class StockIdempotencyConflictError(StockConflictError):
    """A mesma chave idempotente foi reutilizada com outro corpo."""


class StockPostgresStore(BasePostgresStore):
    """Adaptador Stock tipado com inventário e reservas PostgreSQL transacionais."""

    module = "stock"
    backend = "postgres_stock_typed_store"
    tables = {
        "suppliers": "stock.suppliers",
        "catalog_products": "stock.catalog_products",
        "price_rules": "stock.price_rules",
        "supplier_orders": "stock.supplier_orders",
        "discount_quotes": "stock.discount_quotes",
        "inventory_items": "stock.inventory_items",
        "stock_reservations": "stock.stock_reservations",
    }
    soft_deletable = frozenset(
        ["suppliers", "catalog_products", "price_rules", "supplier_orders"]
    )

    @staticmethod
    def _decimal_text(value: Decimal | Any) -> str:
        return format(Decimal(str(value)).normalize(), "f")

    @classmethod
    def reservation_request_hash(
        cls,
        *,
        inventory_item_id: str,
        order_id: str,
        quantity: Decimal,
        expires_in_seconds: int,
    ) -> str:
        normalized = json.dumps(
            {
                "expires_in_seconds": expires_in_seconds,
                "inventory_item_id": inventory_item_id,
                "order_id": order_id,
                "quantity": cls._decimal_text(quantity),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @classmethod
    def _inventory_view(cls, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "company_id": str(row["company_id"]),
            "warehouse_id": str(row["warehouse_id"]) if row.get("warehouse_id") else None,
            "product_id": str(row["product_id"]),
            "sku": row["sku"],
            "physical_quantity": cls._decimal_text(row["physical_quantity"]),
            "reserved_quantity": cls._decimal_text(row["reserved_quantity"]),
            "available_quantity": cls._decimal_text(row["available_quantity"]),
            "version": int(row["version"]),
            "status": row["status"],
            "metadata": dict(row.get("metadata") or {}),
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }

    @classmethod
    def _reservation_view(cls, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "reservation_id": str(row["id"]),
            "user_id": str(row["user_id"]),
            "company_id": str(row["company_id"]),
            "order_id": str(row["order_id"]),
            "inventory_item_id": str(row["inventory_item_id"]),
            "quantity": cls._decimal_text(row["quantity"]),
            "status": row["status"],
            "expires_at": row["expires_at"].isoformat(),
            "committed_at": row["committed_at"].isoformat()
            if row.get("committed_at")
            else None,
            "released_at": row["released_at"].isoformat()
            if row.get("released_at")
            else None,
            "release_reason": row.get("release_reason"),
            "correlation_id": str(row["correlation_id"]),
            "causation_id": str(row["causation_id"])
            if row.get("causation_id")
            else None,
            "created_at": row["created_at"].isoformat(),
            "updated_at": row["updated_at"].isoformat(),
        }

    @classmethod
    def _event_item(cls, row: dict[str, Any]) -> dict[str, Any]:
        view = cls._reservation_view(row)
        return {
            "id": view["reservation_id"],
            "resource_type": "stock_reservations",
            "user_id": view["user_id"],
            "entity_id": view["company_id"],
            "status": view["status"],
            "idempotency_key": row["idempotency_key"],
            "payload": {
                "inventory_item_id": view["inventory_item_id"],
                "order_id": view["order_id"],
                "quantity": view["quantity"],
                "status": view["status"],
                "expires_at": view["expires_at"],
                "release_reason": view["release_reason"],
            },
        }

    def _emit_reservation_event(
        self,
        connection: Connection,
        routing_key: str,
        actor: str,
        row: dict[str, Any],
    ) -> None:
        item = self._event_item(row)
        envelope = build_event_envelope(
            module=self.module,
            routing_key=routing_key,
            actor_user_id=actor,
            item=item,
            correlation_id=get_correlation_id(),
            causation_id=str(row["causation_id"]) if row.get("causation_id") else None,
        )
        connection.execute(
            """INSERT INTO audit.domain_events
               (id, user_id, actor_user_id, entity_id, routing_key, aggregate_type,
                aggregate_id, correlation_id, schema_version, payload, created_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                envelope["event_id"],
                item["user_id"],
                actor,
                item["entity_id"],
                routing_key,
                item["resource_type"],
                item["id"],
                envelope["correlation_id"],
                EVENT_SCHEMA_VERSION,
                Jsonb(envelope),
                actor,
            ),
        )

    def create_inventory_item(
        self,
        *,
        user_id: str,
        company_id: str,
        warehouse_id: str | None,
        product_id: str,
        sku: str,
        physical_quantity: Decimal,
        actor: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        item_id = str(uuid4())
        try:
            with self.transaction() as connection:
                product = connection.execute(
                    """SELECT p.id
                       FROM marketplace.products p
                       JOIN marketplace.stores s ON s.id = p.store_id
                       WHERE p.id = %s AND s.company_id = %s AND p.sku = %s
                         AND p.deleted_at IS NULL AND s.deleted_at IS NULL""",
                    (product_id, company_id, sku),
                ).fetchone()
                if product is None:
                    raise StockNotFoundError(
                        "Produto Marketplace não pertence à empresa e ao SKU informados."
                    )
                row = connection.execute(
                    """INSERT INTO stock.inventory_items
                       (id, user_id, company_id, warehouse_id, product_id, sku,
                        physical_quantity, reserved_quantity, status, metadata,
                        created_by, updated_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 'active', %s, %s, %s)
                       RETURNING *""",
                    (
                        item_id,
                        user_id,
                        company_id,
                        warehouse_id,
                        product_id,
                        sku,
                        physical_quantity,
                        Jsonb(metadata),
                        actor,
                        actor,
                    ),
                ).fetchone()
                view = self._inventory_view(row)
                self._audit(
                    connection,
                    actor,
                    "create",
                    "inventory_items",
                    item_id,
                    None,
                    view,
                    user_id,
                    company_id,
                )
                return view
        except UniqueViolation as exc:
            raise DuplicateValueError("inventory_items") from exc

    def adjust_inventory_item(
        self,
        *,
        inventory_item_id: str,
        company_id: str,
        expected_version: int,
        physical_quantity: Decimal,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            current = connection.execute(
                """SELECT * FROM stock.inventory_items
                   WHERE id = %s AND company_id = %s
                   FOR UPDATE""",
                (inventory_item_id, company_id),
            ).fetchone()
            if current is None:
                raise StockNotFoundError("Item de inventário não encontrado.")
            if int(current["version"]) != expected_version:
                raise StockConflictError(
                    f"Versão divergente: esperado {expected_version}, atual {current['version']}."
                )
            if physical_quantity < current["reserved_quantity"]:
                raise StockConflictError(
                    "Quantidade física não pode ficar abaixo da quantidade reservada."
                )
            row = connection.execute(
                """UPDATE stock.inventory_items
                   SET physical_quantity = %s,
                       version = version + 1,
                       status = CASE WHEN %s = reserved_quantity THEN 'depleted' ELSE 'active' END,
                       metadata = jsonb_set(metadata, '{last_adjustment_reason}', to_jsonb(%s::text), true),
                       updated_at = NOW(),
                       updated_by = %s
                   WHERE id = %s AND company_id = %s AND version = %s
                   RETURNING *""",
                (
                    physical_quantity,
                    physical_quantity,
                    reason,
                    actor,
                    inventory_item_id,
                    company_id,
                    expected_version,
                ),
            ).fetchone()
            if row is None:
                raise StockConflictError("Inventário alterado concorrentemente.")
            before = self._inventory_view(current)
            after = self._inventory_view(row)
            self._audit(
                connection,
                actor,
                "adjust",
                "inventory_items",
                inventory_item_id,
                before,
                after,
                str(current["user_id"]),
                company_id,
            )
            return after

    def get_reservation(self, reservation_id: str) -> dict[str, Any] | None:
        row = self.connection.execute(
            "SELECT * FROM stock.stock_reservations WHERE id = %s",
            (reservation_id,),
        ).fetchone()
        return self._reservation_view(row) if row else None

    def reserve_inventory(
        self,
        *,
        user_id: str,
        company_id: str,
        inventory_item_id: str,
        order_id: str,
        quantity: Decimal,
        expires_in_seconds: int,
        actor: str,
        idempotency_key: str,
        correlation_id: str,
        causation_id: str | None,
    ) -> dict[str, Any]:
        request_hash = self.reservation_request_hash(
            inventory_item_id=inventory_item_id,
            order_id=order_id,
            quantity=quantity,
            expires_in_seconds=expires_in_seconds,
        )
        idempotency_conflict = False
        conflict_reservation_id: str | None = None
        with self.transaction() as connection:
            previous = connection.execute(
                """SELECT * FROM stock.stock_reservations
                   WHERE user_id = %s AND company_id = %s AND idempotency_key = %s
                   FOR UPDATE""",
                (user_id, company_id, idempotency_key),
            ).fetchone()
            if previous is not None:
                if previous["request_hash"] == request_hash:
                    return self._reservation_view(previous)
                conflict_reservation_id = str(previous["id"])
                self._audit(
                    connection,
                    actor,
                    "idempotency_conflict",
                    "stock_reservations",
                    conflict_reservation_id,
                    self._reservation_view(previous),
                    {"request_hash_mismatch": True},
                    user_id,
                    company_id,
                )
                idempotency_conflict = True
            else:
                inventory = connection.execute(
                    """SELECT * FROM stock.inventory_items
                       WHERE id = %s AND company_id = %s AND status IN ('active', 'depleted')
                       FOR UPDATE""",
                    (inventory_item_id, company_id),
                ).fetchone()
                if inventory is None:
                    raise StockNotFoundError("Item de inventário não encontrado.")
                reservation_id = str(uuid4())
                expires_at = datetime.now(UTC) + timedelta(seconds=expires_in_seconds)
                available = inventory["physical_quantity"] - inventory["reserved_quantity"]
                status = "reserved" if available >= quantity else "rejected"
                release_reason = None if status == "reserved" else "insufficient_stock"
                if status == "reserved":
                    connection.execute(
                        """UPDATE stock.inventory_items
                           SET reserved_quantity = reserved_quantity + %s,
                               version = version + 1,
                               status = CASE
                                   WHEN physical_quantity = reserved_quantity + %s THEN 'depleted'
                                   ELSE 'active'
                               END,
                               updated_at = NOW(), updated_by = %s
                           WHERE id = %s AND company_id = %s
                           RETURNING id""",
                        (quantity, quantity, actor, inventory_item_id, company_id),
                    ).fetchone()
                row = connection.execute(
                    """INSERT INTO stock.stock_reservations
                       (id, user_id, company_id, order_id, inventory_item_id, quantity,
                        status, idempotency_key, request_hash, correlation_id, causation_id,
                        expires_at, release_reason, metadata, created_by, updated_by)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                               %s, %s, '{}'::jsonb, %s, %s)
                       RETURNING *""",
                    (
                        reservation_id,
                        user_id,
                        company_id,
                        order_id,
                        inventory_item_id,
                        quantity,
                        status,
                        idempotency_key,
                        request_hash,
                        correlation_id,
                        causation_id,
                        expires_at,
                        release_reason,
                        actor,
                        actor,
                    ),
                ).fetchone()
                view = self._reservation_view(row)
                self._audit(
                    connection,
                    actor,
                    "reserve" if status == "reserved" else "reject",
                    "stock_reservations",
                    reservation_id,
                    None,
                    view,
                    user_id,
                    company_id,
                )
                self._emit_reservation_event(
                    connection,
                    "stock.reservation.created"
                    if status == "reserved"
                    else "stock.reservation.rejected",
                    actor,
                    row,
                )
                return view
        if idempotency_conflict:
            raise StockIdempotencyConflictError(
                f"Chave idempotente já usada por {conflict_reservation_id} com outro corpo."
            )
        raise RuntimeError("Reserva não produziu resultado.")

    def commit_reservation(
        self,
        *,
        reservation_id: str,
        expected_user_id: str,
        actor: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            reservation = connection.execute(
                "SELECT * FROM stock.stock_reservations WHERE id = %s FOR UPDATE",
                (reservation_id,),
            ).fetchone()
            if reservation is None or str(reservation["user_id"]) != expected_user_id:
                raise StockNotFoundError("Reserva não encontrada.")
            if reservation["status"] == "committed":
                return self._reservation_view(reservation)
            if reservation["status"] != "reserved":
                raise StockConflictError(
                    f"Reserva em estado terminal ou incompatível: {reservation['status']}."
                )
            inventory = connection.execute(
                "SELECT * FROM stock.inventory_items WHERE id = %s FOR UPDATE",
                (reservation["inventory_item_id"],),
            ).fetchone()
            if inventory is None:
                raise StockNotFoundError("Inventário da reserva não encontrado.")
            if reservation["expires_at"] <= datetime.now(UTC):
                row = self._expire_locked(connection, reservation, inventory, actor)
                return self._reservation_view(row)
            quantity = reservation["quantity"]
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
                   RETURNING *""",
                (
                    quantity,
                    quantity,
                    quantity,
                    actor,
                    inventory["id"],
                    quantity,
                    quantity,
                ),
            ).fetchone()
            if updated_inventory is None:
                raise StockConflictError("Saldo reservado inconsistente no inventário.")
            row = connection.execute(
                """UPDATE stock.stock_reservations
                   SET status = 'committed', committed_at = NOW(), updated_at = NOW(), updated_by = %s
                   WHERE id = %s AND status = 'reserved'
                   RETURNING *""",
                (actor, reservation_id),
            ).fetchone()
            before = self._reservation_view(reservation)
            after = self._reservation_view(row)
            self._audit(
                connection,
                actor,
                "commit",
                "stock_reservations",
                reservation_id,
                before,
                after,
                expected_user_id,
                str(reservation["company_id"]),
            )
            self._emit_reservation_event(
                connection, "stock.reservation.committed", actor, row
            )
            return after

    def release_reservation(
        self,
        *,
        reservation_id: str,
        expected_user_id: str,
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        with self.transaction() as connection:
            reservation = connection.execute(
                "SELECT * FROM stock.stock_reservations WHERE id = %s FOR UPDATE",
                (reservation_id,),
            ).fetchone()
            if reservation is None or str(reservation["user_id"]) != expected_user_id:
                raise StockNotFoundError("Reserva não encontrada.")
            if reservation["status"] == "released":
                return self._reservation_view(reservation)
            if reservation["status"] != "reserved":
                raise StockConflictError(
                    f"Reserva em estado terminal ou incompatível: {reservation['status']}."
                )
            inventory = connection.execute(
                "SELECT * FROM stock.inventory_items WHERE id = %s FOR UPDATE",
                (reservation["inventory_item_id"],),
            ).fetchone()
            if inventory is None:
                raise StockNotFoundError("Inventário da reserva não encontrado.")
            quantity = reservation["quantity"]
            updated_inventory = connection.execute(
                """UPDATE stock.inventory_items
                   SET reserved_quantity = reserved_quantity - %s,
                       version = version + 1,
                       status = 'active', updated_at = NOW(), updated_by = %s
                   WHERE id = %s AND reserved_quantity >= %s
                   RETURNING id""",
                (quantity, actor, inventory["id"], quantity),
            ).fetchone()
            if updated_inventory is None:
                raise StockConflictError("Saldo reservado inconsistente no inventário.")
            row = connection.execute(
                """UPDATE stock.stock_reservations
                   SET status = 'released', released_at = NOW(), release_reason = %s,
                       updated_at = NOW(), updated_by = %s
                   WHERE id = %s AND status = 'reserved'
                   RETURNING *""",
                (reason, actor, reservation_id),
            ).fetchone()
            before = self._reservation_view(reservation)
            after = self._reservation_view(row)
            self._audit(
                connection,
                actor,
                "release",
                "stock_reservations",
                reservation_id,
                before,
                after,
                expected_user_id,
                str(reservation["company_id"]),
            )
            self._emit_reservation_event(
                connection, "stock.reservation.released", actor, row
            )
            return after

    def _expire_locked(
        self,
        connection: Connection,
        reservation: dict[str, Any],
        inventory: dict[str, Any],
        actor: str,
    ) -> dict[str, Any]:
        quantity = reservation["quantity"]
        updated_inventory = connection.execute(
            """UPDATE stock.inventory_items
               SET reserved_quantity = reserved_quantity - %s,
                   version = version + 1,
                   status = 'active', updated_at = NOW(), updated_by = %s
               WHERE id = %s AND reserved_quantity >= %s
               RETURNING id""",
            (quantity, actor, inventory["id"], quantity),
        ).fetchone()
        if updated_inventory is None:
            raise StockConflictError("Saldo reservado inconsistente durante expiração.")
        row = connection.execute(
            """UPDATE stock.stock_reservations
               SET status = 'expired', released_at = NOW(),
                   release_reason = 'reservation_expired', updated_at = NOW(), updated_by = %s
               WHERE id = %s AND status = 'reserved'
               RETURNING *""",
            (actor, reservation["id"]),
        ).fetchone()
        before = self._reservation_view(reservation)
        after = self._reservation_view(row)
        self._audit(
            connection,
            actor,
            "expire",
            "stock_reservations",
            str(reservation["id"]),
            before,
            after,
            str(reservation["user_id"]),
            str(reservation["company_id"]),
        )
        self._emit_reservation_event(
            connection, "stock.reservation.expired", actor, row
        )
        return row

    def expire_due_reservations(self, *, actor: str, limit: int = 100) -> list[dict[str, Any]]:
        expired: list[dict[str, Any]] = []
        with self.transaction() as connection:
            reservations = connection.execute(
                """SELECT * FROM stock.stock_reservations
                   WHERE status = 'reserved' AND expires_at <= NOW()
                   ORDER BY expires_at, id
                   FOR UPDATE SKIP LOCKED
                   LIMIT %s""",
                (limit,),
            ).fetchall()
            for reservation in reservations:
                inventory = connection.execute(
                    "SELECT * FROM stock.inventory_items WHERE id = %s FOR UPDATE",
                    (reservation["inventory_item_id"],),
                ).fetchone()
                if inventory is None:
                    raise StockNotFoundError("Inventário de reserva vencida não encontrado.")
                row = self._expire_locked(connection, reservation, inventory, actor)
                expired.append(self._reservation_view(row))
        return expired

    def _insert(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        user_id: str,
        entity_id: str | None,
        status: str,
        payload: dict[str, Any],
        actor: str,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        return self._insert_generic(
            connection,
            resource_type,
            resource_id,
            user_id,
            entity_id,
            status,
            payload,
            actor,
            idempotency_key,
        )

    def _update(
        self,
        connection: Connection,
        resource_type: str,
        resource_id: str,
        payload: dict[str, Any],
        status: str,
        actor: str,
    ) -> dict[str, Any]:
        return self._update_generic(
            connection, resource_type, resource_id, payload, status, actor
        )
