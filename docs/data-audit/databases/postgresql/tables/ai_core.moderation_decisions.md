# `ai_core.moderation_decisions`

| Campo           | Tipo          | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| --------------- | ------------- | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id              | UUID          | False | True  |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:293 |
| user_id         | UUID          | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:294 |
| module          | VARCHAR(60)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:295 |
| resource_id     | UUID          | True  | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:296 |
| risk_score      | NUMERIC(5, 4) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:297 |
| reasons         | JSONB         | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:298 |
| status          | VARCHAR(40)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:299 |
| metadata        | JSONB         | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:300 |
| created_at      | TIMESTAMPTZ   | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:301 |
| updated_at      | TIMESTAMPTZ   | False | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:302 |
| deleted_at      | TIMESTAMPTZ   | True  | False |                   | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:303 |
| created_by      | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:304 |
| updated_by      | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:305 |
| idempotency_key | VARCHAR(120)  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:84  |
