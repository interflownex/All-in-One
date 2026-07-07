BEGIN;

CREATE TABLE IF NOT EXISTS delivery.rider_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    rider_profile_id UUID NOT NULL REFERENCES delivery.rider_profiles(id),
    document_type VARCHAR(60) NOT NULL,
    storage_key TEXT NOT NULL,
    verified_at TIMESTAMPTZ,
    status VARCHAR(40) NOT NULL DEFAULT 'pending_review',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(120) UNIQUE
);

CREATE TABLE IF NOT EXISTS delivery.rider_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    rider_profile_id UUID NOT NULL REFERENCES delivery.rider_profiles(id),
    reviewer_user_id UUID REFERENCES identity.users(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    status VARCHAR(40) NOT NULL DEFAULT 'published',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(120) UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_delivery_rider_documents_profile
    ON delivery.rider_documents (rider_profile_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_delivery_rider_reviews_profile
    ON delivery.rider_reviews (rider_profile_id, created_at DESC);

COMMIT;
