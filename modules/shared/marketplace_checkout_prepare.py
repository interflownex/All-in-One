from __future__ import annotations

from decimal import Decimal
from typing import Any

from psycopg import Connection

from .marketplace_checkout_base import (
    CheckoutConflictError,
    CheckoutNotFoundError,
    MarketplaceCheckoutBase,
)


def prepare_checkout_input(
    store: MarketplaceCheckoutBase,
    connection: Connection,
    *,
    user_id: str,
    cart_id: str,
    wallet_id: str,
    expected_total_brl: Decimal,
    currency: str,
    payment_method: str,
) -> dict[str, Any]:
    if currency != "BRL" or payment_method != "wallet":
        raise CheckoutConflictError(
            "Esta versão aceita apenas currency=BRL e payment_method=wallet."
        )

    cart = connection.execute(
        """SELECT * FROM marketplace.carts
           WHERE id = %s AND user_id = %s
             AND status = 'active' AND deleted_at IS NULL
           FOR UPDATE""",
        (cart_id, user_id),
    ).fetchone()
    if cart is None:
        raise CheckoutNotFoundError(
            "Carrinho não encontrado para o usuário autenticado."
        )
    requested_items = store._cart_items(cart)

    wallet = connection.execute(
        """SELECT id FROM finance.wallets
           WHERE id = %s AND user_id = %s
             AND status = 'active' AND deleted_at IS NULL
           FOR UPDATE""",
        (wallet_id, user_id),
    ).fetchone()
    if wallet is None:
        raise CheckoutNotFoundError(
            "Carteira ativa não encontrada para o usuário."
        )

    prepared: list[dict[str, Any]] = []
    total = Decimal("0")
    company_id: str | None = None
    store_id: str | None = None

    for requested in requested_items:
        catalog = connection.execute(
            """SELECT p.id AS product_id, p.store_id, p.sku, p.name,
                      p.price_brl, p.status AS product_status,
                      p.metadata AS product_metadata,
                      p.updated_at AS catalog_version,
                      p.deleted_at AS product_deleted_at,
                      s.company_id, s.status AS store_status,
                      s.deleted_at AS store_deleted_at
               FROM marketplace.products p
               JOIN marketplace.stores s ON s.id = p.store_id
               WHERE p.id = %s
               FOR SHARE OF p, s""",
            (requested["product_id"],),
        ).fetchone()
        if catalog is None:
            raise CheckoutNotFoundError("Produto do carrinho não foi encontrado.")

        inventory = connection.execute(
            """SELECT id AS inventory_item_id, status AS inventory_status,
                      physical_quantity, reserved_quantity, available_quantity
               FROM stock.inventory_items
               WHERE product_id = %s AND company_id = %s
                 AND status IN ('active', 'depleted')
               FOR UPDATE""",
            (catalog["product_id"], catalog["company_id"]),
        ).fetchone()
        if inventory is None:
            raise CheckoutConflictError(
                "Produto sem inventário autoritativo no Stock."
            )

        row = {**catalog, **inventory}
        if row["product_deleted_at"] or row["product_status"] not in {
            "active",
            "published",
        }:
            raise CheckoutConflictError(
                "Produto privado, inativo ou não publicado."
            )
        if row["store_deleted_at"] or row["store_status"] not in {
            "active",
            "approved",
        }:
            raise CheckoutConflictError("Loja inativa ou não aprovada.")
        if row["inventory_status"] not in {"active", "depleted"}:
            raise CheckoutConflictError("Inventário bloqueado ou arquivado.")
        if row["available_quantity"] < requested["quantity"]:
            raise CheckoutConflictError("Quantidade indisponível no Stock.")

        current_company_id = str(row["company_id"])
        current_store_id = str(row["store_id"])
        if company_id is None:
            company_id = current_company_id
            store_id = current_store_id
        elif company_id != current_company_id or store_id != current_store_id:
            raise CheckoutConflictError(
                "Esta versão aceita somente itens de uma única loja e empresa."
            )

        unit_price = store._money(row["price_brl"])
        subtotal = store._money(unit_price * requested["quantity"])
        total += subtotal
        product_payload = dict(
            (row.get("product_metadata") or {}).get("runtime_payload") or {}
        )
        prepared.append(
            {
                **requested,
                "store_id": current_store_id,
                "company_id": current_company_id,
                "inventory_item_id": str(row["inventory_item_id"]),
                "sku": row["sku"],
                "name": row["name"],
                "unit_price_brl": unit_price,
                "subtotal_brl": subtotal,
                "promotion": product_payload.get("promotion")
                if isinstance(product_payload.get("promotion"), dict)
                else {},
                "catalog_version": row["catalog_version"],
            }
        )

    if company_id is None or store_id is None:
        raise CheckoutConflictError("Carrinho vazio não pode ser confirmado.")
    total = store._money(total)
    if total != store._money(expected_total_brl):
        raise CheckoutConflictError(
            "Preço divergente: esperado "
            f"{store._money(expected_total_brl)}, atual {total}."
        )

    snapshot_items = [
        {
            "product_id": item["product_id"],
            "store_id": item["store_id"],
            "company_id": item["company_id"],
            "inventory_item_id": item["inventory_item_id"],
            "sku": item["sku"],
            "name": item["name"],
            "quantity": store._decimal_text(item["quantity"]),
            "unit_price_brl": store._decimal_text(item["unit_price_brl"]),
            "subtotal_brl": store._decimal_text(item["subtotal_brl"]),
            "currency": "BRL",
            "promotion": item["promotion"],
            "catalog_version": item["catalog_version"].isoformat(),
        }
        for item in prepared
    ]
    return {
        "prepared": prepared,
        "snapshot_items": snapshot_items,
        "company_id": company_id,
        "store_id": store_id,
        "total": total,
    }
