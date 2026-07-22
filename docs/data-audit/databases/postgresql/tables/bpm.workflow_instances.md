# `bpm.workflow_instances`

| Campo           | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                    |
| --------------- | ------------ | ----- | ----- | --------------------- | -------------------------------- | ------------------------------------------------------------ |
| id              | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:86 |
| user_id         | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:87 |
| company_id      | UUID         | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:88 |
| process_key     | VARCHAR(120) | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:89 |
| current_task    | VARCHAR(120) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:90 |
| sla_due_at      | TIMESTAMPTZ  | True  | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:91 |
| status          | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:92 |
| metadata        | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:93 |
| created_at      | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:94 |
| updated_at      | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:95 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                       | não classificado automaticamente | database/postgres/migrations/004_enterprise_verticals.sql:96 |
| created_by      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:97 |
| updated_by      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/004_enterprise_verticals.sql:98 |
| idempotency_key | VARCHAR(120) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/012_platform_idempotency.sql:39 |
