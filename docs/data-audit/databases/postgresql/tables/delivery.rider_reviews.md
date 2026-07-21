# `delivery.rider_reviews`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:21 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:22 |
| rider_profile_id | UUID | False | False | delivery.rider_profiles.id | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:23 |
| reviewer_user_id | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:24 |
| rating | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:25 |
| comment | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:26 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:27 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:28 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:29 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:30 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:31 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:32 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:33 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:34 |
