# `delivery.insurance_options`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:94 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:95 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:96 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:97 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:98 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:99 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:100 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:101 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:102 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:103 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:104 |
