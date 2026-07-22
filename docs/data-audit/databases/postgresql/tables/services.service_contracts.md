# `services.service_contracts`

| Campo                | Tipo           | Nulo  | PK    | FK                         | LGPD                             | Evidência                                                                       |
| -------------------- | -------------- | ----- | ----- | -------------------------- | -------------------------------- | ------------------------------------------------------------------------------- |
| id                   | UUID           | False | True  |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:158 |
| user_id              | UUID           | False | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:159 |
| provider_user_id     | UUID           | False | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:160 |
| escrow_id            | UUID           | False | False | finance.escrows.id         | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:161 |
| visit_price_brl      | NUMERIC(18, 4) | False | False |                            | financeiro confidencial          | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:162 |
| contracted_price_brl | NUMERIC(18, 4) | True  | False |                            | financeiro confidencial          | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:163 |
| evidence             | JSONB          | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:164 |
| status               | VARCHAR(40)    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:165 |
| metadata             | JSONB          | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:166 |
| created_at           | TIMESTAMPTZ    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:167 |
| updated_at           | TIMESTAMPTZ    | False | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:168 |
| deleted_at           | TIMESTAMPTZ    | True  | False |                            | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:169 |
| created_by           | UUID           | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:170 |
| updated_by           | UUID           | True  | False | identity.users.id          | pseudônimo vinculável            | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:171 |
| idempotency_key      | VARCHAR(120)   | True  | False |                            | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:19                    |
| offer_id             | UUID           | True  | False | business.catalog_offers.id | não classificado automaticamente | database/postgres/migrations/020_valley_services_health_sprint3.sql:5           |
| company_id           | UUID           | True  | False | business.companies.id      | não classificado automaticamente | database/postgres/migrations/020_valley_services_health_sprint3.sql:6           |
| scheduled_at         | TIMESTAMPTZ    | True  | False |                            | não classificado automaticamente | database/postgres/migrations/020_valley_services_health_sprint3.sql:7           |
