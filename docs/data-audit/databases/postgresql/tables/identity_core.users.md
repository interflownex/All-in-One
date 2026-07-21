# `identity_core.users`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:10 |
| global_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:11 |
| email | VARCHAR(255) | False | False |  | pessoal | database/postgres/migrations/009_identity_core_refinement.sql:12 |
| password_hash | VARCHAR(255) | False | False |  | sensível/restrito | database/postgres/migrations/009_identity_core_refinement.sql:13 |
| full_name | VARCHAR(255) | False | False |  | pessoal | database/postgres/migrations/009_identity_core_refinement.sql:14 |
| document_cpf | VARCHAR(14) | True | False |  | sensível/restrito | database/postgres/migrations/009_identity_core_refinement.sql:15 |
| mfa_enabled | BOOLEAN | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:16 |
| mfa_secret | VARCHAR(255) | True | False |  | sensível/restrito | database/postgres/migrations/009_identity_core_refinement.sql:17 |
| account_status | VARCHAR(50) | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:18 |
| last_login_at | TIMESTAMP WITH TIME ZONE | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:19 |
| idempotency_key | VARCHAR(100) | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:20 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:21 |
| created_at | TIMESTAMP WITH TIME ZONE | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:22 |
| updated_at | TIMESTAMP WITH TIME ZONE | True | False |  | não classificado automaticamente | database/postgres/migrations/009_identity_core_refinement.sql:23 |
