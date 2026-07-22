# `identity.duplicate_attempts`

| Campo              | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| ------------------ | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id                 | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:166 |
| user_id            | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:167 |
| cpf_document_hash  | TEXT         | True  | False |                   | dado pessoal identificador       | database/postgres/migrations/001_identity_and_schemas.sql:168 |
| face_hash          | TEXT         | True  | False |                   | dado pessoal sensível            | database/postgres/migrations/001_identity_and_schemas.sql:169 |
| email_hash         | TEXT         | True  | False |                   | dado pessoal                     | database/postgres/migrations/001_identity_and_schemas.sql:170 |
| device_fingerprint | TEXT         | True  | False |                   | dado pessoal                     | database/postgres/migrations/001_identity_and_schemas.sql:171 |
| ip_address         | INET         | True  | False |                   | dado pessoal                     | database/postgres/migrations/001_identity_and_schemas.sql:172 |
| blocked_reason     | TEXT         | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:173 |
| status             | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:174 |
| metadata           | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:175 |
| created_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:176 |
| updated_at         | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:177 |
| deleted_at         | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:178 |
| created_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:179 |
| updated_by         | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:180 |
| idempotency_key    | VARCHAR(100) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:10  |
