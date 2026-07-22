# `insurance.policies`

| Campo             | Tipo           | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| ----------------- | -------------- | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id                | UUID           | False | True  |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:246 |
| user_id           | UUID           | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:247 |
| reference_type    | VARCHAR(50)    | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:248 |
| reference_id      | UUID           | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:249 |
| premium_brl       | NUMERIC(18, 4) | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:250 |
| insured_value_brl | NUMERIC(18, 4) | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:251 |
| accepted_at       | TIMESTAMPTZ    | True  | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:252 |
| status            | VARCHAR(40)    | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:253 |
| metadata          | JSONB          | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:254 |
| created_at        | TIMESTAMPTZ    | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:255 |
| updated_at        | TIMESTAMPTZ    | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:256 |
| deleted_at        | TIMESTAMPTZ    | True  | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:257 |
| created_by        | UUID           | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:258 |
| updated_by        | UUID           | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:259 |
| idempotency_key   | VARCHAR(120)   | True  | False |                   | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:72  |
