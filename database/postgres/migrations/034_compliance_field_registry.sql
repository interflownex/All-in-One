BEGIN;

CREATE TABLE IF NOT EXISTS compliance.catalog_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_version VARCHAR(16) NOT NULL,
    baseline_sha CHAR(40) NOT NULL,
    status VARCHAR(24) NOT NULL DEFAULT 'active',
    activated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    retired_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id)
);

ALTER TABLE compliance.catalog_versions
    ADD CONSTRAINT compliance_catalog_versions_baseline_sha
    CHECK (baseline_sha ~ '^[0-9a-f]{40}$');

ALTER TABLE compliance.catalog_versions
    ADD CONSTRAINT compliance_catalog_versions_status
    CHECK (status = ANY (ARRAY['active'::varchar, 'retired'::varchar, 'superseded'::varchar]));

ALTER TABLE compliance.catalog_versions
    ADD CONSTRAINT compliance_catalog_versions_window
    CHECK (retired_at IS NULL OR retired_at >= activated_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_compliance_catalog_versions_schema
    ON compliance.catalog_versions (schema_version);

CREATE UNIQUE INDEX IF NOT EXISTS idx_compliance_catalog_versions_active
    ON compliance.catalog_versions (status)
    WHERE status = 'active';

CREATE TABLE IF NOT EXISTS compliance.field_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    catalog_version_id UUID NOT NULL REFERENCES compliance.catalog_versions(id),
    field_id VARCHAR(160) NOT NULL,
    asset VARCHAR(256) NOT NULL,
    field_name VARCHAR(160) NOT NULL,
    owner VARCHAR(160) NOT NULL,
    physical_type VARCHAR(96) NOT NULL,
    required BOOLEAN NOT NULL,
    purpose TEXT NOT NULL,
    legal_basis VARCHAR(160) NOT NULL,
    sensitivity VARCHAR(32) NOT NULL,
    retention_policy VARCHAR(160) NOT NULL,
    access_policy VARCHAR(160) NOT NULL,
    security_policy VARCHAR(160) NOT NULL,
    source TEXT NOT NULL,
    lineage JSONB NOT NULL DEFAULT '[]'::jsonb,
    disposal_policy VARCHAR(160) NOT NULL,
    status VARCHAR(32) NOT NULL,
    bundle_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_to TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id)
);

ALTER TABLE compliance.field_registry
    ADD CONSTRAINT compliance_field_registry_sensitivity
    CHECK (
        sensitivity = ANY (
            ARRAY[
                'public'::varchar,
                'internal'::varchar,
                'personal'::varchar,
                'sensitive_personal'::varchar,
                'financial'::varchar,
                'secret'::varchar
            ]
        )
    );

ALTER TABLE compliance.field_registry
    ADD CONSTRAINT compliance_field_registry_status
    CHECK (
        status = ANY (
            ARRAY[
                'implemented'::varchar,
                'partial'::varchar,
                'planned'::varchar,
                'conditional'::varchar,
                'divergent'::varchar
            ]
        )
    );

ALTER TABLE compliance.field_registry
    ADD CONSTRAINT compliance_field_registry_lineage_array
    CHECK (jsonb_typeof(lineage) = 'array');

ALTER TABLE compliance.field_registry
    ADD CONSTRAINT compliance_field_registry_bundle_ids_array
    CHECK (jsonb_typeof(bundle_ids) = 'array');

ALTER TABLE compliance.field_registry
    ADD CONSTRAINT compliance_field_registry_effective_window
    CHECK (effective_to IS NULL OR effective_to >= effective_from);

ALTER TABLE compliance.field_registry
    ADD CONSTRAINT compliance_field_registry_field_id_format
    CHECK (field_id ~ '^[a-z0-9_.-]+$');

CREATE UNIQUE INDEX IF NOT EXISTS idx_compliance_field_registry_field_id
    ON compliance.field_registry (catalog_version_id, field_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_compliance_field_registry_asset_field
    ON compliance.field_registry (catalog_version_id, asset, field_name);

CREATE INDEX IF NOT EXISTS idx_compliance_field_registry_owner_status
    ON compliance.field_registry (owner, status, asset);

CREATE INDEX IF NOT EXISTS idx_compliance_field_registry_effective
    ON compliance.field_registry (effective_from, effective_to);

CREATE INDEX IF NOT EXISTS idx_compliance_field_registry_bundle_ids
    ON compliance.field_registry USING GIN (bundle_ids);

CREATE INDEX IF NOT EXISTS idx_compliance_field_registry_lineage
    ON compliance.field_registry USING GIN (lineage);

INSERT INTO compliance.catalog_versions (
    id,
    schema_version,
    baseline_sha,
    status
)
VALUES (
    '00000000-0000-4000-8000-000000000034',
    '1.0.0',
    'ab2ebca1849d2e3ed31ca8922ab74a0215e04939',
    'active'
)
ON CONFLICT (schema_version) DO UPDATE
SET baseline_sha = EXCLUDED.baseline_sha,
    status = 'active',
    retired_at = NULL;

WITH active_catalog AS (
    SELECT id
    FROM compliance.catalog_versions
    WHERE schema_version = '1.0.0'
),
common AS (
    SELECT
        'equipe-governanca-dados'::varchar AS owner,
        'obrigacao_legal_e_governanca_interna_sujeita_validacao_dpo'::varchar AS legal_basis,
        'vigencia_do_catalogo_mais_5_anos_ou_legal_hold'::varchar AS retention_policy,
        'rbac_compliance_admin_leitura_auditoria'::varchar AS access_policy,
        'criptografia_em_reposo_tls_em_transito_logs_sem_payload'::varchar AS security_policy,
        'database/postgres/migrations/034_compliance_field_registry.sql'::text AS source,
        '["config/compliance/field_registry.v1.json","database/postgres/migrations/034_compliance_field_registry.sql"]'::jsonb AS lineage,
        'expurgo_controlado_apos_retencao_sem_legal_hold'::varchar AS disposal_policy,
        'implemented'::varchar AS status
),
seed (
    field_id,
    asset,
    field_name,
    physical_type,
    required,
    purpose,
    sensitivity,
    bundle_ids
) AS (
    VALUES
        ('compliance.catalog_versions.id', 'compliance.catalog_versions', 'id', 'uuid', TRUE, 'Identificar de forma única a versão física do catálogo.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.catalog_versions.schema_version', 'compliance.catalog_versions', 'schema_version', 'varchar(16)', TRUE, 'Vincular registros ao contrato semântico versionado.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.catalog_versions.baseline_sha', 'compliance.catalog_versions', 'baseline_sha', 'char(40)', TRUE, 'Fixar a baseline Git usada pelo gate incremental.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.catalog_versions.status', 'compliance.catalog_versions', 'status', 'varchar(24)', TRUE, 'Controlar o ciclo de vida da versão do catálogo.', 'internal', '["B0","B4","B11"]'::jsonb),
        ('compliance.catalog_versions.activated_at', 'compliance.catalog_versions', 'activated_at', 'timestamptz', TRUE, 'Registrar quando a versão passou a vigorar.', 'internal', '["B0","B4","B11"]'::jsonb),
        ('compliance.catalog_versions.retired_at', 'compliance.catalog_versions', 'retired_at', 'timestamptz', FALSE, 'Registrar quando a versão deixou de vigorar.', 'internal', '["B0","B4","B11"]'::jsonb),
        ('compliance.catalog_versions.created_at', 'compliance.catalog_versions', 'created_at', 'timestamptz', TRUE, 'Registrar a criação técnica da versão.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.catalog_versions.created_by', 'compliance.catalog_versions', 'created_by', 'uuid', FALSE, 'Identificar o usuário responsável pela criação quando aplicável.', 'personal', '["B0","B3","B4","B5","B8","B11"]'::jsonb),
        ('compliance.field_registry.id', 'compliance.field_registry', 'id', 'uuid', TRUE, 'Identificar de forma única o registro físico do campo.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.catalog_version_id', 'compliance.field_registry', 'catalog_version_id', 'uuid', TRUE, 'Vincular o campo à versão vigente do catálogo.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.field_id', 'compliance.field_registry', 'field_id', 'varchar(160)', TRUE, 'Manter o identificador estável do campo regulatório.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.asset', 'compliance.field_registry', 'asset', 'varchar(256)', TRUE, 'Identificar o ativo físico ou lógico que contém o campo.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.field_name', 'compliance.field_registry', 'field_name', 'varchar(160)', TRUE, 'Identificar o nome físico do campo catalogado.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.owner', 'compliance.field_registry', 'owner', 'varchar(160)', TRUE, 'Definir a equipe responsável pelo campo.', 'internal', '["B0","B5","B8"]'::jsonb),
        ('compliance.field_registry.physical_type', 'compliance.field_registry', 'physical_type', 'varchar(96)', TRUE, 'Registrar o tipo físico esperado.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.required', 'compliance.field_registry', 'required', 'boolean', TRUE, 'Indicar se o preenchimento é obrigatório.', 'internal', '["B0","B1"]'::jsonb),
        ('compliance.field_registry.purpose', 'compliance.field_registry', 'purpose', 'text', TRUE, 'Registrar a finalidade específica do tratamento.', 'internal', '["B1","B8","B12"]'::jsonb),
        ('compliance.field_registry.legal_basis', 'compliance.field_registry', 'legal_basis', 'varchar(160)', TRUE, 'Registrar a base legal declarada para revisão.', 'internal', '["B2","B9","B13"]'::jsonb),
        ('compliance.field_registry.sensitivity', 'compliance.field_registry', 'sensitivity', 'varchar(32)', TRUE, 'Classificar a sensibilidade do campo.', 'internal', '["B3"]'::jsonb),
        ('compliance.field_registry.retention_policy', 'compliance.field_registry', 'retention_policy', 'varchar(160)', TRUE, 'Referenciar a política de retenção aplicável.', 'internal', '["B4","B11"]'::jsonb),
        ('compliance.field_registry.access_policy', 'compliance.field_registry', 'access_policy', 'varchar(160)', TRUE, 'Referenciar a política de acesso e isolamento.', 'internal', '["B5","B13","B14"]'::jsonb),
        ('compliance.field_registry.security_policy', 'compliance.field_registry', 'security_policy', 'varchar(160)', TRUE, 'Referenciar controles de segurança e criptografia.', 'internal', '["B6","B10","B14"]'::jsonb),
        ('compliance.field_registry.source', 'compliance.field_registry', 'source', 'text', TRUE, 'Registrar a fonte técnica da definição.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.lineage', 'compliance.field_registry', 'lineage', 'jsonb', TRUE, 'Registrar a linhagem técnica sem armazenar payload pessoal.', 'internal', '["B0","B7","B11"]'::jsonb),
        ('compliance.field_registry.disposal_policy', 'compliance.field_registry', 'disposal_policy', 'varchar(160)', TRUE, 'Referenciar o descarte após retenção e legal hold.', 'internal', '["B4","B14"]'::jsonb),
        ('compliance.field_registry.status', 'compliance.field_registry', 'status', 'varchar(32)', TRUE, 'Registrar o estado de implementação do campo.', 'internal', '["B0","B9","B12"]'::jsonb),
        ('compliance.field_registry.bundle_ids', 'compliance.field_registry', 'bundle_ids', 'jsonb', TRUE, 'Vincular o campo aos bundles regulatórios B0-B14.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.effective_from', 'compliance.field_registry', 'effective_from', 'timestamptz', TRUE, 'Registrar o início da vigência do registro.', 'internal', '["B0","B4","B11"]'::jsonb),
        ('compliance.field_registry.effective_to', 'compliance.field_registry', 'effective_to', 'timestamptz', FALSE, 'Registrar o fim da vigência do registro.', 'internal', '["B0","B4","B11"]'::jsonb),
        ('compliance.field_registry.created_at', 'compliance.field_registry', 'created_at', 'timestamptz', TRUE, 'Registrar a criação técnica do registro.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.updated_at', 'compliance.field_registry', 'updated_at', 'timestamptz', TRUE, 'Registrar a última atualização técnica do registro.', 'internal', '["B0","B11"]'::jsonb),
        ('compliance.field_registry.created_by', 'compliance.field_registry', 'created_by', 'uuid', FALSE, 'Identificar o usuário responsável pela criação quando aplicável.', 'personal', '["B0","B3","B4","B5","B8","B11"]'::jsonb),
        ('compliance.field_registry.updated_by', 'compliance.field_registry', 'updated_by', 'uuid', FALSE, 'Identificar o usuário responsável pela atualização quando aplicável.', 'personal', '["B0","B3","B4","B5","B8","B11"]'::jsonb)
)
INSERT INTO compliance.field_registry (
    catalog_version_id,
    field_id,
    asset,
    field_name,
    owner,
    physical_type,
    required,
    purpose,
    legal_basis,
    sensitivity,
    retention_policy,
    access_policy,
    security_policy,
    source,
    lineage,
    disposal_policy,
    status,
    bundle_ids
)
SELECT
    active_catalog.id,
    seed.field_id,
    seed.asset,
    seed.field_name,
    common.owner,
    seed.physical_type,
    seed.required,
    seed.purpose,
    common.legal_basis,
    seed.sensitivity,
    common.retention_policy,
    common.access_policy,
    common.security_policy,
    common.source,
    common.lineage,
    common.disposal_policy,
    common.status,
    seed.bundle_ids
FROM active_catalog
CROSS JOIN common
CROSS JOIN seed
ON CONFLICT (catalog_version_id, field_id) DO UPDATE
SET asset = EXCLUDED.asset,
    field_name = EXCLUDED.field_name,
    owner = EXCLUDED.owner,
    physical_type = EXCLUDED.physical_type,
    required = EXCLUDED.required,
    purpose = EXCLUDED.purpose,
    legal_basis = EXCLUDED.legal_basis,
    sensitivity = EXCLUDED.sensitivity,
    retention_policy = EXCLUDED.retention_policy,
    access_policy = EXCLUDED.access_policy,
    security_policy = EXCLUDED.security_policy,
    source = EXCLUDED.source,
    lineage = EXCLUDED.lineage,
    disposal_policy = EXCLUDED.disposal_policy,
    status = EXCLUDED.status,
    bundle_ids = EXCLUDED.bundle_ids,
    updated_at = NOW();

COMMENT ON TABLE compliance.catalog_versions IS
    'Versões físicas do catálogo regulatório executável All in One + Valley.';

COMMENT ON TABLE compliance.field_registry IS
    'Registro físico versionado dos campos, finalidades, bases, controles e retenção.';

COMMIT;
