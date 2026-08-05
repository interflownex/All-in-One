BEGIN;

CREATE OR REPLACE FUNCTION compliance.require_access_context()
RETURNS void
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog, compliance
AS $$
DECLARE
    tenant_value text := current_setting('app.tenant_id', true);
    subject_value text := current_setting('app.subject_id', true);
    subject_type_value text := current_setting('app.subject_type', true);
    purpose_value text := current_setting('app.processing_purpose', true);
    request_value text := current_setting('app.request_id', true);
BEGIN
    IF tenant_value IS NULL OR tenant_value = '' THEN
        RAISE EXCEPTION 'missing required access context: app.tenant_id' USING ERRCODE = '28000';
    END IF;
    IF subject_value IS NULL OR subject_value = '' THEN
        RAISE EXCEPTION 'missing required access context: app.subject_id' USING ERRCODE = '28000';
    END IF;
    IF request_value IS NULL OR request_value = '' THEN
        RAISE EXCEPTION 'missing required access context: app.request_id' USING ERRCODE = '28000';
    END IF;

    PERFORM tenant_value::uuid;
    PERFORM subject_value::uuid;
    PERFORM request_value::uuid;

    IF subject_type_value IS NULL OR subject_type_value NOT IN ('user', 'service', 'support', 'auditor') THEN
        RAISE EXCEPTION 'invalid or missing access context: app.subject_type' USING ERRCODE = '28000';
    END IF;

    IF purpose_value IS NULL OR purpose_value NOT IN (
        'service_delivery',
        'security',
        'compliance',
        'support',
        'data_subject_request'
    ) THEN
        RAISE EXCEPTION 'invalid or missing access context: app.processing_purpose' USING ERRCODE = '28000';
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION compliance.current_tenant_id()
RETURNS uuid
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = pg_catalog, compliance
AS $$
BEGIN
    PERFORM compliance.require_access_context();
    RETURN current_setting('app.tenant_id', true)::uuid;
END;
$$;

CREATE OR REPLACE FUNCTION compliance.current_subject_id()
RETURNS uuid
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = pg_catalog, compliance
AS $$
BEGIN
    PERFORM compliance.require_access_context();
    RETURN current_setting('app.subject_id', true)::uuid;
END;
$$;

CREATE OR REPLACE FUNCTION compliance.current_processing_purpose()
RETURNS text
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = pg_catalog, compliance
AS $$
BEGIN
    PERFORM compliance.require_access_context();
    RETURN current_setting('app.processing_purpose', true);
END;
$$;

REVOKE ALL ON FUNCTION compliance.require_access_context() FROM PUBLIC;
REVOKE ALL ON FUNCTION compliance.current_tenant_id() FROM PUBLIC;
REVOKE ALL ON FUNCTION compliance.current_subject_id() FROM PUBLIC;
REVOKE ALL ON FUNCTION compliance.current_processing_purpose() FROM PUBLIC;

COMMENT ON FUNCTION compliance.require_access_context() IS
    'Valida de forma fail-closed o contexto transacional obrigatório antes da avaliação de políticas RLS.';
COMMENT ON FUNCTION compliance.current_tenant_id() IS
    'Retorna o tenant validado da sessão; falha quando o contexto obrigatório está ausente ou inválido.';
COMMENT ON FUNCTION compliance.current_subject_id() IS
    'Retorna o sujeito validado da sessão; falha quando o contexto obrigatório está ausente ou inválido.';
COMMENT ON FUNCTION compliance.current_processing_purpose() IS
    'Retorna a finalidade validada da sessão para uso futuro em políticas ABAC.';

COMMIT;
