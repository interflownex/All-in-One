# `billing.subscriptions`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:121 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:122 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:123 |
| plan_code | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:124 |
| recurring_brl | NUMERIC(18, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:125 |
| next_billing_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:126 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:127 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:128 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:129 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:130 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:131 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:132 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:133 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:46 |
