# `jobs.applications`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:107 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:108 |
| job_posting_id | UUID | False | False | jobs.job_postings.id | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:109 |
| resume_id | UUID | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:110 |
| cover_letter | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:111 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:112 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:114 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:115 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:116 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:117 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:118 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:119 |
| idempotency_key | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:7 |
