BEGIN;

ALTER TABLE audit.logs
    ADD COLUMN IF NOT EXISTS schema_version INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS event VARCHAR(180),
    ADD COLUMN IF NOT EXISTS log_type VARCHAR(40) NOT NULL DEFAULT 'audit',
    ADD COLUMN IF NOT EXISTS tenant_id UUID,
    ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES business.companies(id),
    ADD COLUMN IF NOT EXISTS actor_role VARCHAR(100),
    ADD COLUMN IF NOT EXISTS session_id VARCHAR(180),
    ADD COLUMN IF NOT EXISTS device_id VARCHAR(180),
    ADD COLUMN IF NOT EXISTS origin VARCHAR(100) NOT NULL DEFAULT 'backend',
    ADD COLUMN IF NOT EXISTS channel VARCHAR(80) NOT NULL DEFAULT 'api',
    ADD COLUMN IF NOT EXISTS changed_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS reason TEXT,
    ADD COLUMN IF NOT EXISTS correlation_id UUID,
    ADD COLUMN IF NOT EXISTS causation_id UUID,
    ADD COLUMN IF NOT EXISTS occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS result VARCHAR(40) NOT NULL DEFAULT 'success',
    ADD COLUMN IF NOT EXISTS error_detail TEXT,
    ADD COLUMN IF NOT EXISTS authorization TEXT,
    ADD COLUMN IF NOT EXISTS approval_id UUID,
    ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES identity.users(id),
    ADD COLUMN IF NOT EXISTS exported BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS printed BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS shared BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS previous_hash CHAR(64),
    ADD COLUMN IF NOT EXISTS row_hash CHAR(64),
    ADD COLUMN IF NOT EXISTS retention_until TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 years');

ALTER TABLE audit.logs
    ADD CONSTRAINT audit_logs_log_type_allowed CHECK (log_type IN ('audit', 'security', 'business', 'technical')),
    ADD CONSTRAINT audit_logs_result_allowed CHECK (result IN ('success', 'failure', 'denied', 'partial')),
    ADD CONSTRAINT audit_logs_row_hash_format CHECK (row_hash IS NULL OR row_hash ~ '^[0-9a-f]{64}$'),
    ADD CONSTRAINT audit_logs_previous_hash_format CHECK (previous_hash IS NULL OR previous_hash ~ '^[0-9a-f]{64}$');

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_occurred ON audit.logs (tenant_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_session ON audit.logs (actor_user_id, session_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation ON audit.logs (correlation_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_retention ON audit.logs (retention_until);
CREATE INDEX IF NOT EXISTS idx_audit_logs_security_reads ON audit.logs (resource_type, occurred_at DESC)
    WHERE action = 'sensitive_read';

COMMENT ON TABLE audit.logs IS 'Trilha unificada append-only: alteração, leitura sensível, autorização, contexto, retenção e integridade.';
COMMENT ON COLUMN audit.logs.row_hash IS 'SHA-256 calculado pela aplicação sobre o registro canônico e o hash anterior.';
COMMENT ON COLUMN audit.logs.metadata IS 'Metadados permitidos e versionados; segredos e valores sensíveis devem ser minimizados antes da escrita.';

COMMIT;
