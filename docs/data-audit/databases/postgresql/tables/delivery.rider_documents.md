# `delivery.rider_documents`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:4 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:5 |
| rider_profile_id | UUID | False | False | delivery.rider_profiles.id | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:6 |
| document_type | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:7 |
| storage_key | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:8 |
| verified_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:9 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:10 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:11 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:12 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:13 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:14 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:15 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:16 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/024_riders_delivery_schema_alignment.sql:17 |
