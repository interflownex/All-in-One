# `jobs.resume_access_logs`

| Campo             | Tipo        | Nulo  | PK    | FK                    | LGPD                             | Evidência                                                             |
| ----------------- | ----------- | ----- | ----- | --------------------- | -------------------------------- | --------------------------------------------------------------------- |
| id                | UUID        | False | True  |                       | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:125        |
| user_id           | UUID        | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:126        |
| resume_id         | UUID        | False | False |                       | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:127        |
| business_id       | UUID        | False | False | business.companies.id | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:128        |
| recruiter_user_id | UUID        | False | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:129        |
| purpose           | TEXT        | False | False |                       | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:130        |
| accessed_at       | TIMESTAMPTZ | False | False |                       | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:131        |
| status            | VARCHAR(40) | False | False |                       | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:132        |
| metadata          | JSONB       | False | False |                       | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:133        |
| created_by        | UUID        | True  | False | identity.users.id     | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:134        |
| idempotency_key   | TEXT        | True  | False |                       | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:8 |
