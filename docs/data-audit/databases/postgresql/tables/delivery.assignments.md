# `delivery.assignments`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                                 |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | ------------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:64 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:65 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:66 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:67 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:68 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:69 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:70 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:71 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:72 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:73 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:74 |
