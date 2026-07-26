# `wms.warehouses`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:20 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:21 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:22 |
| name | VARCHAR(160) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:23 |
| addressing_rules | JSONB | False | False |  | dado pessoal | database/postgres/migrations/004_enterprise_verticals.sql:24 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:25 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:26 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:27 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:28 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:29 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:30 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:31 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:29 |
