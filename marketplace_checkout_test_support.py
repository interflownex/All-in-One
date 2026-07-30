from __future__ import annotations

import os
from decimal import Decimal
from uuid import UUID, uuid4

import psycopg
from psycopg.types.json import Jsonb

from modules.shared.correlation import set_correlation_id
from modules.shared.marketplace_checkout_postgres_store import (
    MarketplaceCheckoutPostgresStore,
)

POSTGRES_DSN = os.getenv("ALL_IN_ONE_MARKETPLACE_POSTGRES_TEST_DSN") or os.getenv(
    "ALL_IN_ONE_STOCK_POSTGRES_TEST_DSN"
)


def _phone(nonce: str) -> str:
    return f"+55119{str(int(nonce[:7], 16)).zfill(8)[-8:]}"


def _seed_user(connection: psycopg.Connection, user_id: UUID) -> None:
    nonce = uuid4().hex[:12]
    connection.execute(
        """INSERT INTO identity.users
           (id, full_name, cpf_document, birth_date, email, phone_e164,
            password_hash, face_hash, liveness_score, terms_accepted_at,
            lgpd_consent_at, status)
           VALUES (%s, %s, %s, DATE '1990-01-01', %s, %s, %s, %s,
                   0.9900, NOW(), NOW(), 'active')""",
        (
            user_id,
            f"Usuário Checkout {nonce}",
            f"CPF-{nonce}",
            f"{nonce}@example.test",
            _phone(nonce),
            f"hash-{nonce}",
            f"face-{nonce}",
        ),
    )


def _seed_company_catalog(
    connection: psycopg.Connection,
    *,
    owner_id: UUID,
    company_id: UUID,
    store_id: UUID,
    product_id: UUID,
    sku: str,
    price_brl: Decimal,
) -> None:
    nonce = uuid4().hex[:12]
    connection.execute(
        """INSERT INTO business.companies
           (id, user_id, cnpj, root_cnpj, legal_name,
            legal_representative_user_id, status, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)""",
        (
            company_id,
            owner_id,
            nonce[:12],
            nonce[:8],
            f"Empresa Checkout {nonce}",
            owner_id,
            owner_id,
            owner_id,
        ),
    )
    connection.execute(
        """INSERT INTO marketplace.stores
           (id, user_id, company_id, name, status, created_by, updated_by)
           VALUES (%s, %s, %s, %s, 'active', %s, %s)""",
        (store_id, owner_id, company_id, f"Loja {nonce}", owner_id, owner_id),
    )
    connection.execute(
        """INSERT INTO marketplace.products
           (id, user_id, store_id, sku, name, price_brl, stock_quantity,
            status, metadata, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, %s, 999, 'published', %s, %s, %s)""",
        (
            product_id,
            owner_id,
            store_id,
            sku,
            f"Produto {nonce}",
            price_brl,
            Jsonb(
                {
                    "runtime_payload": {
                        "promotion": {
                            "active": True,
                            "discount_percent": "0",
                        }
                    }
                }
            ),
            owner_id,
            owner_id,
        ),
    )


def _seed_buyer_workspace(
    connection: psycopg.Connection,
    *,
    buyer_id: UUID,
    company_id: UUID,
    product_id: UUID,
    quantity: int,
) -> tuple[UUID, UUID]:
    cart_id = uuid4()
    wallet_id = uuid4()
    connection.execute(
        """INSERT INTO marketplace.carts
           (id, user_id, company_id, status, metadata, created_by, updated_by)
           VALUES (%s, %s, %s, 'active', %s, %s, %s)""",
        (
            cart_id,
            buyer_id,
            company_id,
            Jsonb(
                {
                    "runtime_payload": {
                        "cart_type": "cart",
                        "items": [
                            {
                                "product_id": str(product_id),
                                "quantity": quantity,
                            }
                        ],
                    }
                }
            ),
            buyer_id,
            buyer_id,
        ),
    )
    connection.execute(
        """INSERT INTO finance.wallets
           (id, user_id, wallet_type, brl_available, brl_held, status,
            created_by, updated_by)
           VALUES (%s, %s, 'personal', 1000, 0, 'active', %s, %s)""",
        (wallet_id, buyer_id, buyer_id, buyer_id),
    )
    return cart_id, wallet_id


def _seed_inventory(
    connection: psycopg.Connection,
    *,
    owner_id: UUID,
    company_id: UUID,
    product_id: UUID,
    sku: str,
    quantity: Decimal,
) -> UUID:
    inventory_id = uuid4()
    connection.execute(
        """INSERT INTO stock.inventory_items
           (id, user_id, company_id, product_id, sku, physical_quantity,
            reserved_quantity, status, metadata, created_by, updated_by)
           VALUES (%s, %s, %s, %s, %s, %s, 0, 'active', '{}'::jsonb,
                   %s, %s)""",
        (
            inventory_id,
            owner_id,
            company_id,
            product_id,
            sku,
            quantity,
            owner_id,
            owner_id,
        ),
    )
    return inventory_id


def _context(
    *,
    stock_quantity: Decimal = Decimal("5"),
    cart_quantity: int = 2,
    price_brl: Decimal = Decimal("19.90"),
) -> dict[str, UUID | Decimal | str]:
    owner_id = uuid4()
    buyer_id = uuid4()
    other_user_id = uuid4()
    company_id = uuid4()
    store_id = uuid4()
    product_id = uuid4()
    sku = f"SKU-{uuid4().hex[:12]}"
    with psycopg.connect(POSTGRES_DSN) as connection:
        _seed_user(connection, owner_id)
        _seed_user(connection, buyer_id)
        _seed_user(connection, other_user_id)
        _seed_company_catalog(
            connection,
            owner_id=owner_id,
            company_id=company_id,
            store_id=store_id,
            product_id=product_id,
            sku=sku,
            price_brl=price_brl,
        )
        cart_id, wallet_id = _seed_buyer_workspace(
            connection,
            buyer_id=buyer_id,
            company_id=company_id,
            product_id=product_id,
            quantity=cart_quantity,
        )
        inventory_id = _seed_inventory(
            connection,
            owner_id=owner_id,
            company_id=company_id,
            product_id=product_id,
            sku=sku,
            quantity=stock_quantity,
        )
    return {
        "owner_id": owner_id,
        "buyer_id": buyer_id,
        "other_user_id": other_user_id,
        "company_id": company_id,
        "store_id": store_id,
        "product_id": product_id,
        "cart_id": cart_id,
        "wallet_id": wallet_id,
        "inventory_id": inventory_id,
        "price_brl": price_brl,
        "total_brl": price_brl * cart_quantity,
    }


def _create_checkout(
    store: MarketplaceCheckoutPostgresStore,
    context: dict[str, UUID | Decimal | str],
    *,
    key: str,
    expected_total_brl: Decimal | None = None,
    user_id: UUID | None = None,
    expires_in_seconds: int = 900,
) -> dict[str, object]:
    correlation_id = uuid4()
    set_correlation_id(str(correlation_id))
    return store.create_checkout(
        user_id=str(user_id or context["buyer_id"]),
        cart_id=str(context["cart_id"]),
        wallet_id=str(context["wallet_id"]),
        expected_total_brl=expected_total_brl
        if expected_total_brl is not None
        else Decimal(str(context["total_brl"])),
        currency="BRL",
        payment_method="wallet",
        actor=str(user_id or context["buyer_id"]),
        idempotency_key=key,
        correlation_id=str(correlation_id),
        causation_id=None,
        expires_in_seconds=expires_in_seconds,
    )
