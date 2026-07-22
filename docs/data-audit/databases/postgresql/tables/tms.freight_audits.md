# `tms.freight_audits`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                               |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ----------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:199 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:200 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:201 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:202 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:203 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:204 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:205 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:206 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:207 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/026_complete_typed_store_relations.sql:208 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:209 |
