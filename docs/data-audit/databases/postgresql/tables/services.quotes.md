# `services.quotes`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:124 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:125 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:126 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:127 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:128 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:129 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:130 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:131 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:132 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:133 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:134 |
