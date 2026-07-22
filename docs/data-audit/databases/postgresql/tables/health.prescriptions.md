# `health.prescriptions`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                               |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ----------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:424 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:425 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:426 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:427 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:428 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:429 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:430 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:431 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:432 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:433 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:434 |
