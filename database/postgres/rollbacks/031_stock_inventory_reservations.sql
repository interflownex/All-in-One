-- Rollback manual da migration 031.
-- Executar somente em banco efêmero, desenvolvimento controlado ou após
-- confirmação de que nenhuma reserva produtiva precisa ser preservada.

BEGIN;

DROP TABLE IF EXISTS stock.stock_reservations;
DROP TABLE IF EXISTS stock.inventory_items;
DROP FUNCTION IF EXISTS stock.derive_inventory_availability_status();

COMMIT;
