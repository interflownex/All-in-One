# `stock.suppliers`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:90 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:91 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:92 |
| homologated_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:93 |
| api_configuration | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:94 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:95 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:96 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:97 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:98 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:99 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:100 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/003_marketplace_delivery_services_mobility.sql:101 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:9 |
