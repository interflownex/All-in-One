BEGIN;

DROP TABLE IF EXISTS mobility.fare_rules;
DROP TABLE IF EXISTS mobility.stops;
DROP TABLE IF EXISTS mobility.routes;
DROP TABLE IF EXISTS services.evidence;
DROP TABLE IF EXISTS services.quotes;
DROP TABLE IF EXISTS services.visits;
DROP TABLE IF EXISTS delivery.insurance_options;
DROP TABLE IF EXISTS delivery.proofs;
DROP TABLE IF EXISTS delivery.assignments;
DROP TABLE IF EXISTS delivery.quotes;
DROP TABLE IF EXISTS marketplace.carts;
DROP TABLE IF EXISTS finance.invoices;
DROP TABLE IF EXISTS finance.splits;

COMMIT;

