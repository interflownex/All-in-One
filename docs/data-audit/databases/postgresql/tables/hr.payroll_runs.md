# `hr.payroll_runs`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                               |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ----------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:349 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:350 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:351 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:352 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:353 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:354 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:355 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:356 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:357 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:358 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:359 |
