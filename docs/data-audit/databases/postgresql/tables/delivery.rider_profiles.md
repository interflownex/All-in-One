# `delivery.rider_profiles`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:4 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:5 |
| wallet_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:6 |
| cnh_number_hash | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:7 |
| cnh_category | VARCHAR(10) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:8 |
| document_expiry | DATE | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:9 |
| proof_of_life_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:10 |
| approved_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:11 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:12 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:13 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:14 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:15 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:16 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:17 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:18 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:13 |
