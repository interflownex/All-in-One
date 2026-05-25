# Rastreabilidade Do Documento Mestre

Este baseline transforma o documento `ALL_IN_ONE_MASTER_PROMPT_CODEX_COMPLETO`
em artefatos executaveis e registra explicitamente os incrementos ainda
necessarios para producao.

| Requisito mestre | Artefato implementado |
| --- | --- |
| Identidade unica e validacoes | `database/postgres/migrations/001_identity_and_schemas.sql`, `modules/identity/` |
| Business, filiais e aprovacao manual | `002_business_permissions_finance.sql`, `modules/business/` |
| RBAC, ABAC e alcadas | `permissions.*` na migration 002, `modules/permissions/` |
| Wallet, ledger, escrow e NFC | `finance.*` e `identity.led_cards` na migration 002 |
| Riders, Marketplace, Stock, Delivery, Services e Mobility | Migration 003 e respectivos modulos |
| ERP, WMS, TMS, CRM, BPM, GED, HR, Health, Vision, Legal e Property | Migration 004 e modulos |
| Auditoria, eventos, anti-burla e API Hub | Migration 005, runtime comum e documentacao |
| Curriculo, CTPS Digital PDF, vagas e acesso Business | Migrations 006/007, `modules/jobs/`, `modules/shared/private_documents.py`, `modules/shared/jobs_postgres_store.py`, `docs/JOBS_CTSP_DIGITAL.md` |
| IA, social e telemetria | `database/mongodb/init/001_ai_social_telemetry.js` |
| Seis apps | `apps/all-in-one-*` |
| Projetos e telas Stitch por microservico | `scripts/stitch_orchestrator.py`, `config/stitch/screen_manifest.json`, `docs/STITCH_FRONTEND.md` |
| Outbox PostgreSQL publicada em RabbitMQ | `modules/shared/outbox_dispatcher.py`, `workers/outbox_dispatcher/`, `tests/test_outbox_rabbitmq_integration.py` |
| Microservicos funcionais | 25 diretorios em `modules/`, gerados pelo catalogo |
| Contratos e OpenAPI | `contracts/`, `modules/*/OPENAPI.yaml`, validador OpenAPI |
| Infraestrutura | `infra/docker/`, `infra/kubernetes/`, `infra/terraform/` |
| CI/CD | `.github/workflows/` |
| Testes de modulo e Jobs | `modules/*/tests/`, `tests/test_identity_jobs_domain.py` |
| Seguranca, monetizacao e operacao | `docs/SECURITY.md`, `docs/MONETIZATION.md`, `docs/OPERATIONS.md` |

## Limite correto do baseline

Os microservicos possuem endpoints funcionais, store contratual e contratos,
mas integracoes reguladas ainda nao representam operacao produtiva. O roadmap
exige provider KYC/KYB/CTPS, pagamento/fiscal, aplicativos
visuais, observabilidade, E2E, carga, homologacao e compliance antes de beta
ou producao.
