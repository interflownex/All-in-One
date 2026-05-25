BEGIN;

CREATE SCHEMA IF NOT EXISTS jobs;

CREATE TABLE IF NOT EXISTS jobs.resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    headline VARCHAR(240) NOT NULL,
    professional_summary TEXT,
    skills JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(skills) = 'array'),
    education JSONB NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(education) = 'array'),
    recruiter_visibility VARCHAR(40) NOT NULL DEFAULT 'private'
        CHECK (recruiter_visibility IN ('private', 'business_recruiters')),
    status VARCHAR(40) NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT resumes_id_user_id_unique UNIQUE (id, user_id)
);

CREATE TABLE IF NOT EXISTS jobs.resume_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    resume_id UUID NOT NULL REFERENCES jobs.resumes(id),
    document_type VARCHAR(60) NOT NULL CHECK (document_type = 'ctps_digital_pdf'),
    storage_key TEXT,
    sha256 CHAR(64) NOT NULL,
    page_count INTEGER CHECK (page_count > 0),
    evidence_status VARCHAR(60) NOT NULL CHECK (evidence_status = 'validated_by_document_import'),
    official_verification_status VARCHAR(60) NOT NULL DEFAULT 'not_verified_externally'
        CHECK (official_verification_status IN ('not_verified_externally', 'verified_by_authorized_provider', 'rejected_by_authorized_provider')),
    extraction_status VARCHAR(60) NOT NULL,
    extracted_fields JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(extracted_fields) = 'object'),
    status VARCHAR(40) NOT NULL DEFAULT 'imported',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    CONSTRAINT resume_document_owner_fk FOREIGN KEY (resume_id, user_id) REFERENCES jobs.resumes(id, user_id),
    UNIQUE (resume_id, sha256)
);

CREATE TABLE IF NOT EXISTS jobs.employment_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    resume_id UUID NOT NULL,
    source_document_id UUID REFERENCES jobs.resume_documents(id),
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('ctps_digital_pdf_import', 'user_declared')),
    evidence_status VARCHAR(60) NOT NULL CHECK (evidence_status IN ('validated_by_document_import', 'self_declared_unverified')),
    official_verification_status VARCHAR(60) NOT NULL DEFAULT 'not_verified_externally',
    employer_name VARCHAR(240) NOT NULL,
    employer_cnpj VARCHAR(20),
    role_title VARCHAR(180),
    started_on DATE NOT NULL,
    ended_on DATE,
    user_activity_description TEXT,
    is_informal_activity BOOLEAN NOT NULL DEFAULT FALSE,
    visible_to_recruiter BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(40) NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT employment_resume_owner_fk FOREIGN KEY (resume_id, user_id) REFERENCES jobs.resumes(id, user_id),
    CONSTRAINT employment_provenance_integrity CHECK (
        (source_type = 'ctps_digital_pdf_import'
            AND source_document_id IS NOT NULL
            AND evidence_status = 'validated_by_document_import'
            AND user_activity_description IS NULL
            AND is_informal_activity = FALSE)
        OR
        (source_type = 'user_declared'
            AND source_document_id IS NULL
            AND evidence_status = 'self_declared_unverified')
    ),
    CHECK (ended_on IS NULL OR ended_on >= started_on)
);

CREATE TABLE IF NOT EXISTS jobs.job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID NOT NULL REFERENCES business.companies(id),
    title VARCHAR(240) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    employment_type VARCHAR(60),
    workplace_model VARCHAR(40),
    salary_min_brl NUMERIC(18, 4) CHECK (salary_min_brl IS NULL OR salary_min_brl >= 0),
    salary_max_brl NUMERIC(18, 4) CHECK (salary_max_brl IS NULL OR salary_max_brl >= salary_min_brl),
    published_at TIMESTAMPTZ,
    closes_at TIMESTAMPTZ,
    status VARCHAR(40) NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'approved', 'published', 'closed', 'cancelled')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id)
);

CREATE TABLE IF NOT EXISTS jobs.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    job_posting_id UUID NOT NULL REFERENCES jobs.job_postings(id),
    resume_id UUID NOT NULL,
    cover_letter TEXT,
    status VARCHAR(40) NOT NULL DEFAULT 'submitted'
        CHECK (status IN ('submitted', 'under_review', 'shortlisted', 'rejected', 'withdrawn', 'hired')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    CONSTRAINT application_resume_owner_fk FOREIGN KEY (resume_id, user_id) REFERENCES jobs.resumes(id, user_id),
    UNIQUE (user_id, job_posting_id)
);

CREATE TABLE IF NOT EXISTS jobs.resume_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    resume_id UUID NOT NULL,
    business_id UUID NOT NULL REFERENCES business.companies(id),
    recruiter_user_id UUID NOT NULL REFERENCES identity.users(id),
    purpose TEXT NOT NULL,
    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status VARCHAR(40) NOT NULL DEFAULT 'recorded',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(metadata) = 'object'),
    created_by UUID REFERENCES identity.users(id),
    CONSTRAINT access_log_resume_owner_fk FOREIGN KEY (resume_id, user_id) REFERENCES jobs.resumes(id, user_id)
);

DROP TRIGGER IF EXISTS immutable_jobs_resume_documents ON jobs.resume_documents;
CREATE TRIGGER immutable_jobs_resume_documents
BEFORE UPDATE OR DELETE ON jobs.resume_documents
FOR EACH ROW EXECUTE FUNCTION audit.reject_immutable_change();

DROP TRIGGER IF EXISTS immutable_jobs_resume_access_logs ON jobs.resume_access_logs;
CREATE TRIGGER immutable_jobs_resume_access_logs
BEFORE UPDATE OR DELETE ON jobs.resume_access_logs
FOR EACH ROW EXECUTE FUNCTION audit.reject_immutable_change();

CREATE INDEX IF NOT EXISTS idx_jobs_resumes_visible ON jobs.resumes(recruiter_visibility, status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_employment_resume ON jobs.employment_records(resume_id, evidence_status);
CREATE INDEX IF NOT EXISTS idx_jobs_postings_public ON jobs.job_postings(status, published_at) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_jobs_applications_company_flow ON jobs.applications(job_posting_id, status);
CREATE INDEX IF NOT EXISTS idx_jobs_resume_access_audit ON jobs.resume_access_logs(resume_id, accessed_at);

COMMIT;
