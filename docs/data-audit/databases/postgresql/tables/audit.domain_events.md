# `audit.domain_events`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:24 |
| user_id | UUID | True | False | identity.users.id | pessoal | database/postgres/migrations/005_audit_events_api_security.sql:25 |
| actor_user_id | UUID | True | False | identity.users.id | pessoal | database/postgres/migrations/005_audit_events_api_security.sql:26 |
| entity_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:27 |
| routing_key | VARCHAR(120) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:28 |
| aggregate_type | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:29 |
| aggregate_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:30 |
| correlation_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:31 |
| schema_version | INTEGER | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:32 |
| payload | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:33 |
| published_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:34 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:35 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:36 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:37 |
| created_by | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:38 |
| next_retry_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/023_performance_indexes.sql:8 |
