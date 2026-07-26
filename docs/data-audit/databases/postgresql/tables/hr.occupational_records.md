# `hr.occupational_records`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:394 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:395 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:396 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:397 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:398 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:399 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:400 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:401 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:402 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:403 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:404 |
