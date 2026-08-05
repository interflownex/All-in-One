\set ON_ERROR_STOP on

DO $$
BEGIN
    BEGIN
        PERFORM compliance.require_access_context();
        RAISE EXCEPTION 'expected missing access context to fail closed';
    EXCEPTION
        WHEN SQLSTATE '28000' THEN
            NULL;
    END;
END;
$$;

SELECT set_config('app.tenant_id', '11111111-1111-1111-1111-111111111111', false);
SELECT set_config('app.subject_id', '22222222-2222-2222-2222-222222222222', false);
SELECT set_config('app.subject_type', 'service', false);
SELECT set_config('app.processing_purpose', 'security', false);
SELECT set_config('app.request_id', '33333333-3333-3333-3333-333333333333', false);

SELECT compliance.require_access_context();

DO $$
BEGIN
    IF compliance.current_tenant_id() <> '11111111-1111-1111-1111-111111111111'::uuid THEN
        RAISE EXCEPTION 'validated tenant context was not returned';
    END IF;
    IF compliance.current_subject_id() <> '22222222-2222-2222-2222-222222222222'::uuid THEN
        RAISE EXCEPTION 'validated subject context was not returned';
    END IF;
    IF compliance.current_processing_purpose() <> 'security' THEN
        RAISE EXCEPTION 'validated processing purpose was not returned';
    END IF;
END;
$$;

SELECT set_config('app.processing_purpose', 'unregistered-purpose', false);
DO $$
BEGIN
    BEGIN
        PERFORM compliance.require_access_context();
        RAISE EXCEPTION 'expected an unregistered processing purpose to fail closed';
    EXCEPTION
        WHEN SQLSTATE '28000' THEN
            NULL;
    END;
END;
$$;

SELECT set_config('app.processing_purpose', 'security', false);
SELECT set_config('app.tenant_id', 'not-a-uuid', false);
DO $$
BEGIN
    BEGIN
        PERFORM compliance.require_access_context();
        RAISE EXCEPTION 'expected an invalid tenant UUID to fail';
    EXCEPTION
        WHEN invalid_text_representation THEN
            NULL;
    END;
END;
$$;
