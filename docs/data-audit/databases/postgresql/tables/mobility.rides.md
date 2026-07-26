# `mobility.rides`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:175 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:176 |
| driver_user_id | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:177 |
| escrow_id | UUID | True | False | finance.escrows.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:178 |
| origin | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:179 |
| destination | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:180 |
| fare_brl | NUMERIC(18, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:181 |
| vehicle_type | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:182 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:183 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:184 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:185 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:186 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:187 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:188 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:189 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:22 |
