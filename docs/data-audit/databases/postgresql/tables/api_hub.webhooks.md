# `api_hub.webhooks`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:90 |
| user_id | UUID | False | False | identity.users.id | pessoal | database/postgres/migrations/005_audit_events_api_security.sql:91 |
| company_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:92 |
| target_url | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:93 |
| event_patterns | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:94 |
| signing_secret_reference | TEXT | False | False |  | sensível/restrito | database/postgres/migrations/005_audit_events_api_security.sql:95 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:96 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:97 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:98 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:99 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:100 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:101 |
| updated_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:102 |
| idempotency_key | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/010_api_hub_refinement.sql:50 |
