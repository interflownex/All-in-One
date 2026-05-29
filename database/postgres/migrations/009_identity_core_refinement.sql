BEGIN;

-- Extensao uuid-ossp ja pode estar habilitada pela 001 (pgcrypto), mas garantindo uuid-ossp se preferido
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE SCHEMA IF NOT EXISTS identity_core;

-- Sincronizando identity.users para identity_core.users com campos adicionais
CREATE TABLE IF NOT EXISTS identity_core.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    global_id UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    document_cpf VARCHAR(14) UNIQUE,
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    account_status VARCHAR(50) DEFAULT 'PENDING_KYC',
    last_login_at TIMESTAMP WITH TIME ZONE,
    idempotency_key VARCHAR(100) UNIQUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- KYC Records
CREATE TABLE IF NOT EXISTS identity_core.kyc_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES identity_core.users(id) ON DELETE RESTRICT,
    biometry_hash TEXT NOT NULL,
    doc_front_url TEXT,
    doc_back_url TEXT,
    verification_status VARCHAR(50) DEFAULT 'PROCESSING',
    audited_by UUID,
    rejection_reason TEXT,
    verified_at TIMESTAMP WITH TIME ZONE,
    idempotency_key VARCHAR(100) UNIQUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- KYB Business Profiles
CREATE TABLE IF NOT EXISTS identity_core.business_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_user_id UUID NOT NULL REFERENCES identity_core.users(id) ON DELETE RESTRICT,
    legal_name VARCHAR(255) NOT NULL,
    trade_name VARCHAR(255),
    document_cnpj VARCHAR(18) UNIQUE NOT NULL,
    cnae_primary VARCHAR(20),
    business_status VARCHAR(50) DEFAULT 'PENDING_KYB',
    idempotency_key VARCHAR(100) UNIQUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Consents LGPD
CREATE TABLE IF NOT EXISTS identity_core.consents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES identity_core.users(id) ON DELETE CASCADE,
    document_version VARCHAR(50) NOT NULL,
    consent_type VARCHAR(100) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    accepted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP WITH TIME ZONE,
    idempotency_key VARCHAR(100) UNIQUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Auditoria Local do Modulo (especifica conforme pedido)
CREATE TABLE IF NOT EXISTS identity_core.audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    actor_user_id UUID NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_id UUID NOT NULL,
    old_payload JSONB,
    new_payload JSONB,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email_core ON identity_core.users(email);
CREATE INDEX IF NOT EXISTS idx_users_global_id_core ON identity_core.users(global_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor_core ON identity_core.audit_logs(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_business_cnpj_core ON identity_core.business_profiles(document_cnpj);

COMMIT;
