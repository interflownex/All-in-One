BEGIN;

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

ALTER TABLE marketplace.reviews
    ADD COLUMN IF NOT EXISTS order_id UUID REFERENCES marketplace.orders(id),
    ADD COLUMN IF NOT EXISTS store_id UUID REFERENCES marketplace.stores(id),
    ADD COLUMN IF NOT EXISTS offer_id TEXT,
    ADD COLUMN IF NOT EXISTS rating SMALLINT,
    ADD COLUMN IF NOT EXISTS comment TEXT,
    ADD COLUMN IF NOT EXISTS moderation_status VARCHAR(40) NOT NULL DEFAULT 'published';

ALTER TABLE marketplace.reviews
    ALTER COLUMN order_id SET NOT NULL,
    ALTER COLUMN rating SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'marketplace.reviews'::regclass
          AND conname = 'reviews_rating_check'
    ) THEN
        ALTER TABLE marketplace.reviews
            ADD CONSTRAINT reviews_rating_check CHECK (rating BETWEEN 1 AND 5);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'marketplace.reviews'::regclass
          AND conname = 'reviews_order_user_key'
    ) THEN
        ALTER TABLE marketplace.reviews
            ADD CONSTRAINT reviews_order_user_key UNIQUE (order_id, user_id);
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS marketplace_reviews_store_created_idx
    ON marketplace.reviews (store_id, created_at DESC);

COMMIT;
