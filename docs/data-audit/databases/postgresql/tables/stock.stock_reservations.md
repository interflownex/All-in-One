# `stock.stock_reservations`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:65 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/031_stock_inventory_reservations.sql:66 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:67 |
| order_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:68 |
| inventory_item_id | UUID | False | False | stock.inventory_items.id | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:69 |
| quantity | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:70 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:71 |
| idempotency_key | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:72 |
| request_hash | CHAR(64) | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:73 |
| correlation_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:74 |
| causation_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:75 |
| expires_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:76 |
| committed_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:77 |
| released_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:78 |
| release_reason | VARCHAR(500) | True | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:79 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:80 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:81 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/031_stock_inventory_reservations.sql:82 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/031_stock_inventory_reservations.sql:83 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/031_stock_inventory_reservations.sql:84 |
