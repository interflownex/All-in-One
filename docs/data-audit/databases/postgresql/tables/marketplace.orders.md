# `marketplace.orders`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:74 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:75 |
| store_id | UUID | False | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:76 |
| escrow_id | UUID | True | False | finance.escrows.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:77 |
| total_brl | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:78 |
| commission_brl | NUMERIC(18, 4) | False | False |  | financeiro confidencial | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:79 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:80 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:81 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:82 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:83 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:84 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:85 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:86 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:6 |
| offer_id | UUID | True | False | business.catalog_offers.id | não classificado automaticamente | database/postgres/migrations/019_valley_orders.sql:4 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/019_valley_orders.sql:5 |
