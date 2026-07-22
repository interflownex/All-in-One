# `audit.event_deliveries`

| Campo             | Tipo         | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                         |
| ----------------- | ------------ | ----- | ----- | ---------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                | UUID         | False | True  |                        | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:42 |
| user_id           | UUID         | True  | False | identity.users.id      | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:43 |
| event_id          | UUID         | False | False | audit.domain_events.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:44 |
| destination       | VARCHAR(120) | False | False |                        | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:45 |
| delivery_status   | VARCHAR(40)  | False | False |                        | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:46 |
| response_metadata | JSONB        | False | False |                        | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:47 |
| created_at        | TIMESTAMPTZ  | False | False |                        | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:48 |
| created_by        | UUID         | True  | False | identity.users.id      | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:49 |
