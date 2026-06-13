-- Migration 016: Indices de Performance para Outbox, Auditoria e Ledger
-- Data: 2026-06-01

-- 1. Otimizacao do Dispatcher da Outbox (Busca por eventos prontos para envio/retry)
CREATE INDEX IF NOT EXISTS idx_outbox_dispatcher_ready
ON audit.domain_events ((metadata->>'next_retry_at'), status)
WHERE status = 'pending';

-- 2. Rastreabilidade Transversal (Busca por Correlation ID em Logs e Eventos)
ALTER TABLE audit.logs
ADD COLUMN IF NOT EXISTS correlation_id UUID;

CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation ON audit.logs (correlation_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_correlation ON audit.domain_events (correlation_id);

-- 3. Performance de Saldo e Extrato (Finance e Gold Valley)
CREATE INDEX IF NOT EXISTS idx_finance_ledger_wallet_lookup ON finance.ledger_entries (wallet_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_finance_gold_ledger_entity_lookup ON finance.valley_gold_ledger_entries (merchant_business_id, created_at DESC);

-- 4. Otimizacao de Busca em Jobs (Visibilidade de Curriculos para Recrutadores)
CREATE INDEX IF NOT EXISTS idx_jobs_resumes_visibility ON jobs.resumes (recruiter_visibility, status);

-- 5. Otimizacao de Busca em Business (Lookup de Membros por Empresa)
CREATE INDEX IF NOT EXISTS idx_business_membership_lookup ON business.user_company_memberships (company_id, status);

COMMENT ON INDEX audit.idx_outbox_dispatcher_ready IS 'Acelera a selecao de eventos pendentes pelo worker outbox-dispatcher';
COMMENT ON INDEX finance.idx_finance_ledger_wallet_lookup IS 'Otimiza o calculo de saldo derivado e listagem de extrato';
