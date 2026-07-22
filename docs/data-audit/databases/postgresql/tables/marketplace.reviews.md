# `marketplace.reviews`

| Campo             | Tipo        | Nulo  | PK    | FK                    | LGPD                             | Evidência                                              |
| ----------------- | ----------- | ----- | ----- | --------------------- | -------------------------------- | ------------------------------------------------------ |
| id                | UUID        | False | True  |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:4  |
| user_id           | UUID        | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/021_valley_reviews.sql:5  |
| order_id          | UUID        | False | False | marketplace.orders.id | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:6  |
| store_id          | UUID        | True  | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:7  |
| offer_id          | TEXT        | True  | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:8  |
| rating            | SMALLINT    | False | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:9  |
| comment           | TEXT        | True  | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:10 |
| moderation_status | VARCHAR(40) | False | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:11 |
| status            | VARCHAR(40) | False | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:12 |
| metadata          | JSONB       | False | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:13 |
| created_at        | TIMESTAMPTZ | False | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:14 |
| updated_at        | TIMESTAMPTZ | False | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:15 |
| created_by        | UUID        | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/021_valley_reviews.sql:16 |
| updated_by        | UUID        | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/021_valley_reviews.sql:17 |
| idempotency_key   | TEXT        | True  | False |                       | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:18 |
