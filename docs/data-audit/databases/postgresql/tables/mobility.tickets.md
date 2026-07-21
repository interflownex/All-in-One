# `mobility.tickets`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:193 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:194 |
| route_code | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:195 |
| amount_brl | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:196 |
| qr_token_hash | TEXT | False | False |  | sensível/restrito | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:197 |
| used_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:198 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:199 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:200 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:201 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:202 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:203 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:204 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:205 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:23 |
