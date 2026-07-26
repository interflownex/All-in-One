# `marketplace.reviews`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:24 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/021_valley_reviews.sql:25 |
| order_id | UUID | False | False | marketplace.orders.id | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:26 |
| store_id | UUID | True | False | marketplace.stores.id | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:27 |
| offer_id | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:28 |
| rating | SMALLINT | False | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:29 |
| comment | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:30 |
| moderation_status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:31 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:32 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:33 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:34 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:35 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/021_valley_reviews.sql:36 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/021_valley_reviews.sql:37 |
| idempotency_key | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/021_valley_reviews.sql:38 |
