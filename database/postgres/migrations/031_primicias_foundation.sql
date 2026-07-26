-- =============================================================================
-- Migration 031: Fundação das Primícias Selecionadas All in One + Valley
-- Recursos 1-5 e 7-24 (Recurso 6 excluído)
-- Branch: feature/primicias-selecionadas-v1
-- Data: 2026-07-26
-- =============================================================================

BEGIN;

-- ===========================================================================
-- FUNDAÇÃO TRANSVERSAL: Feature Flags e Entitlements
-- ===========================================================================

CREATE TABLE IF NOT EXISTS shared.feature_flag_activations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    flag            TEXT        NOT NULL,
    scope           TEXT        NOT NULL DEFAULT 'global', -- global | tenant | user
    scope_id        TEXT,                                  -- tenant_id ou user_id
    activated_by    UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    activated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    deactivated_at  TIMESTAMPTZ,
    deactivated_by  UUID,
    active          BOOLEAN     NOT NULL DEFAULT true,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_ffa_flag_active ON shared.feature_flag_activations (flag, active);
CREATE INDEX IF NOT EXISTS ix_ffa_scope ON shared.feature_flag_activations (scope, scope_id, active);

CREATE TABLE IF NOT EXISTS shared.entitlements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL,
    tenant_id       UUID,
    flag            TEXT        NOT NULL,
    plan            TEXT        NOT NULL DEFAULT 'standard',
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_until     TIMESTAMPTZ,
    limit_units     INTEGER,
    consumed_units  INTEGER     NOT NULL DEFAULT 0,
    promotional     BOOLEAN     NOT NULL DEFAULT false,
    revoked         BOOLEAN     NOT NULL DEFAULT false,
    revoked_at      TIMESTAMPTZ,
    revoked_by      UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_entitlements_user_flag
    ON shared.entitlements (user_id, flag, plan)
    WHERE NOT revoked;
CREATE INDEX IF NOT EXISTS ix_entitlements_tenant_flag ON shared.entitlements (tenant_id, flag);

CREATE TABLE IF NOT EXISTS shared.premium_usage_records (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    entitlement_id  UUID        REFERENCES shared.entitlements(id),
    user_id         UUID        NOT NULL,
    tenant_id       UUID,
    flag            TEXT        NOT NULL,
    action          TEXT        NOT NULL,
    units_consumed  INTEGER     NOT NULL DEFAULT 1,
    correlation_id  UUID,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_pur_user_flag ON shared.premium_usage_records (user_id, flag);
CREATE INDEX IF NOT EXISTS ix_pur_occurred ON shared.premium_usage_records (occurred_at);

-- ===========================================================================
-- RECURSO 1: Identity – Cofre de Provas Mínimas
-- ===========================================================================

CREATE TABLE IF NOT EXISTS identity.proof_definitions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT        NOT NULL,
    attribute       TEXT        NOT NULL,  -- e.g. "age_over_18", "cpf_valid"
    issuer_id       UUID        NOT NULL,
    schema_version  INTEGER     NOT NULL DEFAULT 1,
    valid_days      INTEGER     NOT NULL DEFAULT 365,
    scope           TEXT        NOT NULL DEFAULT 'basic',
    description     TEXT,
    active          BOOLEAN     NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS identity.issued_credentials (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL REFERENCES identity.users(id),
    definition_id   UUID        NOT NULL REFERENCES identity.proof_definitions(id),
    issuer_id       UUID        NOT NULL,
    attribute_hash  TEXT        NOT NULL,  -- hash do atributo, nunca o dado cru
    issued_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    revoked         BOOLEAN     NOT NULL DEFAULT false,
    revoked_at      TIMESTAMPTZ,
    revoked_reason  TEXT,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_ic_user ON identity.issued_credentials (user_id, revoked);

CREATE TABLE IF NOT EXISTS identity.proof_requests (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id    UUID        NOT NULL,
    definition_id   UUID        NOT NULL REFERENCES identity.proof_definitions(id),
    purpose         TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'pending',
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS identity.proof_presentations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL REFERENCES identity.issued_credentials(id),
    request_id      UUID        REFERENCES identity.proof_requests(id),
    presented_to    UUID        NOT NULL,
    attributes_revealed JSONB   NOT NULL DEFAULT '[]',  -- somente atributos autorizados
    consented_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS identity.proof_revocations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL REFERENCES identity.issued_credentials(id),
    revoked_by      UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    revoked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS identity.proof_access_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL,
    action          TEXT        NOT NULL,  -- presented | requested | revoked | denied
    actor_id        UUID,
    requester_id    UUID,
    purpose         TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_pal_credential ON identity.proof_access_logs (credential_id, occurred_at);

-- ===========================================================================
-- RECURSO 2: Business – Consórcio Relâmpago Empresarial
-- ===========================================================================

CREATE TABLE IF NOT EXISTS business.business_opportunities (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT        NOT NULL,
    description     TEXT,
    owner_id        UUID        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    deadline        TIMESTAMPTZ,
    min_members     INTEGER     NOT NULL DEFAULT 2,
    max_members     INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS business.temporary_consortia (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id  UUID        NOT NULL REFERENCES business.business_opportunities(id),
    name            TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'forming',
    activated_at    TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    closed_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS business.consortium_members (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    consortium_id   UUID        NOT NULL REFERENCES business.temporary_consortia(id),
    company_id      UUID        NOT NULL,
    role            TEXT        NOT NULL DEFAULT 'member',
    invited_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    accepted_at     TIMESTAMPTZ,
    status          TEXT        NOT NULL DEFAULT 'invited',
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_cm_consortium_company
    ON business.consortium_members (consortium_id, company_id);

CREATE TABLE IF NOT EXISTS business.responsibility_matrix (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    consortium_id   UUID        NOT NULL REFERENCES business.temporary_consortia(id),
    member_id       UUID        NOT NULL REFERENCES business.consortium_members(id),
    area            TEXT        NOT NULL,
    description     TEXT,
    accepted_at     TIMESTAMPTZ,
    version         INTEGER     NOT NULL DEFAULT 1,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS business.consortium_agreements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    consortium_id   UUID        NOT NULL REFERENCES business.temporary_consortia(id),
    document_hash   TEXT        NOT NULL,
    signed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    signed_by       UUID        NOT NULL,
    version         INTEGER     NOT NULL DEFAULT 1,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS business.consortium_revenue_splits (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    consortium_id   UUID        NOT NULL REFERENCES business.temporary_consortia(id),
    member_id       UUID        NOT NULL REFERENCES business.consortium_members(id),
    percentage      NUMERIC(5,2) NOT NULL CHECK (percentage > 0 AND percentage <= 100),
    approved_at     TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS business.consortium_closures (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    consortium_id   UUID        NOT NULL REFERENCES business.temporary_consortia(id),
    closed_by       UUID        NOT NULL,
    reason          TEXT,
    closed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    audit_summary   JSONB       NOT NULL DEFAULT '{}'
);

-- ===========================================================================
-- RECURSO 3: Permissions – Procuração Operacional Expirável
-- ===========================================================================

CREATE TABLE IF NOT EXISTS permissions.delegations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    grantor_id      UUID        NOT NULL,
    grantee_id      UUID        NOT NULL,
    purpose         TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at    TIMESTAMPTZ,
    expired_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_del_grantee ON permissions.delegations (grantee_id, status);

CREATE TABLE IF NOT EXISTS permissions.delegation_constraints (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    delegation_id   UUID        NOT NULL REFERENCES permissions.delegations(id),
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_until     TIMESTAMPTZ,
    max_amount      NUMERIC(18,2),
    allowed_actions JSONB       NOT NULL DEFAULT '[]',
    allowed_entities JSONB      NOT NULL DEFAULT '[]',
    allowed_branches JSONB      NOT NULL DEFAULT '[]',
    allowed_locations JSONB     NOT NULL DEFAULT '[]',
    allowed_hours   JSONB       NOT NULL DEFAULT '{}',  -- {"start":"08:00","end":"18:00"}
    single_use      BOOLEAN     NOT NULL DEFAULT false,
    requires_second_approval BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS permissions.delegation_grants (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    delegation_id   UUID        NOT NULL REFERENCES permissions.delegations(id),
    module          TEXT        NOT NULL,
    resource_type   TEXT        NOT NULL,
    permission      TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS permissions.delegation_usages (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    delegation_id   UUID        NOT NULL REFERENCES permissions.delegations(id),
    actor_id        UUID        NOT NULL,
    module          TEXT        NOT NULL,
    action          TEXT        NOT NULL,
    amount          NUMERIC(18,2),
    correlation_id  UUID,
    used_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    result          TEXT        NOT NULL DEFAULT 'allowed',
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_du_delegation ON permissions.delegation_usages (delegation_id, used_at);

CREATE TABLE IF NOT EXISTS permissions.delegation_revocations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    delegation_id   UUID        NOT NULL REFERENCES permissions.delegations(id),
    revoked_by      UUID        NOT NULL,
    reason          TEXT,
    revoked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===========================================================================
-- RECURSO 4: Finance – Dinheiro com Destino
-- ===========================================================================

CREATE TABLE IF NOT EXISTS finance.allocation_rules (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT        NOT NULL,
    tenant_id       UUID        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    description     TEXT,
    created_by      UUID        NOT NULL,
    activated_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS finance.allocation_rule_conditions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id         UUID        NOT NULL REFERENCES finance.allocation_rules(id),
    condition_type  TEXT        NOT NULL,  -- origin | customer | contract | category
    condition_value TEXT        NOT NULL,
    account_code    TEXT        NOT NULL,
    percentage      NUMERIC(5,2) NOT NULL CHECK (percentage > 0),
    priority        INTEGER     NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS finance.earmarked_accounts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    rule_id         UUID        NOT NULL REFERENCES finance.allocation_rules(id),
    account_code    TEXT        NOT NULL,
    purpose         TEXT        NOT NULL,
    balance         NUMERIC(18,2) NOT NULL DEFAULT 0,
    currency        TEXT        NOT NULL DEFAULT 'BRL',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS finance.allocation_executions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id         UUID        NOT NULL REFERENCES finance.allocation_rules(id),
    income_ref      TEXT        NOT NULL,  -- referência à transação de entrada
    total_amount    NUMERIC(18,2) NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'pending',
    executed_at     TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS finance.allocation_execution_items (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id    UUID        NOT NULL REFERENCES finance.allocation_executions(id),
    account_code    TEXT        NOT NULL,
    amount          NUMERIC(18,2) NOT NULL,
    ledger_entry_id TEXT,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS finance.allocation_reversals (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id    UUID        NOT NULL REFERENCES finance.allocation_executions(id),
    reversed_by     UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    reversed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    ledger_entry_id TEXT,
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- RECURSO 5: Marketplace – Compra em Coalizão Local
-- ===========================================================================

CREATE TABLE IF NOT EXISTS marketplace.buying_coalitions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT        NOT NULL,
    description     TEXT,
    organizer_id    UUID        NOT NULL,
    region          TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'open',
    min_quantity    INTEGER     NOT NULL DEFAULT 2,
    target_price    NUMERIC(18,2),
    deadline        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS marketplace.coalition_product_requests (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    coalition_id    UUID        NOT NULL REFERENCES marketplace.buying_coalitions(id),
    product_id      TEXT        NOT NULL,
    quantity        INTEGER     NOT NULL,
    specifications  JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS marketplace.coalition_members (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    coalition_id    UUID        NOT NULL REFERENCES marketplace.buying_coalitions(id),
    user_id         UUID        NOT NULL,
    quantity        INTEGER     NOT NULL DEFAULT 1,
    joined_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT        NOT NULL DEFAULT 'active',
    location_approx TEXT,  -- bairro/cidade, NUNCA coordenada exata antes do aceite
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_cm_coalition_user
    ON marketplace.coalition_members (coalition_id, user_id);

CREATE TABLE IF NOT EXISTS marketplace.coalition_thresholds (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    coalition_id    UUID        NOT NULL REFERENCES marketplace.buying_coalitions(id),
    threshold_type  TEXT        NOT NULL,
    value           NUMERIC(18,2) NOT NULL,
    met             BOOLEAN     NOT NULL DEFAULT false,
    met_at          TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS marketplace.supplier_bids (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    coalition_id    UUID        NOT NULL REFERENCES marketplace.buying_coalitions(id),
    supplier_id     UUID        NOT NULL,
    unit_price      NUMERIC(18,2) NOT NULL,
    valid_until     TIMESTAMPTZ,
    status          TEXT        NOT NULL DEFAULT 'pending',
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    accepted_at     TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS marketplace.coalition_orders (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    coalition_id    UUID        NOT NULL REFERENCES marketplace.buying_coalitions(id),
    supplier_bid_id UUID        REFERENCES marketplace.supplier_bids(id),
    status          TEXT        NOT NULL DEFAULT 'pending',
    confirmed_at    TIMESTAMPTZ,
    total_amount    NUMERIC(18,2),
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS marketplace.coalition_delivery_plans (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID        NOT NULL REFERENCES marketplace.coalition_orders(id),
    delivery_date   DATE,
    location_type   TEXT        NOT NULL DEFAULT 'collection_point',
    address_summary TEXT,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS marketplace.coalition_refunds (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID        NOT NULL REFERENCES marketplace.coalition_orders(id),
    member_id       UUID        NOT NULL REFERENCES marketplace.coalition_members(id),
    reason          TEXT        NOT NULL,
    amount          NUMERIC(18,2) NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'pending',
    processed_at    TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- RECURSO 7: Delivery – Entrega de Trajeto Aproveitado
-- ===========================================================================

CREATE TABLE IF NOT EXISTS delivery.planned_trips (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    carrier_user_id UUID        NOT NULL,
    vehicle_id      UUID,
    origin_approx   TEXT        NOT NULL,
    destination_approx TEXT     NOT NULL,
    departure_at    TIMESTAMPTZ NOT NULL,
    arrival_at      TIMESTAMPTZ,
    status          TEXT        NOT NULL DEFAULT 'available',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS delivery.route_capacity_offers (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id         UUID        NOT NULL REFERENCES delivery.planned_trips(id),
    max_weight_kg   NUMERIC(8,2),
    max_volume_cm3  NUMERIC(12,2),
    prohibited_items JSONB      NOT NULL DEFAULT '[]',
    status          TEXT        NOT NULL DEFAULT 'published',
    published_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS delivery.parcel_requirements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id       UUID        NOT NULL,
    description     TEXT        NOT NULL,
    weight_kg       NUMERIC(8,2) NOT NULL,
    volume_cm3      NUMERIC(12,2),
    category        TEXT        NOT NULL DEFAULT 'general',
    pickup_region   TEXT        NOT NULL,
    dropoff_region  TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'searching',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS delivery.route_parcel_matches (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id        UUID        NOT NULL REFERENCES delivery.route_capacity_offers(id),
    parcel_id       UUID        NOT NULL REFERENCES delivery.parcel_requirements(id),
    status          TEXT        NOT NULL DEFAULT 'proposed',
    matched_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    accepted_at     TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS delivery.handoff_checkpoints (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id        UUID        NOT NULL REFERENCES delivery.route_parcel_matches(id),
    checkpoint_type TEXT        NOT NULL,  -- pickup | delivery
    evidence_url    TEXT,
    evidence_hash   TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS delivery.delivery_capacity_incidents (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id        UUID        NOT NULL REFERENCES delivery.route_parcel_matches(id),
    incident_type   TEXT        NOT NULL,
    description     TEXT,
    reported_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at     TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

-- ===========================================================================
-- RECURSO 8: Riders – Passaporte de Evidências Operacionais
-- ===========================================================================

CREATE TABLE IF NOT EXISTS riders.competency_definitions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT        NOT NULL UNIQUE,
    description     TEXT,
    category        TEXT        NOT NULL DEFAULT 'operational',
    active          BOOLEAN     NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS riders.rider_evidence_credentials (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id        UUID        NOT NULL,
    competency_id   UUID        NOT NULL REFERENCES riders.competency_definitions(id),
    source_type     TEXT        NOT NULL,  -- platform_activity | external | verified
    source_ref      TEXT,
    period_start    DATE        NOT NULL,
    period_end      DATE,
    issued_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    revoked         BOOLEAN     NOT NULL DEFAULT false,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_rec_rider ON riders.rider_evidence_credentials (rider_id, revoked);

CREATE TABLE IF NOT EXISTS riders.evidence_sources (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL REFERENCES riders.rider_evidence_credentials(id),
    source_name     TEXT        NOT NULL,
    source_url      TEXT,
    verified        BOOLEAN     NOT NULL DEFAULT false,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS riders.evidence_presentations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL REFERENCES riders.rider_evidence_credentials(id),
    presented_to    UUID        NOT NULL,
    competencies_shared JSONB   NOT NULL DEFAULT '[]',
    consented_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS riders.evidence_disputes (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL REFERENCES riders.rider_evidence_credentials(id),
    disputed_by     UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'open',
    resolved_at     TIMESTAMPTZ,
    resolution      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS riders.evidence_revocations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    credential_id   UUID        NOT NULL REFERENCES riders.rider_evidence_credentials(id),
    revoked_by      UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    revoked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===========================================================================
-- RECURSO 9: Services – Contrato por Resultado Componível
-- ===========================================================================

CREATE TABLE IF NOT EXISTS services.outcome_contracts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID        NOT NULL,
    title           TEXT        NOT NULL,
    description     TEXT,
    status          TEXT        NOT NULL DEFAULT 'draft',
    escrow_amount   NUMERIC(18,2),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at    TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS services.outcome_milestones (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID        NOT NULL REFERENCES services.outcome_contracts(id),
    title           TEXT        NOT NULL,
    description     TEXT,
    acceptance_criteria TEXT    NOT NULL,
    sequence        INTEGER     NOT NULL DEFAULT 1,
    payment_amount  NUMERIC(18,2),
    status          TEXT        NOT NULL DEFAULT 'pending',
    submitted_at    TIMESTAMPTZ,
    accepted_at     TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS services.provider_roles (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID        NOT NULL REFERENCES services.outcome_contracts(id),
    role_name       TEXT        NOT NULL,
    description     TEXT,
    milestone_scope JSONB       NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS services.provider_assignments (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id         UUID        NOT NULL REFERENCES services.provider_roles(id),
    provider_id     UUID        NOT NULL,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT        NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS services.milestone_evidence (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id    UUID        NOT NULL REFERENCES services.outcome_milestones(id),
    provider_id     UUID        NOT NULL,
    evidence_type   TEXT        NOT NULL,
    evidence_url    TEXT,
    evidence_hash   TEXT,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS services.milestone_acceptances (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id    UUID        NOT NULL REFERENCES services.outcome_milestones(id),
    accepted_by     UUID        NOT NULL,
    accepted_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes           TEXT,
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS services.outcome_disputes (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id    UUID        NOT NULL REFERENCES services.outcome_milestones(id),
    disputed_by     UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'open',
    resolution      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at     TIMESTAMPTZ
);

-- ===========================================================================
-- RECURSO 10: Mobility – Rota de Intenções Premium
-- ===========================================================================

CREATE TABLE IF NOT EXISTS mobility.mobility_intention_plans (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID        NOT NULL,
    title           TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    premium         BOOLEAN     NOT NULL DEFAULT false,
    entitlement_id  UUID,
    quoted_amount   NUMERIC(18,2),
    currency        TEXT        NOT NULL DEFAULT 'BRL',
    quote_valid_until TIMESTAMPTZ,
    charge_ref      TEXT,
    confirmed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_mip_user ON mobility.mobility_intention_plans (user_id, status);

CREATE TABLE IF NOT EXISTS mobility.mobility_intentions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID        NOT NULL REFERENCES mobility.mobility_intention_plans(id),
    intention_type  TEXT        NOT NULL,  -- commitment | pickup | dropoff | waypoint
    title           TEXT        NOT NULL,
    address_approx  TEXT,
    scheduled_at    TIMESTAMPTZ,
    sequence        INTEGER     NOT NULL DEFAULT 1,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS mobility.journey_constraints (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID        NOT NULL REFERENCES mobility.mobility_intention_plans(id),
    constraint_type TEXT        NOT NULL,
    value           JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS mobility.journey_plan_versions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID        NOT NULL REFERENCES mobility.mobility_intention_plans(id),
    version         INTEGER     NOT NULL DEFAULT 1,
    snapshot        JSONB       NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mobility.journey_steps (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID        NOT NULL REFERENCES mobility.mobility_intention_plans(id),
    step_type       TEXT        NOT NULL,
    transport_mode  TEXT,
    from_intention  UUID        REFERENCES mobility.mobility_intentions(id),
    to_intention    UUID        REFERENCES mobility.mobility_intentions(id),
    estimated_duration_min INTEGER,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS mobility.premium_price_quotes (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id         UUID        NOT NULL REFERENCES mobility.mobility_intention_plans(id),
    pricing_config_id TEXT      NOT NULL,
    base_amount     NUMERIC(18,2) NOT NULL,
    tax_amount      NUMERIC(18,2) NOT NULL DEFAULT 0,
    total_amount    NUMERIC(18,2) NOT NULL,
    currency        TEXT        NOT NULL DEFAULT 'BRL',
    valid_until     TIMESTAMPTZ NOT NULL,
    quoted_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Nunca expor custo interno, margem ou lucro
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

-- ===========================================================================
-- RECURSO 11: Jobs – Janela de Trabalho Reversa
-- ===========================================================================

CREATE TABLE IF NOT EXISTS jobs.availability_windows (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    worker_id       UUID        NOT NULL,
    available_from  TIMESTAMPTZ NOT NULL,
    available_until TIMESTAMPTZ NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    published_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key TEXT        UNIQUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_aw_worker ON jobs.availability_windows (worker_id, status);

CREATE TABLE IF NOT EXISTS jobs.work_preferences (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    window_id       UUID        NOT NULL REFERENCES jobs.availability_windows(id),
    preference_type TEXT        NOT NULL,  -- location | schedule | remote | hybrid
    value           TEXT        NOT NULL,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS jobs.availability_skills (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    window_id       UUID        NOT NULL REFERENCES jobs.availability_windows(id),
    skill           TEXT        NOT NULL,
    level           TEXT        NOT NULL DEFAULT 'intermediate'
);

CREATE TABLE IF NOT EXISTS jobs.employer_work_offers (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    window_id       UUID        NOT NULL REFERENCES jobs.availability_windows(id),
    employer_id     UUID        NOT NULL,
    title           TEXT        NOT NULL,
    description     TEXT,
    min_compensation NUMERIC(18,2),
    compensation_type TEXT      NOT NULL DEFAULT 'hourly',
    status          TEXT        NOT NULL DEFAULT 'sent',
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS jobs.offer_responses (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id        UUID        NOT NULL REFERENCES jobs.employer_work_offers(id),
    worker_id       UUID        NOT NULL,
    response        TEXT        NOT NULL,  -- accepted | rejected
    notes           TEXT,
    responded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS jobs.availability_privacy_settings (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    window_id       UUID        NOT NULL REFERENCES jobs.availability_windows(id),
    location_precision TEXT     NOT NULL DEFAULT 'neighborhood',  -- neighborhood | city | region
    show_to_verified_only BOOLEAN NOT NULL DEFAULT true,
    allow_direct_contact BOOLEAN NOT NULL DEFAULT false
);

-- ===========================================================================
-- RECURSO 12: ERP – Fechamento Contínuo por Exceção
-- ===========================================================================

CREATE TABLE IF NOT EXISTS erp.close_control_rules (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    name            TEXT        NOT NULL,
    rule_type       TEXT        NOT NULL,
    criteria        JSONB       NOT NULL DEFAULT '{}',
    active          BOOLEAN     NOT NULL DEFAULT true,
    created_by      UUID        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS erp.transaction_completeness_scores (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    period          TEXT        NOT NULL,  -- YYYY-MM
    transaction_ref TEXT        NOT NULL,
    score           NUMERIC(5,4) NOT NULL CHECK (score >= 0 AND score <= 1),
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    flags           JSONB       NOT NULL DEFAULT '[]'
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_tcs_period_ref
    ON erp.transaction_completeness_scores (tenant_id, period, transaction_ref);

CREATE TABLE IF NOT EXISTS erp.close_exceptions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    period          TEXT        NOT NULL,
    exception_type  TEXT        NOT NULL,
    description     TEXT        NOT NULL,
    evidence        JSONB       NOT NULL DEFAULT '{}',
    status          TEXT        NOT NULL DEFAULT 'open',
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_ce_period ON erp.close_exceptions (tenant_id, period, status);

CREATE TABLE IF NOT EXISTS erp.close_exception_assignments (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    exception_id    UUID        NOT NULL REFERENCES erp.close_exceptions(id),
    assignee_id     UUID        NOT NULL,
    due_date        DATE        NOT NULL,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT
);

CREATE TABLE IF NOT EXISTS erp.close_period_snapshots (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    period          TEXT        NOT NULL,
    snapshot        JSONB       NOT NULL DEFAULT '{}',
    ready           BOOLEAN     NOT NULL DEFAULT false,
    closed          BOOLEAN     NOT NULL DEFAULT false,
    taken_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_cps_period
    ON erp.close_period_snapshots (tenant_id, period);

CREATE TABLE IF NOT EXISTS erp.close_approvals (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    period          TEXT        NOT NULL,
    tenant_id       UUID        NOT NULL,
    approved_by     UUID        NOT NULL,
    approved_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes           TEXT,
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- RECURSO 13: WMS – Mapa de Certeza do Estoque
-- ===========================================================================

CREATE TABLE IF NOT EXISTS wms.inventory_confidence_scores (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    location_id     TEXT        NOT NULL,
    sku             TEXT        NOT NULL,
    score           NUMERIC(5,4) NOT NULL DEFAULT 1 CHECK (score >= 0 AND score <= 1),
    last_event_type TEXT,
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_ics_location_sku
    ON wms.inventory_confidence_scores (tenant_id, location_id, sku);

CREATE TABLE IF NOT EXISTS wms.inventory_confidence_events (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    score_id        UUID        NOT NULL REFERENCES wms.inventory_confidence_scores(id),
    event_type      TEXT        NOT NULL,  -- movement | adjustment | delay | count_confirmed
    delta           NUMERIC(6,4) NOT NULL,  -- quanto alterou o score
    description     TEXT,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS wms.targeted_count_requests (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    score_id        UUID        NOT NULL REFERENCES wms.inventory_confidence_scores(id),
    location_id     TEXT        NOT NULL,
    sku             TEXT        NOT NULL,
    reason          TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'requested',
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS wms.targeted_count_results (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id      UUID        NOT NULL REFERENCES wms.targeted_count_requests(id),
    counted_by      UUID        NOT NULL,
    counted_quantity NUMERIC(18,4) NOT NULL,
    system_quantity  NUMERIC(18,4),
    discrepancy     NUMERIC(18,4),
    counted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    evidence        JSONB       NOT NULL DEFAULT '{}',
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS wms.confidence_rule_definitions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    warehouse_id    TEXT,
    category        TEXT,
    event_type      TEXT        NOT NULL,
    impact          NUMERIC(5,4) NOT NULL,  -- negativo reduz, positivo aumenta
    description     TEXT,
    active          BOOLEAN     NOT NULL DEFAULT true
);

-- ===========================================================================
-- RECURSO 14: TMS – Bolsa Cega de Capacidade Logística
-- ===========================================================================

CREATE TABLE IF NOT EXISTS tms.anonymous_capacity_offers (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID        NOT NULL,
    anonymous_ref   TEXT        NOT NULL UNIQUE,  -- alias anônimo
    origin_region   TEXT        NOT NULL,
    destination_region TEXT     NOT NULL,
    available_from  TIMESTAMPTZ NOT NULL,
    available_until TIMESTAMPTZ NOT NULL,
    capacity_kg     NUMERIC(12,2),
    capacity_m3     NUMERIC(12,2),
    transport_types JSONB       NOT NULL DEFAULT '[]',
    status          TEXT        NOT NULL DEFAULT 'published',
    published_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tms.anonymous_freight_demands (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID        NOT NULL,
    anonymous_ref   TEXT        NOT NULL UNIQUE,
    origin_region   TEXT        NOT NULL,
    destination_region TEXT     NOT NULL,
    needed_by       TIMESTAMPTZ NOT NULL,
    weight_kg       NUMERIC(12,2),
    volume_m3       NUMERIC(12,2),
    cargo_types     JSONB       NOT NULL DEFAULT '[]',
    status          TEXT        NOT NULL DEFAULT 'published',
    published_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tms.capacity_match_candidates (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    offer_id        UUID        NOT NULL REFERENCES tms.anonymous_capacity_offers(id),
    demand_id       UUID        NOT NULL REFERENCES tms.anonymous_freight_demands(id),
    compatibility_score NUMERIC(5,4),
    proposed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT        NOT NULL DEFAULT 'proposed',
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS tms.mutual_disclosure_consents (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id        UUID        NOT NULL REFERENCES tms.capacity_match_candidates(id),
    company_id      UUID        NOT NULL,
    accepted        BOOLEAN     NOT NULL DEFAULT false,
    accepted_at     TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_mdc_match_company
    ON tms.mutual_disclosure_consents (match_id, company_id);

CREATE TABLE IF NOT EXISTS tms.capacity_exchange_agreements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id        UUID        NOT NULL REFERENCES tms.capacity_match_candidates(id),
    contract_ref    TEXT,
    status          TEXT        NOT NULL DEFAULT 'active',
    signed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tms.capacity_exchange_audits (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    agreement_id    UUID        NOT NULL REFERENCES tms.capacity_exchange_agreements(id),
    event_type      TEXT        NOT NULL,
    actor_id        UUID,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    details         JSONB       NOT NULL DEFAULT '{}'
);

-- ===========================================================================
-- RECURSO 15: CRM – Livro de Promessas ao Cliente
-- ===========================================================================

CREATE TABLE IF NOT EXISTS crm.customer_promises (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    customer_id     UUID        NOT NULL,
    title           TEXT        NOT NULL,
    description     TEXT,
    source_type     TEXT        NOT NULL DEFAULT 'manual',  -- manual | ai_suggested | extracted
    status          TEXT        NOT NULL DEFAULT 'open',
    confirmed       BOOLEAN     NOT NULL DEFAULT false,
    confirmed_at    TIMESTAMPTZ,
    fulfilled_at    TIMESTAMPTZ,
    breached_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_cp_tenant_customer ON crm.customer_promises (tenant_id, customer_id, status);

CREATE TABLE IF NOT EXISTS crm.promise_sources (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    promise_id      UUID        NOT NULL REFERENCES crm.customer_promises(id),
    source_ref      TEXT        NOT NULL,  -- ticket_id, call_id, etc.
    source_type     TEXT        NOT NULL,
    extracted_by    TEXT,  -- 'human' | 'ai'
    requires_review BOOLEAN     NOT NULL DEFAULT false,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS crm.promise_owners (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    promise_id      UUID        NOT NULL REFERENCES crm.customer_promises(id),
    owner_id        UUID        NOT NULL,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    active          BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS crm.promise_deadlines (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    promise_id      UUID        NOT NULL REFERENCES crm.customer_promises(id),
    due_date        TIMESTAMPTZ NOT NULL,
    notified_at     TIMESTAMPTZ,
    version         INTEGER     NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS crm.promise_evidence (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    promise_id      UUID        NOT NULL REFERENCES crm.customer_promises(id),
    evidence_type   TEXT        NOT NULL,
    evidence_ref    TEXT,
    submitted_by    UUID        NOT NULL,
    submitted_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crm.promise_confirmations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    promise_id      UUID        NOT NULL REFERENCES crm.customer_promises(id),
    confirmed_by    UUID        NOT NULL,
    confirmed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    channel         TEXT,
    notes           TEXT,
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS crm.promise_breaches (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    promise_id      UUID        NOT NULL REFERENCES crm.customer_promises(id),
    breached_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason          TEXT,
    resolution      TEXT,
    resolved_at     TIMESTAMPTZ
);

-- ===========================================================================
-- RECURSO 16: BPM – Laboratório de Processo Enxuto
-- ===========================================================================

CREATE TABLE IF NOT EXISTS bpm.process_scenarios (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    source_process_id TEXT      NOT NULL,
    name            TEXT        NOT NULL,
    description     TEXT,
    assumptions     JSONB       NOT NULL DEFAULT '[]',
    status          TEXT        NOT NULL DEFAULT 'draft',
    created_by      UUID        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS bpm.process_scenario_steps (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id     UUID        NOT NULL REFERENCES bpm.process_scenarios(id),
    step_name       TEXT        NOT NULL,
    step_type       TEXT        NOT NULL,
    included        BOOLEAN     NOT NULL DEFAULT true,
    modified        BOOLEAN     NOT NULL DEFAULT false,
    original_ref    TEXT,
    sequence        INTEGER     NOT NULL DEFAULT 1,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS bpm.simulation_runs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id     UUID        NOT NULL REFERENCES bpm.process_scenarios(id),
    status          TEXT        NOT NULL DEFAULT 'pending',
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    parameters      JSONB       NOT NULL DEFAULT '{}',
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS bpm.simulation_metrics (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID        NOT NULL REFERENCES bpm.simulation_runs(id),
    metric_name     TEXT        NOT NULL,
    value           NUMERIC(18,4),
    unit            TEXT,
    compared_to_baseline NUMERIC(18,4),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS bpm.simulation_risk_findings (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID        NOT NULL REFERENCES bpm.simulation_runs(id),
    risk_type       TEXT        NOT NULL,
    severity        TEXT        NOT NULL DEFAULT 'medium',
    description     TEXT        NOT NULL,
    affected_control TEXT,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS bpm.process_experiment_approvals (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id     UUID        NOT NULL REFERENCES bpm.process_scenarios(id),
    approved_by     UUID        NOT NULL,
    approved_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    rollback_plan   TEXT        NOT NULL,
    target_group    JSONB       NOT NULL DEFAULT '{}',
    activated_at    TIMESTAMPTZ,
    rolled_back_at  TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- RECURSO 17: Document/GED ECM – Documento Vivo de Obrigações
-- ===========================================================================

CREATE TABLE IF NOT EXISTS document.document_clause_anchors (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     UUID        NOT NULL,
    document_version INTEGER    NOT NULL DEFAULT 1,
    page_number     INTEGER,
    section_ref     TEXT,
    clause_text     TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document.document_obligations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    anchor_id       UUID        NOT NULL REFERENCES document.document_clause_anchors(id),
    document_id     UUID        NOT NULL,
    title           TEXT        NOT NULL,
    description     TEXT,
    obligation_type TEXT        NOT NULL DEFAULT 'compliance',
    status          TEXT        NOT NULL DEFAULT 'pending',
    ai_generated    BOOLEAN     NOT NULL DEFAULT false,
    reviewed        BOOLEAN     NOT NULL DEFAULT false,
    reviewed_by     UUID,
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_do_document ON document.document_obligations (document_id, status);

CREATE TABLE IF NOT EXISTS document.obligation_responsibles (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    obligation_id   UUID        NOT NULL REFERENCES document.document_obligations(id),
    responsible_id  UUID        NOT NULL,
    assigned_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    active          BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS document.obligation_deadlines (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    obligation_id   UUID        NOT NULL REFERENCES document.document_obligations(id),
    due_date        TIMESTAMPTZ NOT NULL,
    notified_at     TIMESTAMPTZ,
    version         INTEGER     NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS document.obligation_impacts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    obligation_id   UUID        NOT NULL REFERENCES document.document_obligations(id),
    new_version_id  UUID,
    impact_type     TEXT        NOT NULL,  -- superseded | amended | voided
    description     TEXT,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document.obligation_reviews (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    obligation_id   UUID        NOT NULL REFERENCES document.document_obligations(id),
    reviewed_by     UUID        NOT NULL,
    decision        TEXT        NOT NULL,
    notes           TEXT,
    reviewed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- RECURSO 18: HR – Escala de Afinidade Justa
-- ===========================================================================

CREATE TABLE IF NOT EXISTS hr.employee_schedule_preferences (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id     UUID        NOT NULL,
    preference_type TEXT        NOT NULL,
    value           JSONB       NOT NULL DEFAULT '{}',
    voluntary       BOOLEAN     NOT NULL DEFAULT true,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS hr.shift_requirements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    shift_date      DATE        NOT NULL,
    shift_start     TIME        NOT NULL,
    shift_end       TIME        NOT NULL,
    required_count  INTEGER     NOT NULL DEFAULT 1,
    required_skills JSONB       NOT NULL DEFAULT '[]',
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS hr.schedule_constraints (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    constraint_type TEXT        NOT NULL,
    description     TEXT        NOT NULL,
    rule_config     JSONB       NOT NULL DEFAULT '{}',
    active          BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS hr.schedule_proposals (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    period_start    DATE        NOT NULL,
    period_end      DATE        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    generated_by    TEXT        NOT NULL DEFAULT 'algorithm',
    approved_by     UUID,
    approved_at     TIMESTAMPTZ,
    published_at    TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS hr.schedule_assignments (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id     UUID        NOT NULL REFERENCES hr.schedule_proposals(id),
    employee_id     UUID        NOT NULL,
    shift_id        UUID        NOT NULL REFERENCES hr.shift_requirements(id),
    rationale       TEXT,
    contested       BOOLEAN     NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS hr.fairness_metrics (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id     UUID        NOT NULL REFERENCES hr.schedule_proposals(id),
    metric_name     TEXT        NOT NULL,
    value           NUMERIC(18,4),
    threshold       NUMERIC(18,4),
    within_threshold BOOLEAN    NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS hr.schedule_contestations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id   UUID        NOT NULL REFERENCES hr.schedule_assignments(id),
    employee_id     UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'open',
    resolved_by     UUID,
    resolution      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at     TIMESTAMPTZ
);

-- ===========================================================================
-- RECURSO 19: Health – Cápsula de Continuidade do Cuidado
-- ===========================================================================

CREATE TABLE IF NOT EXISTS health.continuity_capsules (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID        NOT NULL,
    title           TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'active',
    version         INTEGER     NOT NULL DEFAULT 1,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_cc_patient ON health.continuity_capsules (patient_id, status);

CREATE TABLE IF NOT EXISTS health.continuity_capsule_sections (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    capsule_id      UUID        NOT NULL REFERENCES health.continuity_capsules(id),
    section_type    TEXT        NOT NULL,  -- allergies | medications | conditions | contacts
    content         JSONB       NOT NULL DEFAULT '{}',
    source_type     TEXT        NOT NULL DEFAULT 'self_reported',  -- self_reported | professional
    fhir_resource_type TEXT,
    shareable       BOOLEAN     NOT NULL DEFAULT false,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS health.continuity_capsule_versions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    capsule_id      UUID        NOT NULL REFERENCES health.continuity_capsules(id),
    version         INTEGER     NOT NULL,
    snapshot        JSONB       NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS health.continuity_access_grants (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    capsule_id      UUID        NOT NULL REFERENCES health.continuity_capsules(id),
    grantee_id      UUID        NOT NULL,
    grantee_type    TEXT        NOT NULL DEFAULT 'professional',
    granted_sections JSONB      NOT NULL DEFAULT '[]',
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    valid_until     TIMESTAMPTZ NOT NULL,
    purpose         TEXT        NOT NULL,
    emergency_access BOOLEAN    NOT NULL DEFAULT false,
    emergency_basis TEXT,
    revoked         BOOLEAN     NOT NULL DEFAULT false,
    revoked_at      TIMESTAMPTZ,
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS health.continuity_access_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_id        UUID        NOT NULL REFERENCES health.continuity_access_grants(id),
    accessed_by     UUID        NOT NULL,
    sections_accessed JSONB     NOT NULL DEFAULT '[]',
    accessed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    purpose         TEXT,
    emergency_justification TEXT
);

CREATE TABLE IF NOT EXISTS health.continuity_revocations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    grant_id        UUID        NOT NULL REFERENCES health.continuity_access_grants(id),
    revoked_by      UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    revoked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===========================================================================
-- RECURSO 20: Legal – Radar de Efeito Jurídico em Cadeia
-- ===========================================================================

CREATE TABLE IF NOT EXISTS legal.legal_change_records (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT        NOT NULL,
    change_type     TEXT        NOT NULL,  -- legislation | regulation | contract
    source          TEXT        NOT NULL,
    source_date     DATE        NOT NULL,
    urgency         TEXT        NOT NULL DEFAULT 'normal',
    description     TEXT,
    created_by      UUID        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS legal.legal_change_sources (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    change_id       UUID        NOT NULL REFERENCES legal.legal_change_records(id),
    source_type     TEXT        NOT NULL,
    reference       TEXT        NOT NULL,
    url             TEXT,
    evidence_hash   TEXT
);

CREATE TABLE IF NOT EXISTS legal.legal_impact_links (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    change_id       UUID        NOT NULL REFERENCES legal.legal_change_records(id),
    entity_type     TEXT        NOT NULL,  -- document | process | module | contract
    entity_id       TEXT        NOT NULL,
    impact_level    TEXT        NOT NULL DEFAULT 'possible',  -- possible | probable | confirmed
    ai_suggested    BOOLEAN     NOT NULL DEFAULT false,
    notes           TEXT,
    linked_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS legal.legal_impact_assessments (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    change_id       UUID        NOT NULL REFERENCES legal.legal_change_records(id),
    assessed_by     UUID        NOT NULL,
    summary         TEXT        NOT NULL,
    ai_assisted     BOOLEAN     NOT NULL DEFAULT false,
    reviewed        BOOLEAN     NOT NULL DEFAULT false,
    assessed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS legal.legal_review_decisions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id   UUID        NOT NULL REFERENCES legal.legal_impact_assessments(id),
    reviewer_id     UUID        NOT NULL,
    decision        TEXT        NOT NULL,
    notes           TEXT,
    reviewed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS legal.legal_action_plans (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    change_id       UUID        NOT NULL REFERENCES legal.legal_change_records(id),
    title           TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    approved_by     UUID,
    approved_at     TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

-- ===========================================================================
-- RECURSO 21: Property – Condomínio de Capacidade Compartilhada
-- ===========================================================================

CREATE TABLE IF NOT EXISTS property.shared_property_assets (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    name            TEXT        NOT NULL,
    asset_type      TEXT        NOT NULL,
    description     TEXT,
    status          TEXT        NOT NULL DEFAULT 'pending_approval',
    approved_by     UUID,
    approved_at     TIMESTAMPTZ,
    hazardous       BOOLEAN     NOT NULL DEFAULT false,
    created_by      UUID        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS property.shared_asset_rules (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID        NOT NULL REFERENCES property.shared_property_assets(id),
    rule_type       TEXT        NOT NULL,
    value           JSONB       NOT NULL DEFAULT '{}',
    active          BOOLEAN     NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS property.shared_asset_availability (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID        NOT NULL REFERENCES property.shared_property_assets(id),
    available_from  TIMESTAMPTZ NOT NULL,
    available_until TIMESTAMPTZ NOT NULL,
    reserved        BOOLEAN     NOT NULL DEFAULT false
);

CREATE TABLE IF NOT EXISTS property.shared_asset_reservations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id        UUID        NOT NULL REFERENCES property.shared_property_assets(id),
    reserver_id     UUID        NOT NULL,
    start_at        TIMESTAMPTZ NOT NULL,
    end_at          TIMESTAMPTZ NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    idempotency_key TEXT        UNIQUE
);

CREATE TABLE IF NOT EXISTS property.shared_asset_inspections (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id  UUID        NOT NULL REFERENCES property.shared_asset_reservations(id),
    inspection_type TEXT        NOT NULL,  -- checkout | return
    inspector_id    UUID,
    condition_notes TEXT,
    evidence        JSONB       NOT NULL DEFAULT '[]',
    inspected_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS property.shared_asset_incidents (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id  UUID        NOT NULL REFERENCES property.shared_asset_reservations(id),
    incident_type   TEXT        NOT NULL,
    description     TEXT        NOT NULL,
    reported_by     UUID        NOT NULL,
    resolved        BOOLEAN     NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS property.shared_asset_revenue_allocations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    reservation_id  UUID        NOT NULL REFERENCES property.shared_asset_reservations(id),
    amount          NUMERIC(18,2) NOT NULL,
    destination     TEXT        NOT NULL,
    allocated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    ledger_ref      TEXT,
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- RECURSO 22: BI – Painel de Perguntas Não Feitas
-- ===========================================================================

CREATE TABLE IF NOT EXISTS bi.anomaly_observations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID        NOT NULL,
    metric          TEXT        NOT NULL,
    period          TEXT        NOT NULL,
    observed_value  NUMERIC(18,4),
    expected_range  JSONB       NOT NULL DEFAULT '{}',
    deviation_pct   NUMERIC(8,4),
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_ao_tenant ON bi.anomaly_observations (tenant_id, detected_at);

CREATE TABLE IF NOT EXISTS bi.question_suggestions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    observation_id  UUID        NOT NULL REFERENCES bi.anomaly_observations(id),
    question_text   TEXT        NOT NULL,
    explanation     TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'suggested',
    dismissed       BOOLEAN     NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bi.question_evidence_links (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id     UUID        NOT NULL REFERENCES bi.question_suggestions(id),
    metric          TEXT        NOT NULL,
    period          TEXT        NOT NULL,
    value           NUMERIC(18,4),
    description     TEXT
);

CREATE TABLE IF NOT EXISTS bi.question_confidence_scores (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id     UUID        NOT NULL REFERENCES bi.question_suggestions(id),
    score           NUMERIC(5,4) NOT NULL,
    explanation     TEXT,
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bi.analyst_feedback (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id     UUID        NOT NULL REFERENCES bi.question_suggestions(id),
    analyst_id      UUID        NOT NULL,
    action          TEXT        NOT NULL,  -- dismissed | investigate | validated
    notes           TEXT,
    feedback_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bi.question_investigations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id     UUID        NOT NULL REFERENCES bi.question_suggestions(id),
    investigator_id UUID        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'open',
    findings        TEXT,
    conclusion      TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at       TIMESTAMPTZ
);

-- ===========================================================================
-- RECURSO 23: AI Core – Recibo de Memória da IA
-- ===========================================================================

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_receipts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID,
    tenant_id       UUID,
    session_id      TEXT,
    memory_type     TEXT        NOT NULL DEFAULT 'session',  -- session | user | tenant
    content_hash    TEXT        NOT NULL,  -- hash do conteúdo, nunca o dado cru
    purpose         TEXT        NOT NULL,
    scope           TEXT        NOT NULL DEFAULT 'local',
    sensitive       BOOLEAN     NOT NULL DEFAULT false,
    active          BOOLEAN     NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS ix_amr_user ON ai_core.ai_memory_receipts (user_id, active);

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_scopes (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id      UUID        NOT NULL REFERENCES ai_core.ai_memory_receipts(id),
    module          TEXT        NOT NULL,
    permission_level TEXT       NOT NULL DEFAULT 'read'
);

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_purposes (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id      UUID        NOT NULL REFERENCES ai_core.ai_memory_receipts(id),
    purpose_code    TEXT        NOT NULL,
    description     TEXT        NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_use_logs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id      UUID        NOT NULL REFERENCES ai_core.ai_memory_receipts(id),
    module          TEXT        NOT NULL,
    action          TEXT        NOT NULL,
    correlation_id  UUID,
    used_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    denied          BOOLEAN     NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS ix_amul_receipt ON ai_core.ai_memory_use_logs (receipt_id, used_at);

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_expirations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id      UUID        NOT NULL REFERENCES ai_core.ai_memory_receipts(id),
    expired_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    reason          TEXT
);

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_revocations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id      UUID        NOT NULL REFERENCES ai_core.ai_memory_receipts(id),
    revoked_by      UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    revoked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ai_core.ai_memory_deletion_jobs (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id      UUID        NOT NULL REFERENCES ai_core.ai_memory_receipts(id),
    requested_by    UUID,
    reason          TEXT        NOT NULL,
    scheduled_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    status          TEXT        NOT NULL DEFAULT 'pending'
);

-- ===========================================================================
-- RECURSO 24: API Hub – Contrato Adaptativo de Integração
-- ===========================================================================

CREATE TABLE IF NOT EXISTS api_hub.integration_intents (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_id    UUID        NOT NULL,
    target_system   TEXT        NOT NULL,
    purpose         TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS api_hub.integration_data_classifications (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_id       UUID        NOT NULL REFERENCES api_hub.integration_intents(id),
    data_type       TEXT        NOT NULL,
    classification  TEXT        NOT NULL DEFAULT 'internal',  -- public | internal | confidential | sensitive
    justification   TEXT
);

CREATE TABLE IF NOT EXISTS api_hub.integration_scope_proposals (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_id       UUID        NOT NULL REFERENCES api_hub.integration_intents(id),
    proposed_scopes JSONB       NOT NULL DEFAULT '[]',
    rationale       TEXT,
    proposed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS api_hub.adaptive_contracts (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_id       UUID        NOT NULL REFERENCES api_hub.integration_intents(id),
    scope_proposal_id UUID      REFERENCES api_hub.integration_scope_proposals(id),
    version         INTEGER     NOT NULL DEFAULT 1,
    sla_config      JSONB       NOT NULL DEFAULT '{}',
    failure_policy  JSONB       NOT NULL DEFAULT '{}',
    status          TEXT        NOT NULL DEFAULT 'proposed',
    proposed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at    TIMESTAMPTZ,
    suspended_at    TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS api_hub.compatibility_reports (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID        NOT NULL REFERENCES api_hub.adaptive_contracts(id),
    check_type      TEXT        NOT NULL,
    result          TEXT        NOT NULL,
    details         JSONB       NOT NULL DEFAULT '{}',
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS api_hub.integration_cost_estimates (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID        NOT NULL REFERENCES api_hub.adaptive_contracts(id),
    estimate_type   TEXT        NOT NULL DEFAULT 'operational',
    -- Nunca expor margem ou custo interno
    total_estimate  NUMERIC(18,2),
    currency        TEXT        NOT NULL DEFAULT 'BRL',
    valid_until     TIMESTAMPTZ,
    estimated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS api_hub.integration_failure_policies (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID        NOT NULL REFERENCES api_hub.adaptive_contracts(id),
    policy_type     TEXT        NOT NULL,  -- timeout | retry | circuit_breaker | fallback
    config          JSONB       NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS api_hub.integration_rollbacks (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id     UUID        NOT NULL REFERENCES api_hub.adaptive_contracts(id),
    triggered_by    UUID        NOT NULL,
    reason          TEXT        NOT NULL,
    executed_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    snapshot        JSONB       NOT NULL DEFAULT '{}',
    idempotency_key TEXT        UNIQUE
);

-- ===========================================================================
-- ÍNDICES DE PERFORMANCE GERAIS
-- ===========================================================================

CREATE INDEX IF NOT EXISTS ix_mobplan_created ON mobility.mobility_intention_plans (created_at);
CREATE INDEX IF NOT EXISTS ix_coalitions_status ON marketplace.buying_coalitions (status, deadline);
CREATE INDEX IF NOT EXISTS ix_promises_due ON crm.promise_deadlines (due_date);
CREATE INDEX IF NOT EXISTS ix_anomalies_metric ON bi.anomaly_observations (metric, period);

COMMIT;
