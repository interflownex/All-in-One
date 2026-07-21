# `compliance.retention_candidates`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:4 |
| module | VARCHAR(80) | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:5 |
| resource_type | VARCHAR(100) | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:6 |
| resource_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:7 |
| subject_id | UUID | True | False | identity.users.id | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:8 |
| payload | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:9 |
| legal_hold | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:10 |
| requested_action | VARCHAR(120) | True | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:11 |
| legal_review_approved | BOOLEAN | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:12 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:13 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:15 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:16 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:17 |
| locked_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/016_compliance_retention_jobs.sql:18 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/016_compliance_retention_jobs.sql:19 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/016_compliance_retention_jobs.sql:20 |
