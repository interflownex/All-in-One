# `identity.mfa_devices`

| Campo            | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| ---------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id               | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:100 |
| user_id          | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:101 |
| method           | VARCHAR(30)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:102 |
| secret_reference | TEXT         | False | False |                   | restrito                         | database/postgres/migrations/001_identity_and_schemas.sql:103 |
| verified_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:104 |
| status           | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:105 |
| metadata         | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:106 |
| created_at       | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:107 |
| updated_at       | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:108 |
| deleted_at       | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:109 |
| created_by       | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:110 |
| updated_by       | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:111 |
| idempotency_key  | VARCHAR(100) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:6   |
