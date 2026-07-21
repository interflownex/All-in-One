# `bi.dashboards`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:278 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:279 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:280 |
| name | VARCHAR(160) | False | False |  | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:281 |
| definition | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:282 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:283 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:284 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:285 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:286 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:287 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:288 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:289 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:81 |
