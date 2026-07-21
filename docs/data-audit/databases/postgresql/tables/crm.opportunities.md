# `crm.opportunities`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:70 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:71 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:72 |
| title | VARCHAR(240) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:73 |
| expected_value_brl | NUMERIC(18, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:74 |
| stage | VARCHAR(50) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:75 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:76 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:77 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:78 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:79 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:80 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:81 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:82 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:36 |
