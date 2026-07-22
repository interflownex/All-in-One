# Catálogo Físico de Dados (Baseado em Migrations)

**Referência:** `docs/plano_de_leitura.md`, Ordem 2

Este documento detalha a estrutura física do banco de dados PostgreSQL, inferida a partir da análise completa dos 24 arquivos de migração encontrados em `database/postgres/migrations/`. Ele serve como a primeira versão do catálogo de dados, focando na estrutura das tabelas, colunas, tipos e constraints.

---

## Schemas Definidos

As seguintes schemas foram criadas e agrupam as tabelas por domínio:

- `identity`
- `business`
- `permissions`
- `marketplace`
- `stock`
- `delivery`
- `services`
- `mobility`
- `erp`
- `wms`
- `tms`
- `crm`
- `bpm`
- `document`
- `finance`
- `billing`
- `fiscal`
- `hr`
- `health`
- `vision`
- `legal`
- `property`
- `audit`
- `compliance`
- `notifications`
- `api_hub`
- `insurance`
- `bi`
- `ai_core`
- `jobs`
- `identity_core`

---

## Estrutura das Tabelas

### Schema: `identity`

#### Tabela: `identity.users`

- `id` (UUID, PK)
- `all_in_one_id` (UUID, UNIQUE)
- `full_name` (VARCHAR(200))
- `cpf_document` (VARCHAR(32), UNIQUE)
- `birth_date` (DATE)
- `email` (CITEXT, UNIQUE)
- `phone_e164` (VARCHAR(20), UNIQUE)
- `password_hash` (TEXT)
- `face_hash` (TEXT, UNIQUE)
- `liveness_score` (NUMERIC(5, 4))
- `document_status` (VARCHAR(40))
- `kyc_status` (VARCHAR(40))
- `mfa_required` (BOOLEAN)
- `terms_accepted_at` (TIMESTAMPTZ)
- `lgpd_consent_at` (TIMESTAMPTZ)
- `default_wallet_id` (UUID)
- `primary_led_card_id` (UUID)
- `status` (VARCHAR(40))
- `metadata` (JSONB)
- `created_at` (TIMESTAMPTZ)
- `updated_at` (TIMESTAMPTZ)
- `deleted_at` (TIMESTAMPTZ)
- `created_by` (UUID)
- `updated_by` (UUID)
- `idempotency_key` (VARCHAR(100), UNIQUE)

#### Tabela: `identity.documents`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `document_type` (VARCHAR(60))
- `document_number_hash` (TEXT)
- `storage_key` (TEXT)
- `expires_at` (DATE)
- `verification_status` (VARCHAR(40))
- `status` (VARCHAR(40))
- ... (outros campos de metadados e auditoria)
- `idempotency_key` (VARCHAR(100), UNIQUE)

---

### Schema: `business`

#### Tabela: `business.companies`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `parent_company_id` (UUID, FK to `business.companies`)
- `cnpj` (VARCHAR(18), UNIQUE)
- `legal_name` (VARCHAR(240))
- `trade_name` (VARCHAR(240))
- ... (outros campos de metadados e auditoria)
- `idempotency_key` (VARCHAR(120), UNIQUE)

#### Tabela: `business.catalog_offers`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `company_id` (UUID, FK to `business.companies`)
- `source_module` (VARCHAR(60))
- `source_entity_id` (UUID)
- `offer_type` (VARCHAR(40))
- `title` (VARCHAR(240))
- `status` (VARCHAR(40))
- ... (outros campos de metadados e auditoria)
- `idempotency_key` (VARCHAR(100), UNIQUE)

---

### Schema: `permissions`

#### Tabela: `permissions.roles`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `company_id` (UUID, FK to `business.companies`)
- `name` (VARCHAR(80))
- `is_system` (BOOLEAN)
- ... (outros campos de metadados e auditoria)

#### Tabela: `permissions.access_policies`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `company_id` (UUID, FK to `business.companies`)
- `module` (VARCHAR(60))
- `expression` (JSONB)
- ... (outros campos de metadados e auditoria)

---

### Schema: `finance`

#### Tabela: `finance.wallets`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `brl_available` (NUMERIC(18, 4))
- `brl_held` (NUMERIC(18, 4))
- `idempotency_key` (VARCHAR(120), UNIQUE)
- ...

#### Tabela: `finance.ledger_entries`

- `id` (UUID, PK)
- `wallet_id` (UUID, FK to `finance.wallets`)
- `currency` (VARCHAR(10))
- `amount_brl` (NUMERIC(18, 4))
- `idempotency_key` (TEXT, UNIQUE)
- ... (Tabela Imutável)

---

### Schema: `jobs`

#### Tabela: `jobs.resumes`

- `id` (UUID, PK)
- `user_id` (UUID, FK to `identity.users`)
- `headline` (VARCHAR(240))
- `professional_summary` (TEXT)
- `recruiter_visibility` (VARCHAR(40))
- `idempotency_key` (TEXT, UNIQUE)
- ...

#### Tabela: `jobs.employment_records`

- `id` (UUID, PK)
- `resume_id` (UUID, FK to `jobs.resumes`)
- `source_type` (VARCHAR(50))
- `employer_name` (VARCHAR(240))
- `started_on` (DATE)
- `ended_on` (DATE)
- ...

---

### Schema: `audit`

#### Tabela: `audit.logs`

- `id` (UUID, PK)
- `actor_user_id` (UUID, FK to `identity.users`)
- `action` (VARCHAR(100))
- `resource_type` (VARCHAR(100))
- `resource_id` (UUID)
- `before_data` (JSONB)
- `after_data` (JSONB)
- ... (Tabela Imutável)

#### Tabela: `audit.domain_events` (Outbox)

- `id` (UUID, PK)
- `routing_key` (VARCHAR(120))
- `aggregate_id` (UUID)
- `correlation_id` (UUID)
- `payload` (JSONB)
- `status` (VARCHAR(40))
- `next_retry_at` (TIMESTAMPTZ)
- ...

---

_(Nota: Esta é uma representação abreviada. A estrutura completa de todas as tabelas e colunas foi inferida e será usada para a construção do Catálogo Lógico de Dados.)_
