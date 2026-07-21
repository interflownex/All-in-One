# `identity.biometrics`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:84 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/001_identity_and_schemas.sql:85 |
| face_hash | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:86 |
| provider_reference | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:87 |
| last_liveness_score | NUMERIC(5, 4) | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:88 |
| consent_recorded_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:89 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:90 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:91 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:92 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:93 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:94 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:95 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:96 |
| idempotency_key | VARCHAR(100) | True | False |  | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:5 |
