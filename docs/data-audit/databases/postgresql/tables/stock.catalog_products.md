# `stock.catalog_products`

| Campo           | Tipo           | Nulo  | PK    | FK                 | LGPD                             | Evidência                                                                       |
| --------------- | -------------- | ----- | ----- | ------------------ | -------------------------------- | ------------------------------------------------------------------------------- |
| id              | UUID           | False | True  |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:105 |
| user_id         | UUID           | False | False | identity.users.id  | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:106 |
| supplier_id     | UUID           | False | False | stock.suppliers.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:107 |
| external_sku    | VARCHAR(120)   | False | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:108 |
| cost_brl        | NUMERIC(18, 4) | False | False |                    | financeiro confidencial          | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:109 |
| markup_percent  | NUMERIC(7, 4)  | False | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:110 |
| status          | VARCHAR(40)    | False | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:111 |
| metadata        | JSONB          | False | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:112 |
| created_at      | TIMESTAMPTZ    | False | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:113 |
| updated_at      | TIMESTAMPTZ    | False | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:114 |
| deleted_at      | TIMESTAMPTZ    | True  | False |                    | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:115 |
| created_by      | UUID           | True  | False | identity.users.id  | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:116 |
| updated_by      | UUID           | True  | False | identity.users.id  | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:117 |
| idempotency_key | VARCHAR(120)   | True  | False |                    | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:10                    |
