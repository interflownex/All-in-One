# `marketplace.carts`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:34 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:35 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:36 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:37 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:38 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:39 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:40 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:41 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:42 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:43 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/027_complete_legacy_adapter_relations.sql:44 |
