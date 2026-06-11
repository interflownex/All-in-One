-- Migration 023: Indices de Performance para Outbox, Auditoria e Ledger
-- Data: 2026-06-01

BEGIN;

-- 1. Otimizacao do Dispatcher da Outbox (Busca por eventos prontos para envio/retry)
ALTER TABLE audit.domain_events
    ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMPTZ;

UPDATE audit.domain_events
SET next_retry_at = (metadata->>'next_retry_at')::timestamptz
WHERE next_retry_at IS NULL
  AND metadata->>'next_retry_at' IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_outbox_dispatcher_ready
ON audit.domain_events (next_retry_at, created_at, id)
WHERE status = 'pending' AND published_at IS NULL;

-- 2. Rastreabilidade Transversal (Busca por Correlation ID nos eventos)
CREATE INDEX IF NOT EXISTS idx_audit_events_correlation ON audit.domain_events (correlation_id);

-- 3. Performance de Saldo e Extrato (Finance e Gold Valley)
CREATE INDEX IF NOT EXISTS idx_finance_ledger_wallet_lookup
ON finance.ledger_entries (wallet_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_finance_gold_ledger_entity_lookup
ON finance.valley_gold_ledger_entries (merchant_business_id, created_at DESC);

-- 4. Otimizacao de Busca em Jobs (Visibilidade de Curriculos para Recrutadores)
CREATE INDEX IF NOT EXISTS idx_jobs_resumes_visibility
ON jobs.resumes (recruiter_visibility, status);

-- 5. Otimizacao de Busca em Business (Lookup de Membros por Empresa)
CREATE INDEX IF NOT EXISTS idx_business_membership_lookup ON business.user_company_memberships (company_id, status);

-- 6. Idempotencia da criacao de carteiras
ALTER TABLE finance.wallets
    ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(120);

CREATE UNIQUE INDEX IF NOT EXISTS finance_wallets_idempotency_uidx
ON finance.wallets (idempotency_key)
WHERE idempotency_key IS NOT NULL;

COMMENT ON INDEX audit.idx_outbox_dispatcher_ready IS 'Acelera a selecao de eventos pendentes pelo worker outbox-dispatcher';
COMMENT ON INDEX finance.idx_finance_ledger_wallet_lookup IS 'Otimiza o calculo de saldo derivado e listagem de extrato';

COMMIT;
