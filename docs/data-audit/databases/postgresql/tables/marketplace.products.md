# `marketplace.products`

| Campo           | Tipo           | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                                      |
| --------------- | -------------- | ----- | ----- | --------------------- | -------------------------------- | ------------------------------------------------------------------------------ |
| id              | UUID           | False | True  |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:56 |
| user_id         | UUID           | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:57 |
| store_id        | UUID           | False | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:58 |
| sku             | VARCHAR(100)   | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:59 |
| name            | VARCHAR(240)   | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:60 |
| price_brl       | NUMERIC(18, 4) | False | False |                       | financeiro confidencial          | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:61 |
| stock_quantity  | NUMERIC(18, 4) | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:62 |
| status          | VARCHAR(40)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:63 |
| metadata        | JSONB          | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:64 |
| created_at      | TIMESTAMPTZ    | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:65 |
| updated_at      | TIMESTAMPTZ    | False | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:66 |
| deleted_at      | TIMESTAMPTZ    | True  | False |                       | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:67 |
| created_by      | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:68 |
| updated_by      | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:69 |
| idempotency_key | VARCHAR(120)   | True  | False |                       | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:5                    |
