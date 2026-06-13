BEGIN;

CREATE TABLE IF NOT EXISTS marketplace.disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    order_id UUID NOT NULL REFERENCES marketplace.orders(id),
    store_id UUID REFERENCES marketplace.stores(id),
    company_id UUID REFERENCES business.companies(id),
    offer_id TEXT,
    case_type VARCHAR(40) NOT NULL,
    subject VARCHAR(200),
    message TEXT NOT NULL,
    desired_resolution TEXT,
    status VARCHAR(40) NOT NULL DEFAULT 'open',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key TEXT UNIQUE
);

ALTER TABLE marketplace.disputes
    ADD COLUMN IF NOT EXISTS order_id UUID REFERENCES marketplace.orders(id),
    ADD COLUMN IF NOT EXISTS store_id UUID REFERENCES marketplace.stores(id),
    ADD COLUMN IF NOT EXISTS offer_id TEXT,
    ADD COLUMN IF NOT EXISTS case_type VARCHAR(40),
    ADD COLUMN IF NOT EXISTS subject VARCHAR(200),
    ADD COLUMN IF NOT EXISTS message TEXT,
    ADD COLUMN IF NOT EXISTS desired_resolution TEXT;

ALTER TABLE marketplace.disputes
    ALTER COLUMN order_id SET NOT NULL,
    ALTER COLUMN case_type SET NOT NULL,
    ALTER COLUMN message SET NOT NULL;

CREATE INDEX IF NOT EXISTS marketplace_disputes_order_created_idx
    ON marketplace.disputes (order_id, created_at DESC);

COMMIT;
