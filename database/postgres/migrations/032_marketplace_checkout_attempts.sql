BEGIN;

CREATE TABLE IF NOT EXISTS marketplace.checkout_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID NOT NULL REFERENCES business.companies(id),
    store_id UUID NOT NULL REFERENCES marketplace.stores(id),
    cart_id UUID NOT NULL REFERENCES marketplace.carts(id),
    order_id UUID NOT NULL UNIQUE REFERENCES marketplace.orders(id),
    escrow_id UUID UNIQUE REFERENCES finance.escrows(id),
    status VARCHAR(48) NOT NULL DEFAULT 'requested',
    payment_status VARCHAR(32) NOT NULL DEFAULT 'not_started',
    payment_method VARCHAR(32) NOT NULL DEFAULT 'wallet',
    currency CHAR(3) NOT NULL DEFAULT 'BRL',
    expected_total_brl NUMERIC(18, 2) NOT NULL,
    total_brl NUMERIC(18, 2) NOT NULL,
    idempotency_key VARCHAR(160) NOT NULL,
    request_hash CHAR(64) NOT NULL,
    confirmation_idempotency_key VARCHAR(160),
    confirmation_request_hash CHAR(64),
    snapshot JSONB NOT NULL,
    reservation_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    correlation_id UUID NOT NULL,
    causation_id UUID,
    expires_at TIMESTAMPTZ NOT NULL,
    confirmed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT marketplace_checkout_status_allowed CHECK (
        status IN (
            'requested', 'pending_stock_reservation', 'pending_payment',
            'confirmed', 'rejected', 'payment_failed', 'cancelled', 'expired'
        )
    ),
    CONSTRAINT marketplace_checkout_payment_status_allowed CHECK (
        payment_status IN ('not_started', 'pending', 'authorized', 'failed', 'cancelled')
    ),
    CONSTRAINT marketplace_checkout_payment_method_allowed CHECK (payment_method IN ('wallet')),
    CONSTRAINT marketplace_checkout_currency_brl CHECK (currency = 'BRL'),
    CONSTRAINT marketplace_checkout_totals_nonnegative CHECK (
        expected_total_brl >= 0 AND total_brl >= 0
    ),
    CONSTRAINT marketplace_checkout_request_hash_sha256 CHECK (
        request_hash ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT marketplace_checkout_confirmation_hash_sha256 CHECK (
        confirmation_request_hash IS NULL
        OR confirmation_request_hash ~ '^[0-9a-f]{64}$'
    ),
    CONSTRAINT marketplace_checkout_snapshot_object CHECK (jsonb_typeof(snapshot) = 'object'),
    CONSTRAINT marketplace_checkout_reservations_array CHECK (jsonb_typeof(reservation_ids) = 'array'),
    CONSTRAINT marketplace_checkout_metadata_object CHECK (jsonb_typeof(metadata) = 'object'),
    CONSTRAINT marketplace_checkout_idempotency_scope_unique UNIQUE (user_id, idempotency_key),
    CONSTRAINT marketplace_checkout_confirmation_complete CHECK (
        status <> 'confirmed'
        OR (
            payment_status = 'authorized'
            AND escrow_id IS NOT NULL
            AND confirmed_at IS NOT NULL
            AND confirmation_idempotency_key IS NOT NULL
            AND confirmation_request_hash IS NOT NULL
        )
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_marketplace_checkout_confirmation_idempotency
    ON marketplace.checkout_attempts (user_id, confirmation_idempotency_key)
    WHERE confirmation_idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_marketplace_checkout_user_status
    ON marketplace.checkout_attempts (user_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_marketplace_checkout_company_status
    ON marketplace.checkout_attempts (company_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_marketplace_checkout_expiration
    ON marketplace.checkout_attempts (expires_at, id)
    WHERE status = 'pending_payment';

CREATE OR REPLACE FUNCTION marketplace.protect_checkout_attempt()
RETURNS trigger AS $$
BEGIN
    IF ROW(
        NEW.user_id,
        NEW.company_id,
        NEW.store_id,
        NEW.cart_id,
        NEW.order_id,
        NEW.currency,
        NEW.expected_total_brl,
        NEW.total_brl,
        NEW.idempotency_key,
        NEW.request_hash,
        NEW.snapshot,
        NEW.reservation_ids,
        NEW.correlation_id,
        NEW.causation_id,
        NEW.expires_at,
        NEW.created_at,
        NEW.created_by
    ) IS DISTINCT FROM ROW(
        OLD.user_id,
        OLD.company_id,
        OLD.store_id,
        OLD.cart_id,
        OLD.order_id,
        OLD.currency,
        OLD.expected_total_brl,
        OLD.total_brl,
        OLD.idempotency_key,
        OLD.request_hash,
        OLD.snapshot,
        OLD.reservation_ids,
        OLD.correlation_id,
        OLD.causation_id,
        OLD.expires_at,
        OLD.created_at,
        OLD.created_by
    ) THEN
        RAISE EXCEPTION 'checkout immutable fields cannot be changed';
    END IF;

    IF OLD.status IN ('confirmed', 'rejected', 'payment_failed', 'cancelled', 'expired')
       AND NEW.status <> OLD.status THEN
        RAISE EXCEPTION 'terminal checkout status cannot be changed';
    END IF;

    IF OLD.status = 'pending_payment'
       AND NEW.status NOT IN ('pending_payment', 'confirmed', 'payment_failed', 'cancelled', 'expired') THEN
        RAISE EXCEPTION 'invalid checkout status transition';
    END IF;

    IF OLD.status IN ('requested', 'pending_stock_reservation')
       AND NEW.status NOT IN (
           'requested', 'pending_stock_reservation', 'pending_payment',
           'rejected', 'cancelled', 'expired'
       ) THEN
        RAISE EXCEPTION 'invalid checkout status transition';
    END IF;

    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS protect_marketplace_checkout_attempt ON marketplace.checkout_attempts;
CREATE TRIGGER protect_marketplace_checkout_attempt
BEFORE UPDATE ON marketplace.checkout_attempts
FOR EACH ROW
EXECUTE FUNCTION marketplace.protect_checkout_attempt();

COMMENT ON TABLE marketplace.checkout_attempts IS
    'Orquestra checkout idempotente, snapshot imutável, reservas Stock e autorização Wallet sem iniciar Delivery.';

COMMIT;
