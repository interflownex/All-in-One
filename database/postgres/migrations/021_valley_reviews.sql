BEGIN;

DO $$
BEGIN
    IF to_regclass('marketplace.reviews') IS NOT NULL
       AND NOT EXISTS (
           SELECT 1
           FROM information_schema.columns
           WHERE table_schema = 'marketplace'
             AND table_name = 'reviews'
             AND column_name = 'order_id'
       )
    THEN
        IF to_regclass('marketplace.reviews_legacy_catalog') IS NOT NULL THEN
            RAISE EXCEPTION
                'marketplace.reviews uses the legacy catalog schema and marketplace.reviews_legacy_catalog already exists';
        END IF;

        ALTER TABLE marketplace.reviews RENAME TO reviews_legacy_catalog;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS marketplace.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    order_id UUID NOT NULL REFERENCES marketplace.orders(id),
    store_id UUID REFERENCES marketplace.stores(id),
    offer_id TEXT,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    moderation_status VARCHAR(40) NOT NULL DEFAULT 'published',
    status VARCHAR(40) NOT NULL DEFAULT 'published',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key TEXT,
    UNIQUE (order_id, user_id),
    UNIQUE (idempotency_key)
);

-- Compatibilidade com ambientes que executaram a migration 013 antiga, na
-- qual reviews era criada como tabela generica.
ALTER TABLE marketplace.reviews
    ADD COLUMN IF NOT EXISTS order_id UUID REFERENCES marketplace.orders(id),
    ADD COLUMN IF NOT EXISTS store_id UUID REFERENCES marketplace.stores(id),
    ADD COLUMN IF NOT EXISTS offer_id TEXT,
    ADD COLUMN IF NOT EXISTS rating SMALLINT,
    ADD COLUMN IF NOT EXISTS comment TEXT,
    ADD COLUMN IF NOT EXISTS moderation_status VARCHAR(40) NOT NULL DEFAULT 'published';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'marketplace_reviews_order_required'
          AND conrelid = 'marketplace.reviews'::regclass
    ) THEN
        ALTER TABLE marketplace.reviews
            ADD CONSTRAINT marketplace_reviews_order_required
            CHECK (order_id IS NOT NULL) NOT VALID;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'marketplace_reviews_rating_range'
          AND conrelid = 'marketplace.reviews'::regclass
    ) THEN
        ALTER TABLE marketplace.reviews
            ADD CONSTRAINT marketplace_reviews_rating_range
            CHECK (rating BETWEEN 1 AND 5) NOT VALID;
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS marketplace_reviews_order_user_uidx
    ON marketplace.reviews (order_id, user_id);

CREATE INDEX IF NOT EXISTS marketplace_reviews_store_created_idx
    ON marketplace.reviews (store_id, created_at DESC);

COMMIT;
