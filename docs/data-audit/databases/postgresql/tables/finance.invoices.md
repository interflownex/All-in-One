# `finance.invoices`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                                 |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:19 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:20 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:21 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:22 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:23 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:24 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:25 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:26 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:27 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:28 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:29 |
