# `audit.logs`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:4 |
| user_id | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/005_audit_events_api_security.sql:5 |
| actor_user_id | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/005_audit_events_api_security.sql:6 |
| actor_entity_id | UUID | True | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:7 |
| action | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:8 |
| module | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:9 |
| resource_type | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:10 |
| resource_id | UUID | True | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:11 |
| before_data | JSONB | True | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:12 |
| after_data | JSONB | True | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:13 |
| ip_address | INET | True | False |  | dado pessoal | database/postgres/migrations/005_audit_events_api_security.sql:14 |
| user_agent | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:15 |
| device_fingerprint | TEXT | True | False |  | dado pessoal | database/postgres/migrations/005_audit_events_api_security.sql:16 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:17 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:18 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:19 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/005_audit_events_api_security.sql:20 |
