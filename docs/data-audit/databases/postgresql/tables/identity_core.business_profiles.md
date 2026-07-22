# `identity_core.business_profiles`

| Campo           | Tipo                     | Nulo  | PK    | FK                     | LGPD                             | Evidência                                                        |
| --------------- | ------------------------ | ----- | ----- | ---------------------- | -------------------------------- | ---------------------------------------------------------------- |
| id              | UUID                     | False | True  |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:44 |
| owner_user_id   | UUID                     | False | False | identity_core.users.id | pseudônimo vinculável            | database/postgres/migrations/009_identity_core_refinement.sql:45 |
| legal_name      | VARCHAR(255)             | False | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:46 |
| trade_name      | VARCHAR(255)             | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:47 |
| document_cnpj   | VARCHAR(18)              | False | False |                        | dado pessoal identificador       | database/postgres/migrations/009_identity_core_refinement.sql:48 |
| cnae_primary    | VARCHAR(20)              | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:49 |
| business_status | VARCHAR(50)              | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:50 |
| idempotency_key | VARCHAR(100)             | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:51 |
| metadata        | JSONB                    | False | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:52 |
| created_at      | TIMESTAMP WITH TIME ZONE | True  | False |                        | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:53 |
