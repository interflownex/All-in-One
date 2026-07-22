# `compliance.retention_decisions`

| Campo           | Tipo         | Nulo  | PK    | FK                                 | LGPD                             | Evidência                                                         |
| --------------- | ------------ | ----- | ----- | ---------------------------------- | -------------------------------- | ----------------------------------------------------------------- |
| id              | UUID         | False | True  |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:24 |
| candidate_id    | UUID         | False | False | compliance.retention_candidates.id | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:25 |
| module          | VARCHAR(80)  | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:26 |
| resource_type   | VARCHAR(100) | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:27 |
| resource_id     | UUID         | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:28 |
| job_name        | VARCHAR(120) | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:29 |
| action          | VARCHAR(160) | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:30 |
| decision_status | VARCHAR(40)  | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:31 |
| audit_event     | VARCHAR(120) | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:32 |
| evidence        | JSONB        | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:33 |
| payload         | JSONB        | True  | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:34 |
| dry_run         | BOOLEAN      | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:35 |
| created_at      | TIMESTAMPTZ  | False | False |                                    | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:36 |
| created_by      | UUID         | True  | False | identity.users.id                  | pseudônimo vinculável            | database/postgres/migrations/016_compliance_retention_jobs.sql:37 |
