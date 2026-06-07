BEGIN;

DO $$
DECLARE
    item RECORD;
BEGIN
    FOR item IN
        SELECT *
        FROM (
            VALUES
                ('business', 'branches'),
                ('finance', 'splits'),
                ('finance', 'invoices'),
                ('marketplace', 'carts'),
                ('stock', 'price_rules'),
                ('stock', 'supplier_orders'),
                ('delivery', 'quotes'),
                ('delivery', 'assignments'),
                ('delivery', 'proofs'),
                ('delivery', 'insurance_options'),
                ('riders', 'rider_profiles'),
                ('riders', 'rider_documents'),
                ('riders', 'vehicles'),
                ('riders', 'rider_reviews'),
                ('services', 'visits'),
                ('services', 'quotes'),
                ('services', 'evidence'),
                ('mobility', 'routes'),
                ('mobility', 'stops'),
                ('mobility', 'fare_rules'),
                ('erp', 'accounts'),
                ('erp', 'payables'),
                ('erp', 'receivables'),
                ('erp', 'cost_centers'),
                ('wms', 'bins'),
                ('wms', 'picking_waves'),
                ('wms', 'shipments'),
                ('tms', 'carriers'),
                ('tms', 'routes'),
                ('tms', 'proofs_of_delivery'),
                ('tms', 'freight_audits'),
                ('crm', 'leads'),
                ('crm', 'activities'),
                ('crm', 'campaigns'),
                ('bpm', 'processes'),
                ('bpm', 'tasks'),
                ('bpm', 'sla_policies'),
                ('document', 'folders'),
                ('document', 'versions'),
                ('document', 'retention_policies'),
                ('hr', 'payroll_runs'),
                ('hr', 'candidates'),
                ('hr', 'courses'),
                ('hr', 'occupational_records'),
                ('health', 'medical_records'),
                ('health', 'prescriptions'),
                ('health', 'beds'),
                ('vision', 'streams'),
                ('vision', 'recordings'),
                ('vision', 'motion_alerts'),
                ('legal', 'deadlines'),
                ('legal', 'hearings'),
                ('legal', 'legal_contracts'),
                ('property', 'units'),
                ('property', 'leases'),
                ('property', 'assemblies'),
                ('property', 'maintenance_orders'),
                ('bi', 'datasets'),
                ('bi', 'indicators'),
                ('bi', 'exports'),
                ('ai_core', 'ai_memories'),
                ('ai_core', 'model_runs')
        ) AS missing(schema_name, table_name)
    LOOP
        EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', item.schema_name);
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I.%I (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES identity.users(id),
                company_id UUID REFERENCES business.companies(id),
                status VARCHAR(40) NOT NULL DEFAULT ''draft'',
                metadata JSONB NOT NULL DEFAULT ''{}''::jsonb CHECK (jsonb_typeof(metadata) = ''object''),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                deleted_at TIMESTAMPTZ,
                created_by UUID REFERENCES identity.users(id),
                updated_by UUID REFERENCES identity.users(id),
                idempotency_key VARCHAR(100) UNIQUE
            )',
            item.schema_name,
            item.table_name
        );
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS %I ON %I.%I(user_id, status, created_at)',
            'idx_' || item.schema_name || '_' || item.table_name || '_user_status',
            item.schema_name,
            item.table_name
        );
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS %I ON %I.%I(idempotency_key) WHERE idempotency_key IS NOT NULL',
            'idx_' || item.schema_name || '_' || item.table_name || '_idempotency',
            item.schema_name,
            item.table_name
        );
    END LOOP;
END $$;

COMMIT;
