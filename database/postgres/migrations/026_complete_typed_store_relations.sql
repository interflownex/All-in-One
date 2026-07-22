BEGIN;

CREATE SCHEMA IF NOT EXISTS stock;
CREATE SCHEMA IF NOT EXISTS erp;
CREATE SCHEMA IF NOT EXISTS wms;
CREATE SCHEMA IF NOT EXISTS tms;
CREATE SCHEMA IF NOT EXISTS crm;
CREATE SCHEMA IF NOT EXISTS bpm;
CREATE SCHEMA IF NOT EXISTS document;
CREATE SCHEMA IF NOT EXISTS hr;
CREATE SCHEMA IF NOT EXISTS health;
CREATE SCHEMA IF NOT EXISTS vision;
CREATE SCHEMA IF NOT EXISTS legal;
CREATE SCHEMA IF NOT EXISTS property;
CREATE SCHEMA IF NOT EXISTS bi;
CREATE SCHEMA IF NOT EXISTS ai_core;

CREATE TABLE IF NOT EXISTS stock.price_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_stock_price_rules_owner_status ON stock.price_rules (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS stock.supplier_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_stock_supplier_orders_owner_status ON stock.supplier_orders (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS erp.accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_erp_accounts_owner_status ON erp.accounts (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS erp.payables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_erp_payables_owner_status ON erp.payables (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS erp.receivables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_erp_receivables_owner_status ON erp.receivables (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS erp.cost_centers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_erp_cost_centers_owner_status ON erp.cost_centers (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS wms.bins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_wms_bins_owner_status ON wms.bins (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS wms.picking_waves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_wms_picking_waves_owner_status ON wms.picking_waves (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS wms.shipments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_wms_shipments_owner_status ON wms.shipments (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS tms.carriers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_tms_carriers_owner_status ON tms.carriers (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS tms.routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_tms_routes_owner_status ON tms.routes (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS tms.proofs_of_delivery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_tms_proofs_of_delivery_owner_status ON tms.proofs_of_delivery (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS tms.freight_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_tms_freight_audits_owner_status ON tms.freight_audits (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS crm.leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_crm_leads_owner_status ON crm.leads (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS crm.activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_crm_activities_owner_status ON crm.activities (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS crm.campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_crm_campaigns_owner_status ON crm.campaigns (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS bpm.processes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bpm_processes_owner_status ON bpm.processes (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS bpm.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bpm_tasks_owner_status ON bpm.tasks (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS bpm.sla_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bpm_sla_policies_owner_status ON bpm.sla_policies (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS document.folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_document_folders_owner_status ON document.folders (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS document.versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_document_versions_owner_status ON document.versions (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS document.retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_document_retention_policies_owner_status ON document.retention_policies (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS hr.payroll_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_hr_payroll_runs_owner_status ON hr.payroll_runs (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS hr.candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_hr_candidates_owner_status ON hr.candidates (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS hr.courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_hr_courses_owner_status ON hr.courses (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS hr.occupational_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_hr_occupational_records_owner_status ON hr.occupational_records (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS health.medical_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_health_medical_records_owner_status ON health.medical_records (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS health.prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_health_prescriptions_owner_status ON health.prescriptions (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS health.beds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_health_beds_owner_status ON health.beds (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS vision.streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_vision_streams_owner_status ON vision.streams (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS vision.recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_vision_recordings_owner_status ON vision.recordings (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS vision.motion_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_vision_motion_alerts_owner_status ON vision.motion_alerts (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS legal.deadlines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_legal_deadlines_owner_status ON legal.deadlines (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS legal.hearings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_legal_hearings_owner_status ON legal.hearings (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS legal.legal_contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_legal_legal_contracts_owner_status ON legal.legal_contracts (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS property.units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_property_units_owner_status ON property.units (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS property.leases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_property_leases_owner_status ON property.leases (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS property.assemblies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_property_assemblies_owner_status ON property.assemblies (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS property.maintenance_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_property_maintenance_orders_owner_status ON property.maintenance_orders (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS bi.datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bi_datasets_owner_status ON bi.datasets (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS bi.indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bi_indicators_owner_status ON bi.indicators (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS bi.exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_bi_exports_owner_status ON bi.exports (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS ai_core.ai_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_ai_core_ai_memories_owner_status ON ai_core.ai_memories (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS ai_core.model_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES identity.users(id),
    company_id UUID,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    updated_by UUID REFERENCES identity.users(id),
    idempotency_key VARCHAR(160) UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_ai_core_model_runs_owner_status ON ai_core.model_runs (user_id, status, created_at DESC) WHERE deleted_at IS NULL;

COMMIT;

