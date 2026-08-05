BEGIN;

DROP FUNCTION IF EXISTS compliance.current_processing_purpose();
DROP FUNCTION IF EXISTS compliance.current_subject_id();
DROP FUNCTION IF EXISTS compliance.current_tenant_id();
DROP FUNCTION IF EXISTS compliance.require_access_context();

COMMIT;
