# `jobs.employment_records`

| Campo                        | Tipo         | Nulo  | PK    | FK                       | LGPD                             | Evidência                                                             |
| ---------------------------- | ------------ | ----- | ----- | ------------------------ | -------------------------------- | --------------------------------------------------------------------- |
| id                           | UUID         | False | True  |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:46         |
| user_id                      | UUID         | False | False | identity.users.id        | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:47         |
| resume_id                    | UUID         | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:48         |
| source_document_id           | UUID         | True  | False | jobs.resume_documents.id | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:49         |
| source_type                  | VARCHAR(50)  | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:50         |
| evidence_status              | VARCHAR(60)  | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:51         |
| official_verification_status | VARCHAR(60)  | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:52         |
| employer_name                | VARCHAR(240) | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:53         |
| employer_cnpj                | VARCHAR(20)  | True  | False |                          | dado pessoal identificador       | database/postgres/migrations/006_jobs_recruitment_ctps.sql:54         |
| role_title                   | VARCHAR(180) | True  | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:55         |
| started_on                   | DATE         | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:56         |
| ended_on                     | DATE         | True  | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:57         |
| user_activity_description    | TEXT         | True  | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:58         |
| is_informal_activity         | BOOLEAN      | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:59         |
| visible_to_recruiter         | BOOLEAN      | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:60         |
| status                       | VARCHAR(40)  | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:61         |
| metadata                     | JSONB        | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:62         |
| created_at                   | TIMESTAMPTZ  | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:63         |
| updated_at                   | TIMESTAMPTZ  | False | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:64         |
| deleted_at                   | TIMESTAMPTZ  | True  | False |                          | não classificado automaticamente | database/postgres/migrations/006_jobs_recruitment_ctps.sql:65         |
| created_by                   | UUID         | True  | False | identity.users.id        | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:66         |
| updated_by                   | UUID         | True  | False | identity.users.id        | pseudônimo vinculável            | database/postgres/migrations/006_jobs_recruitment_ctps.sql:67         |
| idempotency_key              | TEXT         | True  | False |                          | não classificado automaticamente | database/postgres/migrations/007_jobs_runtime_private_documents.sql:5 |
