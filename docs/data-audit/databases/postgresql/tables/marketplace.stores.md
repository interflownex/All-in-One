# `marketplace.stores`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:41 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:42 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:43 |
| name | VARCHAR(200) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:44 |
| published_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:45 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:46 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:47 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:48 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:49 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:50 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:51 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:52 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:4 |
