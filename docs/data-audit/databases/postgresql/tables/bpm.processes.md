# `bpm.processes`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:259 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:260 |
| company_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:261 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:262 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:263 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:264 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:265 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:266 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:267 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/026_complete_typed_store_relations.sql:268 |
| idempotency_key | VARCHAR(160) | True | False |  | não classificado automaticamente | database/postgres/migrations/026_complete_typed_store_relations.sql:269 |
