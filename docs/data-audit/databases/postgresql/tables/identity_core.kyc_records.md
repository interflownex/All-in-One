# `identity_core.kyc_records`

| Campo               | Tipo                     | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                        |
| ------------------- | ------------------------ | ----- | ----- | ---------------------- | -------------------------------- | ---------------------------------------------------------------- |
| id                  | UUID                     | False | True  |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:28 |
| user_id             | UUID                     | False | False | identity_core.users.id | pseudônimo vinculável            | database/postgres/migrations/009_identity_core_refinement.sql:29 |
| biometry_hash       | TEXT                     | False | False |                        | dado pessoal sensível            | database/postgres/migrations/009_identity_core_refinement.sql:30 |
| doc_front_url       | TEXT                     | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:31 |
| doc_back_url        | TEXT                     | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:32 |
| verification_status | VARCHAR(50)              | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:33 |
| audited_by          | UUID                     | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:34 |
| rejection_reason    | TEXT                     | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:35 |
| verified_at         | TIMESTAMP WITH TIME ZONE | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:36 |
| idempotency_key     | VARCHAR(100)             | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:37 |
| metadata            | JSONB                    | False | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:38 |
| created_at          | TIMESTAMP WITH TIME ZONE | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:39 |
