# `property.units`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:544 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:545 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:546 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:547 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:548 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:549 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:550 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:551 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:552 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:553 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:554 |
