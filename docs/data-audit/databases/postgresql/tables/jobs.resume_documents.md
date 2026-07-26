# `jobs.resume_documents`

| Campo | Tipo | Nulo | PK | FK | LGPD | Evidência |
| --- | --- | --- | --- | --- | --- | --- |
| id | UUID | False | True |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:25 |
| user_id | UUID | False | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:26 |
| resume_id | UUID | False | False | jobs.resumes.id | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:27 |
| document_type | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:28 |
| storage_key | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:29 |
| sha256 | CHAR(64) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:30 |
| page_count | INTEGER | True | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:31 |
| evidence_status | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:32 |
| official_verification_status | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:33 |
| extraction_status | VARCHAR(60) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:35 |
| extracted_fields | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:36 |
| status | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:37 |
| metadata | JSONB | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:38 |
| created_at | TIMESTAMPTZ | False | False |  | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:39 |
| created_by | UUID | True | False | identity.users.id | pseudônimo vinculável | database/postgres/migrations/006_jobs_recruitment_ctps.sql:40 |
| idempotency_key | TEXT | True | False |  | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:4 |
| storage_encryption | VARCHAR(40) | False | False |  | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:11 |
