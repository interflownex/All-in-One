# `identity_core.consents`

| Campo            | Tipo                     | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                        |
| ---------------- | ------------------------ | ----- | ----- | ---------------------- | -------------------------------- | ---------------------------------------------------------------- |
| id               | UUID                     | False | True  |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:58 |
| user_id          | UUID                     | False | False | identity_core.users.id | pseudônimo vinculável            | database/postgres/migrations/009_identity_core_refinement.sql:59 |
| document_version | VARCHAR(50)              | False | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:60 |
| consent_type     | VARCHAR(100)             | False | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:61 |
| ip_address       | INET                     | True  | False |                        | dado pessoal                     | database/postgres/migrations/009_identity_core_refinement.sql:62 |
| user_agent       | TEXT                     | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:63 |
| accepted_at      | TIMESTAMP WITH TIME ZONE | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:64 |
| revoked_at       | TIMESTAMP WITH TIME ZONE | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:65 |
| idempotency_key  | VARCHAR(100)             | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:66 |
| metadata         | JSONB                    | False | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:67 |
