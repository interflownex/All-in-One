# `jobs.resumes`

| Campo                | Tipo         | Nulo  | PK    | FK                | LGPD                             | Evidência                                                             |
| -------------------- | ------------ | ----- | ----- | ----------------- | -------------------------------- | --------------------------------------------------------------------- |
| id                   | UUID         | False | True  |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:6          |
| user_id              | UUID         | False | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:7          |
| headline             | VARCHAR(240) | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:8          |
| professional_summary | TEXT         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:9          |
| skills               | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:10         |
| education            | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:11         |
| recruiter_visibility | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:12         |
| status               | VARCHAR(40)  | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:14         |
| metadata             | JSONB        | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:15         |
| created_at           | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:16         |
| updated_at           | TIMESTAMPTZ  | False | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:17         |
| deleted_at           | TIMESTAMPTZ  | True  | False |                   | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:18         |
| created_by           | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:19         |
| updated_by           | UUID         | True  | False | identity.users.id | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:20         |
| idempotency_key      | TEXT         | True  | False |                   | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:3 |
