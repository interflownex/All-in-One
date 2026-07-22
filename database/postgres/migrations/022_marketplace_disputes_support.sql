BEGIN;

DO $$
BEGIN
    IF to_regclass('marketplace.disputes') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1
           FROM information_schema.columns
           WHERE table_schema = 'marketplace'
             AND table_name = 'disputes'
             AND column_name = 'order_id'
       )
    THEN
        IF to_regclass('marketplace.disputes_legacy_catalog') IS NOT NULL THEN
            RAISE EXCEPTION
                'marketplace.disputes uses the legacy catalog schema and marketplace.disputes_legacy_catalog already exists';
        END IF;

        ALTER TABLE marketplace.disputes RENAME TO disputes_legacy_catalog;
    END IF;
END $$;

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

-- Compatibilidade com ambientes que executaram a migration 013 antiga, na
-- qual disputes era criada como tabela generica.
ALTER TABLE marketplace.disputes
    ADD COLUMN IF NOT EXISTS order_id UUID REFERENCES marketplace.orders(id),
    ADD COLUMN IF NOT EXISTS store_id UUID REFERENCES marketplace.stores(id),
    ADD COLUMN IF NOT EXISTS offer_id TEXT,
    ADD COLUMN IF NOT EXISTS case_type VARCHAR(40),
    ADD COLUMN IF NOT EXISTS subject VARCHAR(200),
    ADD COLUMN IF NOT EXISTS message TEXT,
    ADD COLUMN IF NOT EXISTS desired_resolution TEXT;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'marketplace_disputes_order_required'
          AND conrelid = 'marketplace.disputes'::regclass
    ) THEN
        ALTER TABLE marketplace.disputes
            ADD CONSTRAINT marketplace_disputes_order_required
            CHECK (order_id IS NOT NULL) NOT VALID;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'marketplace_disputes_type_required'
          AND conrelid = 'marketplace.disputes'::regclass
    ) THEN
        ALTER TABLE marketplace.disputes
            ADD CONSTRAINT marketplace_disputes_type_required
            CHECK (case_type IS NOT NULL) NOT VALID;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'marketplace_disputes_message_required'
          AND conrelid = 'marketplace.disputes'::regclass
    ) THEN
        ALTER TABLE marketplace.disputes
            ADD CONSTRAINT marketplace_disputes_message_required
            CHECK (message IS NOT NULL) NOT VALID;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS marketplace_disputes_order_created_idx
    ON marketplace.disputes (order_id, created_at DESC);

COMMIT;
