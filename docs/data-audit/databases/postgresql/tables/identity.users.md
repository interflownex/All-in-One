# `identity.users`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:37 |
| all_in_one_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:38 |
| full_name | VARCHAR(200) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:39 |
| cpf_document | VARCHAR(32) | False | False |  | dado pessoal identificador | database/postgres/migrations/001_identity_and_schemas.sql:40 |
| birth_date | DATE | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:41 |
| email | CITEXT | False | False |  | dado pessoal | database/postgres/migrations/001_identity_and_schemas.sql:42 |
| phone_e164 | VARCHAR(20) | False | False |  | dado pessoal | database/postgres/migrations/001_identity_and_schemas.sql:43 |
| password_hash | TEXT | False | False |  | restrito | database/postgres/migrations/001_identity_and_schemas.sql:44 |
| face_hash | TEXT | False | False |  | dado pessoal sensível | database/postgres/migrations/001_identity_and_schemas.sql:45 |
| liveness_score | NUMERIC(5, 4) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:46 |
| document_status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:47 |
| kyc_status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:48 |
| mfa_required | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:49 |
| terms_accepted_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:50 |
| lgpd_consent_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:51 |
| default_wallet_id | UUID | True | False |  | financeiro confidencial | database/postgres/migrations/001_identity_and_schemas.sql:52 |
| primary_led_card_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:53 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:54 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:55 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:56 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:57 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/001_identity_and_schemas.sql:58 |
| created_by | UUID | True | False |  | pseudônimo vinculável | database/postgres/migrations/001_identity_and_schemas.sql:59 |
| updated_by | UUID | True | False |  | pseudônimo vinculável | database/postgres/migrations/001_identity_and_schemas.sql:60 |
| idempotency_key | VARCHAR(100) | True | False |  | não classificado automaticamente | database/postgres/migrations/008_identity_idempotency.sql:3 |
