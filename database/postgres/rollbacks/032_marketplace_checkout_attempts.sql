-- Rollback manual da migration 032.
-- Executar somente em banco efêmero, desenvolvimento controlado ou após
-- confirmar que nenhum checkout iniciado precisa ser preservado.

BEGIN;

DROP TABLE IF EXISTS marketplace.checkout_attempts;
DROP FUNCTION IF EXISTS marketplace.protect_checkout_attempt();

COMMIT;
