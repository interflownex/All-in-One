-- Executar somente em banco efêmero ou após procedimento operacional aprovado.
BEGIN;
DROP TABLE IF EXISTS marketplace.checkout_operations;
DROP TABLE IF EXISTS marketplace.checkout_items;
DROP TABLE IF EXISTS marketplace.checkouts;
COMMIT;
