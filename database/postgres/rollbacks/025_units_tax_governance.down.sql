BEGIN;

DROP TABLE IF EXISTS erp.tax_calculation_snapshots;
DROP TABLE IF EXISTS erp.product_fiscal_assignments;
DROP TABLE IF EXISTS erp.product_tax_classifications;
DROP TABLE IF EXISTS erp.fiscal_rules;
DROP TABLE IF EXISTS erp.fiscal_profiles;
DROP TABLE IF EXISTS stock.stock_movements;
DROP TABLE IF EXISTS stock.product_serials;
DROP TABLE IF EXISTS stock.product_lots;
DROP TABLE IF EXISTS stock.product_unit_conversions;
DROP TABLE IF EXISTS stock.product_units;
DROP TABLE IF EXISTS stock.measurement_units;

COMMIT;
