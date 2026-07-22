# `identity.documents`

| Campo                | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                    |
| -------------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------ |
| id                   | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:66 |
| user_id              | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:67 |
| document_type        | VARCHAR(60)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:68 |
| document_number_hash | TEXT         | False | False |                   | dado pessoal identificador       | database/postgres/migrations/001_identity_and_schemas.sql:69 |
| storage_key          | TEXT         | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:70 |
| expires_at           | DATE         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:71 |
| verification_status  | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:72 |
| status               | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:73 |
| metadata             | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:74 |
| created_at           | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:75 |
| updated_at           | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:76 |
| deleted_at           | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:77 |
| created_by           | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:78 |
| updated_by           | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:79 |
| idempotency_key      | VARCHAR(100) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:4  |
