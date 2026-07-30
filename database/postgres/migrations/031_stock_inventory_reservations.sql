BEGIN;

CREATE TABLE IF NOT EXISTS stock.inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID NOT NULL REFERENCES business.companies(id),
    warehouse_id UUID,
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    sku VARCHAR(120) NOT NULL,
    physical_quantity NUMERIC(18, 4) NOT NULL DEFAULT 0,
    reserved_quantity NUMERIC(18, 4) NOT NULL DEFAULT 0,
    available_quantity NUMERIC(18, 4)
        GENERATED ALWAYS AS (physical_quantity - reserved_quantity) STORED,
    version BIGINT NOT NULL DEFAULT 0,
    status VARCHAR(40) NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT stock_inventory_physical_nonnegative
        CHECK (physical_quantity >= 0),
    CONSTRAINT stock_inventory_reserved_nonnegative
        CHECK (reserved_quantity >= 0),
    CONSTRAINT stock_inventory_reserved_not_above_physical
        CHECK (reserved_quantity <= physical_quantity),
    CONSTRAINT stock_inventory_version_nonnegative
        CHECK (version >= 0),
    CONSTRAINT stock_inventory_status_allowed
        CHECK (status IN ('active', 'blocked', 'depleted', 'archived')),
    CONSTRAINT stock_inventory_metadata_object
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT stock_inventory_company_warehouse_sku_unique
        UNIQUE NULLS NOT DISTINCT (company_id, warehouse_id, sku)
);

CREATE OR REPLACE FUNCTION stock.derive_inventory_availability_status()
RETURNS trigger AS $$
BEGIN
    IF NEW.status IN ('active', 'depleted') THEN
        NEW.status := CASE
            WHEN NEW.physical_quantity - NEW.reserved_quantity = 0 THEN 'depleted'
            ELSE 'active'
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS stock_inventory_availability_status ON stock.inventory_items;
CREATE TRIGGER stock_inventory_availability_status
BEFORE INSERT OR UPDATE OF physical_quantity, reserved_quantity, status
ON stock.inventory_items
FOR EACH ROW
EXECUTE FUNCTION stock.derive_inventory_availability_status();

CREATE INDEX IF NOT EXISTS idx_stock_inventory_product_company
    ON stock.inventory_items (product_id, company_id, status);

CREATE INDEX IF NOT EXISTS idx_stock_inventory_company_available
    ON stock.inventory_items (company_id, available_quantity DESC)
    WHERE status = 'active';

CREATE TABLE IF NOT EXISTS stock.stock_reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID NOT NULL REFERENCES business.companies(id),
    order_id UUID NOT NULL,
    inventory_item_id UUID NOT NULL REFERENCES stock.inventory_items(id),
    quantity NUMERIC(18, 4) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    idempotency_key VARCHAR(160) NOT NULL,
    request_hash CHAR(64) NOT NULL,
    correlation_id UUID NOT NULL,
    causation_id UUID,
    expires_at TIMESTAMPTZ NOT NULL,
    committed_at TIMESTAMPTZ,
    released_at TIMESTAMPTZ,
    release_reason VARCHAR(500),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT stock_reservation_quantity_positive CHECK (quantity > 0),
    CONSTRAINT stock_reservation_status_allowed CHECK (
        status IN ('pending', 'reserved', 'rejected', 'committed', 'released', 'expired')
    ),
    CONSTRAINT stock_reservation_request_hash_sha256
        CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    CONSTRAINT stock_reservation_terminal_timestamps CHECK (
        (status <> 'committed' OR committed_at IS NOT NULL)
        AND (status NOT IN ('released', 'expired') OR released_at IS NOT NULL)
    ),
    CONSTRAINT stock_reservation_metadata_object
        CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT stock_reservation_idempotency_scope_unique
        UNIQUE (user_id, company_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_stock_reservations_inventory_status
    ON stock.stock_reservations (inventory_item_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_stock_reservations_company_order
    ON stock.stock_reservations (company_id, order_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_stock_reservations_expiration
    ON stock.stock_reservations (expires_at, id)
    WHERE status = 'reserved';

COMMENT ON TABLE stock.inventory_items IS
    'Fonte autoritativa de saldo físico, reservado e disponível do Stock.';

COMMENT ON TABLE stock.stock_reservations IS
    'Reservas transacionais idempotentes vinculadas ao checkout do Marketplace.';

COMMIT;
