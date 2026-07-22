# `mobility.routes`

| Campo           | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                                  |
| --------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | -------------------------------------------------------------------------- |
| id              | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:154 |
| user_id         | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:155 |
| company_id      | UUID         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:156 |
| status          | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:157 |
| metadata        | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:158 |
| created_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:159 |
| updated_at      | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:160 |
| deleted_at      | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:161 |
| created_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:162 |
| updated_by      | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:163 |
| idempotency_key | VARCHAR(160) | True  | False |                   | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:164 |
