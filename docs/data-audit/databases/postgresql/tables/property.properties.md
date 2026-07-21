# `property.properties`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:231 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:232 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:233 |
| address | JSONB | False | False |  | pessoal | database/postgres/migrations/004_enterprise_verticals.sql:234 |
| property_type | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:235 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:236 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:237 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:238 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:239 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:240 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:241 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:242 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:68 |
