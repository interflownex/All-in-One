# `document.versions`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                               |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ----------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:319 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:320 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:321 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:322 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:323 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:324 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:325 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:326 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:327 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:328 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:329 |
