# `bi.datasets`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                               |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ----------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:604 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:605 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:606 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:607 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:608 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:609 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:610 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:611 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:612 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:613 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:614 |
