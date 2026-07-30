# `stock.inventory_items`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:4 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/031_stock_inventory_reservations.sql:5 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:6 |
| warehouse_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:7 |
| product_id | UUID | False | False | marketplace.products.id | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:8 |
| sku | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:9 |
| physical_quantity | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:10 |
| reserved_quantity | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:11 |
| available_quantity | NUMERIC(18, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:12 |
| version | BIGINT | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:14 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:15 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:16 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:17 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:18 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/031_stock_inventory_reservations.sql:19 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/031_stock_inventory_reservations.sql:20 |
