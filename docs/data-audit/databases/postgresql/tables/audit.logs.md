# `audit.logs`

| Campo              | Tipo         | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                         |
| ------------------ | ------------ | ----- | ----- | --------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id                 | UUID         | False | True  |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:4  |
| user_id            | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:5  |
| actor_user_id      | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:6  |
| actor_entity_id    | UUID         | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:7  |
| action             | VARCHAR(100) | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:8  |
| module             | VARCHAR(80)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:9  |
| resource_type      | VARCHAR(100) | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:10 |
| resource_id        | UUID         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:11 |
| before_data        | JSONB        | True  | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:12 |
| after_data         | JSONB        | True  | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:13 |
| ip_address         | INET         | True  | False |                       | dado pessoal                     | database/postgres/migrations/005_audit_events_api_security.sql:14 |
| user_agent         | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:15 |
| device_fingerprint | TEXT         | True  | False |                       | dado pessoal                     | database/postgres/migrations/005_audit_events_api_security.sql:16 |
| status             | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:17 |
| metadata           | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:18 |
| created_at         | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/005_audit_events_api_security.sql:19 |
| created_by         | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/005_audit_events_api_security.sql:20 |
| schema_version     | INTEGER      | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:4    |
| event              | VARCHAR(180) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:5    |
| log_type           | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:6    |
| tenant_id          | UUID         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:7    |
| company_id         | UUID         | True  | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:8    |
| actor_role         | VARCHAR(100) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:9    |
| session_id         | VARCHAR(180) | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:10   |
| device_id          | VARCHAR(180) | True  | False |                       | dado pessoal                     | database/postgres/migrations/029_unified_immutable_audit.sql:11   |
| origin             | VARCHAR(100) | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:12   |
| channel            | VARCHAR(80)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:13   |
| changed_fields     | JSONB        | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:14   |
| reason             | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:15   |
| correlation_id     | UUID         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:16   |
| causation_id       | UUID         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:17   |
| occurred_at        | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:18   |
| result             | VARCHAR(40)  | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:19   |
| error_detail       | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:20   |
| authorization      | TEXT         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:21   |
| approval_id        | UUID         | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:22   |
| approved_by        | UUID         | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/029_unified_immutable_audit.sql:23   |
| exported           | BOOLEAN      | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:24   |
| printed            | BOOLEAN      | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:25   |
| shared             | BOOLEAN      | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:26   |
| previous_hash      | CHAR(64)     | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:27   |
| row_hash           | CHAR(64)     | True  | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:28   |
| retention_until    | TIMESTAMPTZ  | False | False |                       | não classificado automaticamente | database/postgres/migrations/029_unified_immutable_audit.sql:29   |
