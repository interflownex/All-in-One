# All-in-One

SuperApp modular com identidade unica para consumidores, empresas, riders,
prestadores, mobilidade, Jobs, saude e operacoes empresariais. Este repositorio
implementa a plataforma arquitetural e executavel definida no documento mestre:
microservicos FastAPI, contratos OpenAPI, persistencia PostgreSQL/MongoDB,
eventos, controles de seguranca, infraestrutura e gates de CI.

## Baseline implementado

- Seis superficies de aplicacao em `apps/`, todas dependentes do All-in-One ID.
- Vinte e cinco microservicos em `modules/`, cada um com runtime funcional,
  contrato, OpenAPI, Dockerfile, documentacao de dominio e testes.
- Runtime compartilhado com persistencia contratual SQLite, autorizacao,
  workflows, idempotencia, auditoria imutavel e outbox de eventos.
- PostgreSQL com 30 schemas, identidade, business/KYB, Jobs, RBAC/ABAC, wallet,
  ledger, escrow, operacoes e verticais; ledger/auditoria sao append-only.
- MongoDB validado para memoria IA consentida, social, metricas de influencer
  e telemetria.
- RabbitMQ com dispatcher transacional da outbox PostgreSQL, publisher confirms
  e evidencias de entrega append-only; Redis para suporte a cache/rate limit.
- CI para scaffold, contratos, testes, banco, OpenAPI, seguranca e automacao
  controlada de branches.

## Jobs E CTPS Digital

O usuario final pode manter curriculo, registrar experiencias informais,
buscar vagas e candidatar-se. O modulo `jobs` importa um PDF da CTPS Digital,
preserva o hash da evidencia, cifra o arquivo em storage privado e exibe itens extraidos como
`validated_by_document_import`; dados digitados pelo usuario sao exibidos
como `self_declared_unverified`. A importacao nao declara verificacao oficial
externa sem integracao autorizada.

Somente recrutadores vinculados a empresa ativa no All-in-One Business, com
escopo Jobs, acessam a base visivel de curriculos. Cada consulta individual
gera log append-only. Veja [docs/JOBS_CTSP_DIGITAL.md](docs/JOBS_CTSP_DIGITAL.md).

Jobs usa tabelas PostgreSQL tipadas e a outbox central quando
`ALL_IN_ONE_JOBS_POSTGRES_DSN` esta configurada; sem DSN, o store SQLite
permanece disponivel para desenvolvimento isolado. O Docker Compose configura
essa DSN e inicia Jobs somente depois das migrations.

## Eventos E Front-End Stitch

`workers/outbox_dispatcher` publica eventos pendentes de `audit.domain_events`
no exchange RabbitMQ `all-in-one.domain`, confirma a entrega e preserva cada
tentativa em `audit.event_deliveries`. Mensagens Jobs usam payload minimizado
e nao carregam PDF, chave de storage nem texto livre de curriculo.

O planejamento visual de front-end usa o Google Stitch por projeto isolado
para cada microservico. Execute `python scripts/stitch_orchestrator.py plan`
para gerar o contrato local; `discover` e `sync` exigem credencial Stitch
rotacionada fornecida via secret local. Veja
[docs/STITCH_FRONTEND.md](docs/STITCH_FRONTEND.md).

## Identidade e integridade

`identity.users.id` e o vinculo central dos recursos de dominio. Wallets,
cartoes NFC/LED, perfis Rider e escrows usam foreign keys compostas para
impedir que uma operacao referencie a wallet de outro usuario. Recursos
financeiros e logs de auditoria rejeitam `UPDATE` e `DELETE`.

## Execucao local

```bash
python -m pip install -r requirements-dev.txt
python scripts/scaffold_modules.py --check
python scripts/validate_repository.py
python -m pytest --import-mode=importlib
docker compose -f infra/docker/docker-compose.yml up --build
```

Exemplo isolado:

```bash
cd modules/identity
pip install -r requirements.txt
uvicorn main:app --port 8000
```

## Organizacao

| Caminho | Conteudo |
| --- | --- |
| `apps/` | Contratos das seis experiencias cliente |
| `modules/` | Microservicos funcionais e testes |
| `contracts/` | Contratos de dominio espelhados e versionaveis |
| `database/` | Migracoes PostgreSQL e validacoes MongoDB |
| `docs/` | Arquitetura, seguranca, eventos, operacao e roadmap |
| `infra/` | Docker, Kubernetes e Terraform inicial |
| `workers/` | Dispatchers e consumidores assincronos da plataforma |
| `.github/workflows/` | Gates e automacoes de entrega |

## Estado

O motor de dominio torna todos os modulos inicializaveis e testaveis. Integracoes
reguladas ou externas (Pix/cartoes, fiscal oficial, biometria, assinatura,
OCR, IA produtiva, hospitais, GPS de concessionarias) permanecem bloqueadas
para producao ate credenciais, homologacao, DPIA/LGPD e testes E2E
documentados em [docs/ROADMAP.md](docs/ROADMAP.md).
