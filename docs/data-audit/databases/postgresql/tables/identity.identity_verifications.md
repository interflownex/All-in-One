# `identity.identity_verifications`

| Campo             | Tipo          | Nulo  | PK    | FK                | LGPD                             | Evidência                                                     |
| ----------------- | ------------- | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------- |
| id                | UUID          | False | True  |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:133 |
| user_id           | UUID          | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:134 |
| verification_type | VARCHAR(50)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:135 |
| risk_score        | NUMERIC(5, 4) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:136 |
| reviewer_user_id  | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:137 |
| decision_reason   | TEXT          | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:138 |
| status            | VARCHAR(40)   | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:139 |
| metadata          | JSONB         | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:140 |
| created_at        | TIMESTAMPTZ   | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:141 |
| updated_at        | TIMESTAMPTZ   | False | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:142 |
| deleted_at        | TIMESTAMPTZ   | True  | False |                   | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:143 |
| created_by        | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:144 |
| updated_by        | UUID          | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/001_identity_and_schemas.sql:145 |
| idempotency_key   | VARCHAR(100)  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:8   |
