BEGIN;

CREATE TABLE IF NOT EXISTS marketplace.checkouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID NOT NULL REFERENCES business.companies(id),
    cart_id UUID NOT NULL REFERENCES marketplace.carts(id),
    order_id UUID NOT NULL UNIQUE REFERENCES marketplace.orders(id),
    store_id UUID NOT NULL REFERENCES marketplace.stores(id),
    wallet_id UUID NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'requested',
    payment_status VARCHAR(40) NOT NULL DEFAULT 'pending',
    currency VARCHAR(10) NOT NULL DEFAULT 'BRL',
    expected_total_brl NUMERIC(18, 4) NOT NULL,
    total_brl NUMERIC(18, 4) NOT NULL,
    idempotency_key VARCHAR(120) NOT NULL,
    request_hash CHAR(64) NOT NULL,
    correlation_id UUID NOT NULL,
    causation_id UUID,
    snapshot JSONB NOT NULL,
    reservation_expires_at TIMESTAMPTZ,
    failure_reason VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT marketplace_checkout_wallet_owner_fk
        FOREIGN KEY (wallet_id, user_id) REFERENCES finance.wallets(id, user_id),
    CONSTRAINT marketplace_checkout_status_allowed CHECK (
        status IN (
            'requested', 'validating_cart', 'pending_stock_reservation',
            'stock_reserved', 'pending_payment', 'confirmed', 'rejected',
            'payment_failed', 'cancelled', 'expired', 'compensated'
        )
    ),
    CONSTRAINT marketplace_checkout_payment_status_allowed CHECK (
        payment_status IN ('pending', 'authorized', 'rejected', 'cancelled', 'compensated')
    ),
    CONSTRAINT marketplace_checkout_currency_brl CHECK (currency = 'BRL'),
    CONSTRAINT marketplace_checkout_totals_nonnegative CHECK (
        expected_total_brl >= 0 AND total_brl >= 0
    ),
    CONSTRAINT marketplace_checkout_request_hash_sha256 CHECK (
        request_hash ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT marketplace_checkout_snapshot_object CHECK (
        jsonb_typeof(snapshot) = 'object'
    ),
    CONSTRAINT marketplace_checkout_idempotency_unique
        UNIQUE (user_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_checkouts_user_created
    ON marketplace.checkouts (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_checkouts_company_created
    ON marketplace.checkouts (company_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_checkouts_pending_expiration
    ON marketplace.checkouts (reservation_expires_at, id)
    WHERE status IN ('stock_reserved', 'pending_payment');
CREATE UNIQUE INDEX IF NOT EXISTS uq_marketplace_checkouts_active_cart
    ON marketplace.checkouts (cart_id)
    WHERE status IN (
        'requested', 'validating_cart', 'pending_stock_reservation',
        'stock_reserved', 'pending_payment'
    );

CREATE TABLE IF NOT EXISTS marketplace.checkout_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checkout_id UUID NOT NULL REFERENCES marketplace.checkouts(id) ON DELETE RESTRICT,
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    store_id UUID NOT NULL REFERENCES marketplace.stores(id),
    company_id UUID NOT NULL REFERENCES business.companies(id),
    inventory_item_id UUID NOT NULL REFERENCES stock.inventory_items(id),
    reservation_id UUID NOT NULL UNIQUE REFERENCES stock.stock_reservations(id),
    sku VARCHAR(120) NOT NULL,
    product_name VARCHAR(240) NOT NULL,
    quantity NUMERIC(18, 4) NOT NULL,
    unit_price_brl NUMERIC(18, 4) NOT NULL,
    subtotal_brl NUMERIC(18, 4) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'BRL',
    promotion_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    catalog_version TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT marketplace_checkout_item_quantity_positive CHECK (quantity > 0),
    CONSTRAINT marketplace_checkout_item_prices_nonnegative CHECK (
        unit_price_brl >= 0 AND subtotal_brl >= 0
    ),
    CONSTRAINT marketplace_checkout_item_currency_brl CHECK (currency = 'BRL'),
    CONSTRAINT marketplace_checkout_item_promotion_object CHECK (
        jsonb_typeof(promotion_snapshot) = 'object'
    ),
    CONSTRAINT marketplace_checkout_item_unique_product
        UNIQUE (checkout_id, product_id)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_checkout_items_checkout
    ON marketplace.checkout_items (checkout_id, created_at);

CREATE TABLE IF NOT EXISTS marketplace.checkout_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checkout_id UUID NOT NULL REFERENCES marketplace.checkouts(id) ON DELETE RESTRICT,
    operation_type VARCHAR(40) NOT NULL,
    idempotency_key VARCHAR(120) NOT NULL,
    request_hash CHAR(64) NOT NULL,
    result JSONB NOT NULL,
    actor_user_id UUID NOT NULL REFERENCES identity.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT marketplace_checkout_operation_type_allowed CHECK (
        operation_type IN ('payment_result', 'cancel', 'expire')
    ),
    CONSTRAINT marketplace_checkout_operation_hash_sha256 CHECK (
        request_hash ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT marketplace_checkout_operation_result_object CHECK (
        jsonb_typeof(result) = 'object'
    ),
    CONSTRAINT marketplace_checkout_operation_idempotency_unique
        UNIQUE (checkout_id, operation_type, idempotency_key)
);

COMMENT ON TABLE marketplace.checkouts IS
    'Checkout idempotente do Marketplace com snapshot imutável e vínculo a reservas Stock.';
COMMENT ON TABLE marketplace.checkout_items IS
    'Itens imutáveis do checkout, com preço autoritativo e reserva Stock correspondente.';
COMMENT ON TABLE marketplace.checkout_operations IS
    'Registro idempotente de resultados financeiros, cancelamentos e expiração.';

COMMIT;
