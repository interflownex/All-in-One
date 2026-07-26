# `property.maintenance_orders`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:589 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:590 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:591 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:592 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:593 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:594 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:595 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:596 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:597 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:598 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:599 |
