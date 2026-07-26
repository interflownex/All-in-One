BEGIN;

DROP INDEX IF EXISTS audit.idx_audit_logs_security_reads;
DROP INDEX IF EXISTS audit.idx_audit_logs_retention;
DROP INDEX IF EXISTS audit.idx_audit_logs_correlation;
DROP INDEX IF EXISTS audit.idx_audit_logs_actor_session;
DROP INDEX IF EXISTS audit.idx_audit_logs_tenant_occurred;

ALTER TABLE audit.logs
    DROP CONSTRAINT IF EXISTS audit_logs_previous_hash_format,
    DROP CONSTRAINT IF EXISTS audit_logs_row_hash_format,
    DROP CONSTRAINT IF EXISTS audit_logs_result_allowed,
    DROP CONSTRAINT IF EXISTS audit_logs_log_type_allowed,
    DROP COLUMN IF EXISTS retention_until,
    DROP COLUMN IF EXISTS row_hash,
    DROP COLUMN IF EXISTS previous_hash,
    DROP COLUMN IF EXISTS shared,
    DROP COLUMN IF EXISTS printed,
    DROP COLUMN IF EXISTS exported,
    DROP COLUMN IF EXISTS approved_by,
    DROP COLUMN IF EXISTS approval_id,
    DROP COLUMN IF EXISTS "authorization",
    DROP COLUMN IF EXISTS error_detail,
    DROP COLUMN IF EXISTS result,
    DROP COLUMN IF EXISTS occurred_at,
    DROP COLUMN IF EXISTS causation_id,
    DROP COLUMN IF EXISTS correlation_id,
    DROP COLUMN IF EXISTS reason,
    DROP COLUMN IF EXISTS changed_fields,
    DROP COLUMN IF EXISTS channel,
    DROP COLUMN IF EXISTS origin,
    DROP COLUMN IF EXISTS device_id,
    DROP COLUMN IF EXISTS session_id,
    DROP COLUMN IF EXISTS actor_role,
    DROP COLUMN IF EXISTS company_id,
    DROP COLUMN IF EXISTS tenant_id,
    DROP COLUMN IF EXISTS log_type,
    DROP COLUMN IF EXISTS event,
    DROP COLUMN IF EXISTS schema_version;

COMMIT;
