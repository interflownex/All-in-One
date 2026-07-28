# `vision.motion_alerts`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:484 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:485 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:486 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:487 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:488 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:489 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:490 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:491 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:492 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:493 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:494 |
