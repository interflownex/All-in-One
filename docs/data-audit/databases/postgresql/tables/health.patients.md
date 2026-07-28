# `health.patients`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:169 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:170 |
| health_identifier | VARCHAR(80) | True | False |  | dado pessoal sensível | database/postgres/migrations/004_enterprise_verticals.sql:171 |
| blood_type | VARCHAR(5) | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:172 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:173 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:174 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:175 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:176 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:177 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:178 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/004_enterprise_verticals.sql:179 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:58 |
