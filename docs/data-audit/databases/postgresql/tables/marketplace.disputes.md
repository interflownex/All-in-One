# `marketplace.disputes`

| Campo              | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                            |
| ------------------ | ------------ | ----- | ----- | --------------------- | -------------------------------- | -------------------------------------------------------------------- |
| id                 | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:4  |
| user_id            | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/022_marketplace_disputes_support.sql:5  |
| order_id           | UUID         | False | False | marketplace.orders.id | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:6  |
| store_id           | UUID         | True  | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:7  |
| company_id         | UUID         | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:8  |
| offer_id           | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:9  |
| case_type          | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:10 |
| subject            | VARCHAR(200) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:11 |
| message            | TEXT         | False | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:12 |
| desired_resolution | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:13 |
| status             | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:14 |
| metadata           | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:15 |
| created_at         | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:16 |
| updated_at         | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:17 |
| created_by         | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/022_marketplace_disputes_support.sql:18 |
| updated_by         | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/022_marketplace_disputes_support.sql:19 |
| idempotency_key    | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/022_marketplace_disputes_support.sql:20 |
