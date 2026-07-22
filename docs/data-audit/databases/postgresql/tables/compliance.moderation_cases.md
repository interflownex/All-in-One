# `compliance.moderation_cases`

| Campo            | Tipo          | Nulo  | PK    | FK                | LGPD                             | Evidência                                                         |
| ---------------- | ------------- | ----- | ----- | ----------------- | -------------------------------- | ----------------------------------------------------------------- |
| id               | UUID          | False | True  |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:53 |
| user_id          | UUID          | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:54 |
| module           | VARCHAR(60)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:55 |
| resource_type    | VARCHAR(80)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:56 |
| resource_id      | UUID          | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:57 |
| matched_signals  | JSONB         | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:58 |
| risk_score       | NUMERIC(5, 4) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:59 |
| reviewer_user_id | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:60 |
| decision         | TEXT          | True  | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:61 |
| status           | VARCHAR(40)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:62 |
| metadata         | JSONB         | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:63 |
| created_at       | TIMESTAMPTZ   | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:64 |
| updated_at       | TIMESTAMPTZ   | False | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:65 |
| deleted_at       | TIMESTAMPTZ   | True  | False |                   | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:66 |
| created_by       | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:67 |
| updated_by       | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:68 |
