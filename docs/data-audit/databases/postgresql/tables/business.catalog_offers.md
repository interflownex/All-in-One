# `business.catalog_offers`

| Campo             | Tipo           | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                       |
| ----------------- | -------------- | ----- | ----- | --------------------- | -------------------------------- | --------------------------------------------------------------- |
| id                | UUID           | False | True  |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:4  |
| user_id           | UUID           | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/018_business_catalog_offers.sql:5  |
| company_id        | UUID           | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:6  |
| source_module     | VARCHAR(60)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:7  |
| source_entity_id  | UUID           | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:8  |
| offer_type        | VARCHAR(40)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:9  |
| title             | VARCHAR(240)   | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:10 |
| short_description | TEXT           | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:11 |
| category_id       | UUID           | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:12 |
| business_category | VARCHAR(120)   | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:13 |
| business_type     | VARCHAR(80)    | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:14 |
| activity_branch   | VARCHAR(120)   | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:15 |
| price_type        | VARCHAR(40)    | False | False |                       | financeiro confidencial          | database/postgres/migrations/018_business_catalog_offers.sql:16 |
| price_amount      | NUMERIC(18, 4) | True  | False |                       | financeiro confidencial          | database/postgres/migrations/018_business_catalog_offers.sql:17 |
| currency          | VARCHAR(10)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:18 |
| location_type     | VARCHAR(40)    | False | False |                       | dado pessoal                     | database/postgres/migrations/018_business_catalog_offers.sql:19 |
| availability_type | VARCHAR(40)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:20 |
| status            | VARCHAR(40)    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:21 |
| metadata          | JSONB          | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:22 |
| created_at        | TIMESTAMPTZ    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:23 |
| updated_at        | TIMESTAMPTZ    | False | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:24 |
| deleted_at        | TIMESTAMPTZ    | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:25 |
| published_at      | TIMESTAMPTZ    | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:26 |
| created_by        | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/018_business_catalog_offers.sql:27 |
| updated_by        | UUID           | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/018_business_catalog_offers.sql:28 |
| idempotency_key   | VARCHAR(100)   | True  | False |                       | não classificado automaticamente | database/postgres/migrations/018_business_catalog_offers.sql:29 |
