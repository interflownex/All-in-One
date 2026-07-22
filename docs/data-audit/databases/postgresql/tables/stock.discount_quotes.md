# `stock.discount_quotes`

| Campo              | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                |
| ------------------ | ------------ | ----- | ----- | ----------------- | -------------------------------- | -------------------------------------------------------- |
| id                 | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:25 |
| user_id            | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/014_valley_ecosystem.sql:26 |
| catalog_product_id | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:27 |
| selected_percent   | INTEGER      | False | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:28 |
| pepitas_required   | INTEGER      | False | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:29 |
| status             | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:30 |
| metadata           | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:31 |
| created_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:32 |
| updated_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:33 |
| deleted_at         | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:34 |
| created_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/014_valley_ecosystem.sql:35 |
| updated_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/014_valley_ecosystem.sql:36 |
| idempotency_key    | VARCHAR(100) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/014_valley_ecosystem.sql:37 |
