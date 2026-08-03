BEGIN;

ALTER TABLE marketplace.checkout_attempts
    DROP CONSTRAINT IF EXISTS marketplace_checkout_payment_method_allowed;

ALTER TABLE marketplace.checkout_attempts
    ADD CONSTRAINT marketplace_checkout_payment_method_allowed
    CHECK (payment_method IN ('wallet', 'mercado_pago'));

COMMENT ON COLUMN marketplace.checkout_attempts.payment_method IS
    'wallet ou mercado_pago; a confirmação externa depende de webhook verificado.';

COMMIT;
