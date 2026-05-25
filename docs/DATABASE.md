# Banco de Dados

## PostgreSQL

As migracoes em `database/postgres/migrations/` criam os schemas:

`identity`, `business`, `permissions`, `marketplace`, `stock`, `delivery`,
`services`, `mobility`, `erp`, `wms`, `tms`, `crm`, `bpm`, `document`,
`finance`, `billing`, `fiscal`, `hr`, `health`, `vision`, `legal`,
`property`, `audit`, `compliance`, `notifications`, `api_hub`, `insurance`,
`bi`, `ai_core` e `jobs`.

Valores BRL usam `NUMERIC(18, 4)`; saldo/token NEX usa `NUMERIC(18, 8)`.
Tabelas operacionais incluem UUID, `user_id`, status, timestamps, atores e
metadata JSONB. O usuario raiz e a unica excecao natural a referenciar a si
mesmo durante o cadastro.

## Propriedade financeira

- `finance.wallets` e unica por `(id, user_id)`.
- `delivery.rider_profiles`, `identity.led_cards`, `finance.ledger_entries` e
  `finance.escrows` referenciam a tupla wallet/proprietario.
- `identity.users.default_wallet_id` e `primary_led_card_id` sao FKs
  deferrable, permitindo criacao transacional sem quebrar integridade.

## Imutabilidade

`audit.logs`, `audit.event_deliveries` e `finance.ledger_entries` recebem
trigger que rejeita `UPDATE` e `DELETE`. A outbox `audit.domain_events` pode
marcar publicacao; cada tentativa de entrega e preservada separadamente.
Correcoes financeiras devem ser novos lancamentos compensatorios.

## Jobs E Procedencia Documental

- `jobs.resumes` pertence ao usuario e define se o curriculo pode ser
  encontrado por recrutadores Business.
- `jobs.resume_documents` preserva SHA-256 do PDF CTPS e rejeita alteracao ou
  exclusao por trigger append-only.
- `jobs.employment_records` possui constraint de procedencia: itens extraidos
  do documento exigem `validated_by_document_import` e documento de origem;
  itens manuais exigem `self_declared_unverified`.
- `jobs.job_postings` e `jobs.applications` modelam vagas e candidaturas.
- `jobs.resume_access_logs` preserva toda leitura empresarial de curriculo e
  tambem e append-only.
- A migration `007_jobs_runtime_private_documents.sql` registra criptografia
  do documento e idempotencia para operacoes Jobs.
- Com `ALL_IN_ONE_JOBS_POSTGRES_DSN`, o runtime Jobs grava diretamente nessas
  tabelas tipadas e nas tabelas centrais `audit.logs`/`audit.domain_events`.

## Publicacao Da Outbox

O worker `workers/outbox_dispatcher` publica eventos PostgreSQL pendentes no
RabbitMQ com confirmacao do broker. Sucesso atualiza `audit.domain_events`;
sucesso e falha adicionam evidencias imutaveis em `audit.event_deliveries`.
Consumidores devem aplicar deduplicacao por `event_id`, pois a garantia e
`at-least-once`.

## MongoDB

`database/mongodb/init/001_ai_social_telemetry.js` valida `ai_memory`,
`social_videos`, `influencer_metrics` e `telemetry_logs`, com indices de
usuario, geoespacial e expiracao por retencao.
