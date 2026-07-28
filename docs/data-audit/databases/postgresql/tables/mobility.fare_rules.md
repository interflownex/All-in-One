# `mobility.fare_rules`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:184 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:185 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:186 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:187 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:188 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:189 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:190 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:191 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:192 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:193 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:194 |
