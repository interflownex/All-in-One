BEGIN;

CREATE TABLE IF NOT EXISTS stock.measurement_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) NOT NULL UNIQUE,
    symbol VARCHAR(24) NOT NULL,
    singular_name_pt_br VARCHAR(120) NOT NULL,
    plural_name_pt_br VARCHAR(120) NOT NULL,
    dimension VARCHAR(40) NOT NULL,
    measurement_system VARCHAR(40) NOT NULL,
    precision SMALLINT NOT NULL DEFAULT 6 CHECK (precision BETWEEN 0 AND 12),
    scale NUMERIC(30, 12) NOT NULL DEFAULT 1 CHECK (scale > 0),
    allows_fraction BOOLEAN NOT NULL DEFAULT TRUE,
    base_unit_id UUID REFERENCES stock.measurement_units(id),
    normative_equivalence TEXT,
    regional_rules JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES identity.users(id),
    CHECK (base_unit_id IS NULL OR base_unit_id <> id)
);

CREATE TABLE IF NOT EXISTS stock.product_units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES business.companies(id),
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    unit_id UUID NOT NULL REFERENCES stock.measurement_units(id),
    purpose VARCHAR(40) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    minimum_quantity NUMERIC(30, 12),
    maximum_quantity NUMERIC(30, 12),
    quantity_step NUMERIC(30, 12) NOT NULL DEFAULT 1 CHECK (quantity_step > 0),
    precision SMALLINT NOT NULL DEFAULT 6 CHECK (precision BETWEEN 0 AND 12),
    rounding_mode VARCHAR(24) NOT NULL DEFAULT 'half_up',
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES identity.users(id),
    CHECK (maximum_quantity IS NULL OR minimum_quantity IS NULL OR maximum_quantity >= minimum_quantity),
    CHECK (effective_to IS NULL OR effective_to > effective_from),
    CHECK (rounding_mode IN ('half_up', 'half_even', 'floor', 'ceiling')),
    CHECK (status <> 'approved' OR (approved_at IS NOT NULL AND approved_by IS NOT NULL))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_stock_product_units_default
    ON stock.product_units (tenant_id, product_id, purpose)
    WHERE is_default AND effective_to IS NULL AND status = 'approved';

CREATE TABLE IF NOT EXISTS stock.product_unit_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES business.companies(id),
    branch_id UUID REFERENCES business.branches(id),
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    source_unit_id UUID NOT NULL REFERENCES stock.measurement_units(id),
    target_unit_id UUID NOT NULL REFERENCES stock.measurement_units(id),
    multiplier NUMERIC(30, 12) NOT NULL DEFAULT 1 CHECK (multiplier > 0),
    divisor NUMERIC(30, 12) NOT NULL DEFAULT 1 CHECK (divisor > 0),
    safe_formula VARCHAR(500),
    precision SMALLINT NOT NULL DEFAULT 6 CHECK (precision BETWEEN 0 AND 12),
    rounding_mode VARCHAR(24) NOT NULL DEFAULT 'half_up',
    tolerance NUMERIC(30, 12) NOT NULL DEFAULT 0 CHECK (tolerance >= 0),
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    context VARCHAR(80) NOT NULL,
    supplier_id UUID REFERENCES stock.suppliers(id),
    package_id UUID,
    density NUMERIC(30, 12) CHECK (density > 0),
    reference_temperature NUMERIC(12, 4),
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES identity.users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    CHECK (source_unit_id <> target_unit_id),
    CHECK (effective_to IS NULL OR effective_to > effective_from),
    CHECK (rounding_mode IN ('half_up', 'half_even', 'floor', 'ceiling')),
    CHECK (status <> 'approved' OR (approved_at IS NOT NULL AND approved_by IS NOT NULL))
);

CREATE INDEX IF NOT EXISTS idx_stock_unit_conversion_lookup
    ON stock.product_unit_conversions (tenant_id, product_id, source_unit_id, target_unit_id, effective_from DESC);

CREATE TABLE IF NOT EXISTS stock.product_lots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES business.companies(id),
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    lot_number VARCHAR(120) NOT NULL,
    sub_lot VARCHAR(120),
    manufactured_on DATE,
    expires_on DATE,
    received_at TIMESTAMPTZ,
    supplier_id UUID REFERENCES stock.suppliers(id),
    origin VARCHAR(160),
    quality_status VARCHAR(40) NOT NULL DEFAULT 'pending_inspection',
    inspection_id UUID,
    quarantine_reason TEXT,
    released_at TIMESTAMPTZ,
    blocked_at TIMESTAMPTZ,
    recall_status VARCHAR(40) NOT NULL DEFAULT 'clear',
    cost_method VARCHAR(40) NOT NULL DEFAULT 'weighted_average',
    status VARCHAR(40) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (tenant_id, product_id, lot_number, sub_lot),
    CHECK (expires_on IS NULL OR manufactured_on IS NULL OR expires_on >= manufactured_on)
);

CREATE TABLE IF NOT EXISTS stock.product_serials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    lot_id UUID REFERENCES stock.product_lots(id),
    serial_number VARCHAR(180) NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'available',
    location_id UUID,
    warranty_until DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES identity.users(id),
    UNIQUE (tenant_id, product_id, serial_number)
);

CREATE TABLE IF NOT EXISTS stock.stock_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID REFERENCES business.companies(id),
    branch_id UUID REFERENCES business.branches(id),
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    lot_id UUID REFERENCES stock.product_lots(id),
    serial_id UUID REFERENCES stock.product_serials(id),
    source_location_id UUID,
    target_location_id UUID,
    movement_type VARCHAR(40) NOT NULL,
    informed_quantity NUMERIC(30, 12) NOT NULL,
    informed_unit_id UUID NOT NULL REFERENCES stock.measurement_units(id),
    base_quantity NUMERIC(30, 12) NOT NULL,
    base_unit_id UUID NOT NULL REFERENCES stock.measurement_units(id),
    conversion_id UUID REFERENCES stock.product_unit_conversions(id),
    conversion_factor_snapshot NUMERIC(30, 12) NOT NULL CHECK (conversion_factor_snapshot > 0),
    previous_balance NUMERIC(30, 12) NOT NULL,
    new_balance NUMERIC(30, 12) NOT NULL,
    unit_cost NUMERIC(30, 12) CHECK (unit_cost >= 0),
    total_value NUMERIC(30, 12) CHECK (total_value >= 0),
    currency_code CHAR(3) NOT NULL DEFAULT 'BRL',
    reason TEXT NOT NULL,
    document_id UUID,
    order_id UUID REFERENCES marketplace.orders(id),
    correlation_id UUID NOT NULL,
    idempotency_key VARCHAR(120) NOT NULL UNIQUE,
    occurred_at TIMESTAMPTZ NOT NULL,
    created_by UUID NOT NULL REFERENCES identity.users(id),
    CHECK (source_location_id IS NOT NULL OR target_location_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS erp.fiscal_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID NOT NULL REFERENCES business.companies(id),
    name VARCHAR(160) NOT NULL,
    country_code CHAR(2) NOT NULL DEFAULT 'BR',
    tax_regime VARCHAR(80) NOT NULL,
    jurisdiction_scope JSONB NOT NULL,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES identity.users(id),
    CHECK (effective_to IS NULL OR effective_to > effective_from),
    CHECK (status <> 'approved' OR (approved_at IS NOT NULL AND approved_by IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS erp.fiscal_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fiscal_profile_id UUID NOT NULL REFERENCES erp.fiscal_profiles(id),
    priority INTEGER NOT NULL DEFAULT 100 CHECK (priority >= 0),
    country_code CHAR(2) NOT NULL DEFAULT 'BR',
    state_code CHAR(2),
    city_code VARCHAR(12),
    operation_nature VARCHAR(80) NOT NULL,
    customer_type VARCHAR(40),
    taxpayer_status VARCHAR(40),
    destination_type VARCHAR(40),
    channel VARCHAR(40),
    product_type VARCHAR(60),
    purpose VARCHAR(60),
    tax_benefit VARCHAR(120),
    substitution BOOLEAN NOT NULL DEFAULT FALSE,
    single_phase BOOLEAN NOT NULL DEFAULT FALSE,
    withholding BOOLEAN NOT NULL DEFAULT FALSE,
    exemption BOOLEAN NOT NULL DEFAULT FALSE,
    immunity BOOLEAN NOT NULL DEFAULT FALSE,
    deferral BOOLEAN NOT NULL DEFAULT FALSE,
    base_reduction NUMERIC(9, 6) NOT NULL DEFAULT 0 CHECK (base_reduction BETWEEN 0 AND 1),
    rate NUMERIC(12, 8) NOT NULL CHECK (rate >= 0),
    base_formula VARCHAR(500) NOT NULL,
    credit_rule VARCHAR(500),
    rounding_mode VARCHAR(24) NOT NULL DEFAULT 'half_up',
    legal_basis TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES identity.users(id),
    CHECK (effective_to IS NULL OR effective_to > effective_from),
    CHECK (rounding_mode IN ('half_up', 'half_even', 'floor', 'ceiling')),
    CHECK (status <> 'approved' OR (approved_at IS NOT NULL AND approved_by IS NOT NULL))
);

CREATE INDEX IF NOT EXISTS idx_erp_fiscal_rules_resolution
    ON erp.fiscal_rules (fiscal_profile_id, status, priority, effective_from DESC);

CREATE TABLE IF NOT EXISTS erp.product_tax_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    ncm VARCHAR(10),
    cest VARCHAR(12),
    origin_code VARCHAR(4),
    cst VARCHAR(4),
    csosn VARCHAR(4),
    service_code VARCHAR(20),
    cnae VARCHAR(12),
    anp_code VARCHAR(20),
    gtin VARCHAR(18),
    tax_unit_id UUID REFERENCES stock.measurement_units(id),
    tax_quantity_rule VARCHAR(500),
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    CHECK (effective_to IS NULL OR effective_to > effective_from),
    CHECK (ncm IS NOT NULL OR service_code IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS erp.product_fiscal_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    company_id UUID NOT NULL REFERENCES business.companies(id),
    branch_id UUID REFERENCES business.branches(id),
    product_id UUID NOT NULL REFERENCES marketplace.products(id),
    variant_id UUID,
    fiscal_profile_id UUID NOT NULL REFERENCES erp.fiscal_profiles(id),
    classification_id UUID NOT NULL REFERENCES erp.product_tax_classifications(id),
    exception_rule_id UUID REFERENCES erp.fiscal_rules(id),
    effective_from TIMESTAMPTZ NOT NULL,
    effective_to TIMESTAMPTZ,
    status VARCHAR(40) NOT NULL DEFAULT 'draft',
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES identity.users(id),
    CHECK (effective_to IS NULL OR effective_to > effective_from),
    CHECK (status <> 'approved' OR (approved_at IS NOT NULL AND approved_by IS NOT NULL))
);

CREATE INDEX IF NOT EXISTS idx_erp_fiscal_assignment_lookup
    ON erp.product_fiscal_assignments (tenant_id, company_id, product_id, effective_from DESC);

CREATE TABLE IF NOT EXISTS erp.tax_calculation_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    document_id UUID NOT NULL REFERENCES erp.fiscal_documents(id),
    item_id UUID REFERENCES erp.invoice_items(id),
    rule_id UUID NOT NULL REFERENCES erp.fiscal_rules(id),
    classification_id UUID NOT NULL REFERENCES erp.product_tax_classifications(id),
    tax_type VARCHAR(32) NOT NULL,
    tax_base NUMERIC(30, 12) NOT NULL CHECK (tax_base >= 0),
    rate NUMERIC(12, 8) NOT NULL CHECK (rate >= 0),
    tax_amount NUMERIC(30, 12) NOT NULL CHECK (tax_amount >= 0),
    currency_code CHAR(3) NOT NULL DEFAULT 'BRL',
    precision SMALLINT NOT NULL CHECK (precision BETWEEN 0 AND 12),
    rounding_mode VARCHAR(24) NOT NULL,
    legal_basis TEXT NOT NULL,
    calculated_at TIMESTAMPTZ NOT NULL,
    calculation_version VARCHAR(40) NOT NULL,
    input_hash VARCHAR(128) NOT NULL,
    created_by UUID NOT NULL REFERENCES identity.users(id),
    CHECK (rounding_mode IN ('half_up', 'half_even', 'floor', 'ceiling')),
    UNIQUE (tenant_id, document_id, item_id, tax_type, calculation_version)
);

COMMIT;
