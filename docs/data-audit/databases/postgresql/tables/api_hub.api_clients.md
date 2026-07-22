# `api_hub.api_clients`

| Campo                 | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                         |
| --------------------- | ------------ | ----- | ----- | --------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                    | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:72 |
| user_id               | UUID         | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:73 |
| company_id            | UUID         | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:74 |
| client_name           | VARCHAR(150) | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:75 |
| client_id_hash        | TEXT         | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:76 |
| secret_reference      | TEXT         | False | False |                       | restrito                         | database/postgres/migrations/005_audit_events_api_security.sql:77 |
| scopes                | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:78 |
| rate_limit_per_minute | INTEGER      | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:79 |
| status                | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:80 |
| metadata              | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:81 |
| created_at            | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:82 |
| updated_at            | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:83 |
| deleted_at            | TIMESTAMPTZ  | True  | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:84 |
| created_by            | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:85 |
| updated_by            | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:86 |
| idempotency_key       | VARCHAR(120) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:47        |
