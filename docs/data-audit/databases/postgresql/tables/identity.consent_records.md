# `identity.consent_records`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:149 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/001_identity_and_schemas.sql:150 |
| consent_type | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:151 |
| policy_version | VARCHAR(30) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:152 |
| accepted_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:153 |
| revoked_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:154 |
| ip_address | INET | True | False |  | dado pessoal | database/postgres/migrations/001_identity_and_schemas.sql:155 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:156 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:157 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:158 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:159 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:160 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/001_identity_and_schemas.sql:161 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/001_identity_and_schemas.sql:162 |
| idempotency_key | VARCHAR(100) | True | False |  | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:9 |
