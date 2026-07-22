# `identity.sessions`

| Campo              | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| ------------------ | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id                 | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:115 |
| user_id            | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:116 |
| token_hash         | TEXT         | False | False |                   | restrito                         | database/postgres/migrations/001_identity_and_schemas.sql:117 |
| device_fingerprint | TEXT         | False | False |                   | dado pessoal                     | database/postgres/migrations/001_identity_and_schemas.sql:118 |
| ip_address         | INET         | False | False |                   | dado pessoal                     | database/postgres/migrations/001_identity_and_schemas.sql:119 |
| user_agent         | TEXT         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:120 |
| expires_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:121 |
| revoked_at         | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:122 |
| status             | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:123 |
| metadata           | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:124 |
| created_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:125 |
| updated_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:126 |
| deleted_at         | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:127 |
| created_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:128 |
| updated_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:129 |
| idempotency_key    | VARCHAR(100) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:7   |
