# `finance.splits`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                                 |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:4  |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:5  |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:6  |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:7  |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:8  |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:9  |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:10 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:11 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:12 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:13 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:14 |
