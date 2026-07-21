# `delivery.delivery_requests`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:121 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:122 |
| assigned_rider_user_id | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:123 |
| escrow_id | UUID | True | False | finance.escrows.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:124 |
| service_type | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:125 |
| origin | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:126 |
| destination | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:127 |
| distance_km | NUMERIC(12, 3) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:128 |
| weight_kg | NUMERIC(12, 3) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:129 |
| volume_m3 | NUMERIC(12, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:130 |
| quoted_brl | NUMERIC(18, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:131 |
| insurance_required | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:132 |
| insurance_accepted | BOOLEAN | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:133 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:134 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:135 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:136 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:137 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:138 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:139 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:140 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:15 |
