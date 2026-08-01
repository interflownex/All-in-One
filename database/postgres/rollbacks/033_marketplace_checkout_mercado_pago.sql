BEGIN;

UPDATE marketplace.checkout_attempts
SET payment_method = 'wallet'
WHERE payment_method = 'mercado_pago';

ALTER TABLE marketplace.checkout_attempts
    DROP CONSTRAINT IF EXISTS marketplace_checkout_payment_method_allowed;

ALTER TABLE marketplace.checkout_attempts
    ADD CONSTRAINT marketplace_checkout_payment_method_allowed
    CHECK (payment_method IN ('wallet'));

COMMIT;
