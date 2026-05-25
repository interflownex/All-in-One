BEGIN;

ALTER TABLE jobs.resumes ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
ALTER TABLE jobs.resume_documents ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
ALTER TABLE jobs.employment_records ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
ALTER TABLE jobs.job_postings ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
ALTER TABLE jobs.applications ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
ALTER TABLE jobs.resume_access_logs ADD COLUMN IF NOT EXISTS idempotency_key TEXT;

ALTER TABLE jobs.resume_documents
    ADD COLUMN IF NOT EXISTS storage_encryption VARCHAR(40) NOT NULL DEFAULT 'AES-256-GCM';

CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_resumes_idempotency
    ON jobs.resumes(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_documents_idempotency
    ON jobs.resume_documents(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_employment_idempotency
    ON jobs.employment_records(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_postings_idempotency
    ON jobs.job_postings(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_applications_idempotency
    ON jobs.applications(idempotency_key) WHERE idempotency_key IS NOT NULL;

COMMIT;
