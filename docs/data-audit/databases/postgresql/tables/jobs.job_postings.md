# `jobs.job_postings`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:84 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:85 |
| company_id | UUID | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:86 |
| title | VARCHAR(240) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:87 |
| description | TEXT | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:88 |
| requirements | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:89 |
| employment_type | VARCHAR(60) | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:90 |
| workplace_model | VARCHAR(40) | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:91 |
| salary_min_brl | NUMERIC(18, 4) | True | False |  | financeiro confidencial | database/postgres/migrations/006_jobs_recruitment_ctps.sql:92 |
| salary_max_brl | NUMERIC(18, 4) | True | False |  | financeiro confidencial | database/postgres/migrations/006_jobs_recruitment_ctps.sql:93 |
| published_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:94 |
| closes_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:95 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:96 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:98 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:99 |
| updated_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:100 |
| deleted_at | TIMESTAMPTZ | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:101 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:102 |
| updated_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:103 |
| idempotency_key | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:6 |
