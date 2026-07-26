SELECT to_regclass('forms.field_catalog') IS NULL AS run_dynamic_forms_migration \gset
\if :run_dynamic_forms_migration
BEGIN;

CREATE SCHEMA IF NOT EXISTS forms;

CREATE TABLE forms.field_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(80) NOT NULL,
    logical_entity VARCHAR(120) NOT NULL,
    logical_field VARCHAR(120) NOT NULL,
    data_type VARCHAR(40) NOT NULL,
    description TEXT NOT NULL,
    allowed_components JSONB NOT NULL DEFAULT '[]'::jsonb,
    mandatory_validations JSONB NOT NULL DEFAULT '[]'::jsonb,
    sensitivity VARCHAR(40) NOT NULL DEFAULT 'internal',
    permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    authorized_binding VARCHAR(240) NOT NULL,
    allowed_operations JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_calculations JSONB NOT NULL DEFAULT '[]'::jsonb,
    unit VARCHAR(40),
    format VARCHAR(80),
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'suspended', 'retired')),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES identity.users(id),
    UNIQUE (domain, logical_entity, logical_field, version),
    CHECK (jsonb_typeof(allowed_components) = 'array'),
    CHECK (jsonb_typeof(mandatory_validations) = 'array'),
    CHECK (authorized_binding !~* '(^|[^a-z_])(select|insert|update|delete|drop|alter|create)([^a-z_]|$)|;|--|/\*')
);

CREATE TABLE forms.field_bindings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_catalog_id UUID NOT NULL REFERENCES forms.field_catalog(id),
    command VARCHAR(160) NOT NULL,
    api VARCHAR(240) NOT NULL,
    dto VARCHAR(160) NOT NULL,
    logical_path VARCHAR(240) NOT NULL,
    data_type VARCHAR(40) NOT NULL,
    transformation VARCHAR(120),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    validation_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    authorization_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'suspended', 'retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (field_catalog_id, version),
    CHECK (logical_path !~* '(^|[^a-z_])(select|insert|update|delete|drop|alter|create)([^a-z_]|$)|;|--|/\*'),
    CHECK (transformation IS NULL OR transformation IN ('identity', 'trim', 'lowercase', 'uppercase', 'decimal', 'date_iso', 'unit_conversion'))
);

CREATE TABLE forms.form_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES business.companies(id),
    module_id VARCHAR(80) NOT NULL,
    business_context VARCHAR(120) NOT NULL,
    name VARCHAR(160) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'suspended', 'retired')),
    current_version_id UUID,
    created_by UUID NOT NULL REFERENCES identity.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID NOT NULL REFERENCES identity.users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE (tenant_id, module_id, business_context, name)
);

CREATE TABLE forms.form_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_definition_id UUID NOT NULL REFERENCES forms.form_definitions(id),
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    schema_version INTEGER NOT NULL DEFAULT 1 CHECK (schema_version > 0),
    status VARCHAR(30) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'editing', 'submitted', 'under_review', 'changes_requested', 'approved', 'published', 'suspended', 'retired', 'rejected')),
    change_summary TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES identity.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMPTZ,
    submitted_by UUID REFERENCES identity.users(id),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES identity.users(id),
    rejected_at TIMESTAMPTZ,
    rejected_by UUID REFERENCES identity.users(id),
    rejection_reason TEXT,
    published_at TIMESTAMPTZ,
    published_by UUID REFERENCES identity.users(id),
    retired_at TIMESTAMPTZ,
    checksum CHAR(64),
    UNIQUE (form_definition_id, version_number),
    CHECK ((status NOT IN ('submitted', 'under_review')) OR (submitted_at IS NOT NULL AND submitted_by IS NOT NULL)),
    CHECK ((status <> 'approved') OR (approved_at IS NOT NULL AND approved_by IS NOT NULL)),
    CHECK ((status <> 'rejected') OR (rejected_at IS NOT NULL AND rejected_by IS NOT NULL AND rejection_reason IS NOT NULL)),
    CHECK ((status <> 'published') OR (published_at IS NOT NULL AND published_by IS NOT NULL AND approved_at IS NOT NULL AND checksum IS NOT NULL))
);

ALTER TABLE forms.form_definitions
    ADD CONSTRAINT form_definitions_current_version_fk
    FOREIGN KEY (current_version_id) REFERENCES forms.form_versions(id);

CREATE TABLE forms.form_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id) ON DELETE CASCADE,
    block_type VARCHAR(30) NOT NULL CHECK (block_type IN ('section', 'group', 'tab', 'column')),
    parent_block_id UUID REFERENCES forms.form_blocks(id) ON DELETE CASCADE,
    display_order INTEGER NOT NULL CHECK (display_order >= 0),
    title VARCHAR(160) NOT NULL,
    description TEXT,
    width SMALLINT NOT NULL DEFAULT 12 CHECK (width BETWEEN 1 AND 12),
    collapsible BOOLEAN NOT NULL DEFAULT FALSE,
    visibility_rule_id UUID,
    repeatable BOOLEAN NOT NULL DEFAULT FALSE,
    allowed_style VARCHAR(40) NOT NULL DEFAULT 'default' CHECK (allowed_style IN ('default', 'compact', 'highlight', 'bordered')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (form_version_id, parent_block_id, display_order)
);

CREATE TABLE forms.form_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id) ON DELETE CASCADE,
    block_id UUID NOT NULL REFERENCES forms.form_blocks(id) ON DELETE CASCADE,
    field_catalog_id UUID NOT NULL REFERENCES forms.field_catalog(id),
    field_binding_id UUID NOT NULL REFERENCES forms.field_bindings(id),
    component VARCHAR(40) NOT NULL CHECK (component IN ('text', 'textarea', 'number', 'decimal', 'date', 'datetime', 'select', 'multiselect', 'checkbox', 'radio', 'file', 'currency', 'unit', 'email', 'phone')),
    label VARCHAR(160) NOT NULL,
    help_text TEXT,
    placeholder VARCHAR(240),
    required BOOLEAN NOT NULL DEFAULT FALSE,
    read_only BOOLEAN NOT NULL DEFAULT FALSE,
    hidden BOOLEAN NOT NULL DEFAULT FALSE,
    display_order INTEGER NOT NULL CHECK (display_order >= 0),
    width SMALLINT NOT NULL DEFAULT 12 CHECK (width BETWEEN 1 AND 12),
    mask VARCHAR(80),
    format VARCHAR(80),
    default_value JSONB,
    value_source VARCHAR(40) NOT NULL DEFAULT 'user' CHECK (value_source IN ('user', 'context', 'backend', 'calculation')),
    unit VARCHAR(40),
    permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
    visibility_rule_id UUID,
    validation_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    audit_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (form_version_id, field_catalog_id),
    UNIQUE (block_id, display_order),
    CHECK (jsonb_typeof(validation_ids) = 'array')
);

CREATE TABLE forms.form_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    result_field_id UUID NOT NULL REFERENCES forms.form_fields(id),
    operand_field_ids JSONB NOT NULL,
    operation VARCHAR(40) NOT NULL CHECK (operation IN ('sum', 'subtract', 'multiply', 'divide', 'percentage', 'average', 'minimum', 'maximum', 'count', 'date_difference', 'unit_conversion', 'round', 'conditional', 'controlled_text_composition')),
    safe_expression JSONB NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    precision SMALLINT CHECK (precision BETWEEN 0 AND 12),
    rounding VARCHAR(20) CHECK (rounding IN ('half_up', 'half_even', 'floor', 'ceiling')),
    trigger_mode VARCHAR(30) NOT NULL DEFAULT 'on_change' CHECK (trigger_mode IN ('on_change', 'on_blur', 'on_submit')),
    condition JSONB,
    unit VARCHAR(40),
    null_handling VARCHAR(30) NOT NULL DEFAULT 'error' CHECK (null_handling IN ('error', 'zero', 'ignore')),
    division_by_zero_handling VARCHAR(30) NOT NULL DEFAULT 'error' CHECK (division_by_zero_handling IN ('error', 'null', 'zero')),
    visibility VARCHAR(30) NOT NULL DEFAULT 'visible' CHECK (visibility IN ('visible', 'hidden', 'read_only')),
    validation JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'suspended', 'retired')),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (form_version_id, name, version),
    CHECK (jsonb_typeof(operand_field_ids) = 'array'),
    CHECK (jsonb_typeof(safe_expression) IN ('object', 'array'))
);

CREATE TABLE forms.form_validations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id) ON DELETE CASCADE,
    field_id UUID REFERENCES forms.form_fields(id) ON DELETE CASCADE,
    validation_type VARCHAR(40) NOT NULL CHECK (validation_type IN ('required', 'min_length', 'max_length', 'minimum', 'maximum', 'regex_allowlist', 'email', 'phone', 'date_range', 'enum', 'document_checksum', 'custom_catalog_rule')),
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    message_pt_br VARCHAR(300) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'error' CHECK (severity IN ('info', 'warning', 'error', 'blocking')),
    condition JSONB,
    run_frontend BOOLEAN NOT NULL DEFAULT TRUE,
    run_backend BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'suspended', 'retired')),
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    CHECK (run_backend OR severity NOT IN ('error', 'blocking'))
);

CREATE TABLE forms.form_visibility_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id) ON DELETE CASCADE,
    target_type VARCHAR(20) NOT NULL CHECK (target_type IN ('form', 'block', 'field')),
    target_id UUID NOT NULL,
    condition JSONB NOT NULL,
    operator VARCHAR(30) NOT NULL CHECK (operator IN ('equals', 'not_equals', 'contains', 'in', 'greater_than', 'less_than', 'is_empty', 'is_not_empty')),
    comparison_value JSONB,
    result VARCHAR(30) NOT NULL CHECK (result IN ('show', 'hide', 'enable', 'disable', 'require', 'optional')),
    priority INTEGER NOT NULL DEFAULT 0,
    combination VARCHAR(10) NOT NULL DEFAULT 'and' CHECK (combination IN ('and', 'or')),
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'suspended', 'retired')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id)
);

ALTER TABLE forms.form_blocks ADD CONSTRAINT form_blocks_visibility_fk FOREIGN KEY (visibility_rule_id) REFERENCES forms.form_visibility_rules(id);
ALTER TABLE forms.form_fields ADD CONSTRAINT form_fields_visibility_fk FOREIGN KEY (visibility_rule_id) REFERENCES forms.form_visibility_rules(id);

CREATE TABLE forms.form_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_definition_id UUID NOT NULL REFERENCES forms.form_definitions(id) ON DELETE CASCADE,
    form_version_id UUID REFERENCES forms.form_versions(id) ON DELETE CASCADE,
    role VARCHAR(80) NOT NULL,
    attribute_condition JSONB NOT NULL DEFAULT '{}'::jsonb,
    can_view BOOLEAN NOT NULL DEFAULT FALSE,
    can_create BOOLEAN NOT NULL DEFAULT FALSE,
    can_edit BOOLEAN NOT NULL DEFAULT FALSE,
    can_approve BOOLEAN NOT NULL DEFAULT FALSE,
    can_publish BOOLEAN NOT NULL DEFAULT FALSE,
    can_export BOOLEAN NOT NULL DEFAULT FALSE,
    can_print BOOLEAN NOT NULL DEFAULT FALSE,
    can_access_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (form_definition_id, form_version_id, role)
);

CREATE TABLE forms.form_homologations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id),
    requester_id UUID NOT NULL REFERENCES identity.users(id),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    checklist JSONB NOT NULL,
    result VARCHAR(30) CHECK (result IN ('approved', 'changes_requested', 'rejected')),
    reviewer_id UUID REFERENCES identity.users(id),
    reviewed_at TIMESTAMPTZ,
    notes TEXT,
    problems JSONB NOT NULL DEFAULT '[]'::jsonb,
    corrections JSONB NOT NULL DEFAULT '[]'::jsonb,
    revalidation JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(30) NOT NULL DEFAULT 'requested' CHECK (status IN ('requested', 'under_review', 'approved', 'changes_requested', 'rejected', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK ((status NOT IN ('approved', 'changes_requested', 'rejected')) OR (reviewer_id IS NOT NULL AND reviewed_at IS NOT NULL AND result IS NOT NULL))
);

CREATE TABLE forms.form_publications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id),
    environment VARCHAR(30) NOT NULL CHECK (environment IN ('development', 'homologation', 'production')),
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_by UUID NOT NULL REFERENCES identity.users(id),
    rollout_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    rollback_version_id UUID REFERENCES forms.form_versions(id),
    tenant_scope JSONB NOT NULL,
    channels JSONB NOT NULL DEFAULT '["web"]'::jsonb,
    checksum CHAR(64) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'rolled_back', 'suspended', 'retired')),
    UNIQUE (form_version_id, environment, checksum)
);

CREATE TABLE forms.form_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_definition_id UUID NOT NULL REFERENCES forms.form_definitions(id),
    form_version_id UUID NOT NULL REFERENCES forms.form_versions(id),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    tenant_id UUID NOT NULL,
    context JSONB NOT NULL DEFAULT '{}'::jsonb,
    target_entity VARCHAR(120) NOT NULL,
    target_entity_id UUID,
    status VARCHAR(30) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'validating', 'invalid', 'completed', 'cancelled')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    source VARCHAR(30) NOT NULL CHECK (source IN ('web', 'mobile', 'api', 'import')),
    correlation_id UUID NOT NULL,
    idempotency_key VARCHAR(160) NOT NULL,
    validation_result JSONB NOT NULL DEFAULT '{}'::jsonb,
    audit_event_id UUID REFERENCES audit.domain_events(id),
    UNIQUE (tenant_id, idempotency_key),
    CHECK ((status <> 'completed') OR completed_at IS NOT NULL)
);

CREATE TABLE forms.form_submission_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL REFERENCES forms.form_submissions(id) ON DELETE CASCADE,
    field_catalog_id UUID NOT NULL REFERENCES forms.field_catalog(id),
    data_type VARCHAR(40) NOT NULL,
    normalized_value JSONB,
    display_value TEXT,
    unit VARCHAR(40),
    source VARCHAR(30) NOT NULL CHECK (source IN ('user', 'context', 'backend', 'calculation', 'import')),
    validation_result JSONB NOT NULL DEFAULT '{}'::jsonb,
    sensitivity VARCHAR(40) NOT NULL DEFAULT 'internal',
    encryption VARCHAR(40) NOT NULL DEFAULT 'platform_managed' CHECK (encryption IN ('none', 'platform_managed', 'field_level', 'tokenized')),
    schema_version INTEGER NOT NULL DEFAULT 1 CHECK (schema_version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (submission_id, field_catalog_id)
);

CREATE TABLE forms.form_billing_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    form_definition_id UUID REFERENCES forms.form_definitions(id),
    form_version_id UUID REFERENCES forms.form_versions(id),
    event_type VARCHAR(60) NOT NULL CHECK (event_type IN ('form_request_created', 'homologation_submitted', 'homologation_approved', 'initial_publication', 'change_requested', 'new_homologation', 'new_version_published', 'special_maintenance', 'technical_support', 'advanced_customization')),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor_user_id UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) NOT NULL,
    billing_reference JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(30) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'reported', 'cancelled')),
    UNIQUE (tenant_id, idempotency_key)
);

CREATE INDEX idx_form_definitions_tenant_status ON forms.form_definitions (tenant_id, status, updated_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_form_versions_definition_status ON forms.form_versions (form_definition_id, status, version_number DESC);
CREATE INDEX idx_form_blocks_version_order ON forms.form_blocks (form_version_id, parent_block_id, display_order);
CREATE INDEX idx_form_fields_version_order ON forms.form_fields (form_version_id, block_id, display_order);
CREATE INDEX idx_form_permissions_role ON forms.form_permissions (role, form_definition_id);
CREATE INDEX idx_form_homologations_queue ON forms.form_homologations (status, requested_at) WHERE status IN ('requested', 'under_review');
CREATE INDEX idx_form_publications_active ON forms.form_publications (environment, published_at DESC) WHERE status = 'active';
CREATE INDEX idx_form_submissions_tenant_status ON forms.form_submissions (tenant_id, status, started_at DESC);
CREATE INDEX idx_form_billing_pending ON forms.form_billing_events (status, occurred_at) WHERE status = 'pending';

CREATE OR REPLACE FUNCTION forms.reject_published_version_mutation()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'published' THEN
        IF TG_OP = 'DELETE' THEN
            RAISE EXCEPTION 'Versao publicada e imutavel; crie uma nova versao.';
        END IF;
        IF NEW.status NOT IN ('suspended', 'retired')
           OR NEW.form_definition_id IS DISTINCT FROM OLD.form_definition_id
           OR NEW.version_number IS DISTINCT FROM OLD.version_number
           OR NEW.schema_version IS DISTINCT FROM OLD.schema_version
           OR NEW.change_summary IS DISTINCT FROM OLD.change_summary
           OR NEW.created_by IS DISTINCT FROM OLD.created_by
           OR NEW.created_at IS DISTINCT FROM OLD.created_at
           OR NEW.submitted_at IS DISTINCT FROM OLD.submitted_at
           OR NEW.submitted_by IS DISTINCT FROM OLD.submitted_by
           OR NEW.approved_at IS DISTINCT FROM OLD.approved_at
           OR NEW.approved_by IS DISTINCT FROM OLD.approved_by
           OR NEW.published_at IS DISTINCT FROM OLD.published_at
           OR NEW.published_by IS DISTINCT FROM OLD.published_by
           OR NEW.checksum IS DISTINCT FROM OLD.checksum THEN
            RAISE EXCEPTION 'Versao publicada e imutavel; somente suspensao ou aposentadoria sao permitidas.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER immutable_published_form_version
BEFORE UPDATE OR DELETE ON forms.form_versions
FOR EACH ROW EXECUTE FUNCTION forms.reject_published_version_mutation();

CREATE OR REPLACE FUNCTION forms.reject_published_child_mutation()
RETURNS TRIGGER AS $$
DECLARE
    version_id UUID;
BEGIN
    IF TG_OP = 'DELETE' THEN
        version_id := OLD.form_version_id;
    ELSE
        version_id := NEW.form_version_id;
    END IF;
    IF EXISTS (SELECT 1 FROM forms.form_versions WHERE id = version_id AND status = 'published') THEN
        RAISE EXCEPTION 'Metadados de versao publicada sao imutaveis; crie uma nova versao.';
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER immutable_published_blocks BEFORE INSERT OR UPDATE OR DELETE ON forms.form_blocks FOR EACH ROW EXECUTE FUNCTION forms.reject_published_child_mutation();
CREATE TRIGGER immutable_published_fields BEFORE INSERT OR UPDATE OR DELETE ON forms.form_fields FOR EACH ROW EXECUTE FUNCTION forms.reject_published_child_mutation();
CREATE TRIGGER immutable_published_calculations BEFORE INSERT OR UPDATE OR DELETE ON forms.form_calculations FOR EACH ROW EXECUTE FUNCTION forms.reject_published_child_mutation();
CREATE TRIGGER immutable_published_validations BEFORE INSERT OR UPDATE OR DELETE ON forms.form_validations FOR EACH ROW EXECUTE FUNCTION forms.reject_published_child_mutation();
CREATE TRIGGER immutable_published_visibility BEFORE INSERT OR UPDATE OR DELETE ON forms.form_visibility_rules FOR EACH ROW EXECUTE FUNCTION forms.reject_published_child_mutation();

COMMIT;
\else
\echo 'Migração 028 já aplicada; repetição ignorada com segurança.'
\endif
