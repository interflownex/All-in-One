# Plano de Execucao Ordenada - All-in-One

Data-base: 2026-05-29  
Branch operacional: `main`  
Meta: transformar o MVP backend/data atual em beta operacional validado, com infraestrutura estavel, PostgreSQL real por modulo, jornadas E2E e integracoes externas homologadas.

## 1. Estado consolidado

| Area | Conclusao | Evidencia atual | Leitura operacional |
| --- | ---: | --- | --- |
| Git e sincronizacao remota | 100% | `local main`, `origin/main` e `fork/main` alinhados | Fluxo de entrega remoto esta operacional. |
| Contratos de microservicos | 100% | 25 modulos com OpenAPI, contratos, Dockerfile, docs e testes base | Superficie contratual completa para evoluir. |
| PostgreSQL estrutural | 81% | 15 migrations SQL e stores para 25 modulos, incluindo ledger Gold Valley append-only | Schema amplo existe; falta prova real por modulo. |
| Runtime FastAPI modular | 86% | Runtime comum, autorizacao, auditoria, outbox, catalogo Valley regionalizado e carregamento dinamico por DSN validado em containers | Base local estabilizada; falta ampliar testes E2E por jornada. |
| Mensageria/outbox | 90% | RabbitMQ, dispatcher com correlation_id, retry/backoff observavel e metricas Prometheus text, testes criticos, payload seguro, fixtures versionadas por modulo, matriz de dispatch e eventos reais de AI Core/API Hub validados no store/sandbox | Precisa ampliar cobertura para eventos reais de todos os modulos e dashboards reais. |
| MongoDB/NoSQL | 55% | Script inicial para AI/social/telemetria | Precisa validacao de colecoes, indices e uso real. |
| Docker local | 95% | Postgres, RabbitMQ, MongoDB, Redis, outbox e 13 APIs FastAPI healthy | Falta gate CI para impedir regressao de compose. |
| Apps/frontend | 63% | 9 apps catalogados, catalogo Valley backend regionalizado, plano Stitch com 25 projetos/177 telas e jornadas contratuais locais por pytest | Ainda falta app funcional real e Playwright E2E. |
| Integracoes externas | 38% | Contratos, matriz versionada, adapters sandbox e endpoints administrativos locais existem | Provedores reais dependem de credenciais/homologacao e testes de contrato externos. |
| Producao/compliance | 59% | `docs/COMPLIANCE.md`, matriz LGPD por modulo, fluxo de direitos do titular, contrato, worker local, fila PostgreSQL, agendamento seguro e PrometheusRule/AlertmanagerConfig de retencao LGPD | Faltam aplicar os manifests no cluster real, mutacoes finais nos stores de dominio, DPIA assinada, pentest, carga, DR, backup/restore e observabilidade produtiva. |

## 2. Ordem mandataria de execucao

### Fase 0 - Higiene operacional continua

Objetivo: impedir regressao enquanto o projeto avanca.

Status: 99%

Entregas esperadas:
- Manter `main` limpo e sincronizado com `origin` e `fork`.
- Executar `git add`, `git commit` e `git push` ao concluir cada atividade.
- Atualizar `STATUS.md` e este plano quando a realidade mudar.
- Selecionar automaticamente a opcao `2` em prompts interativos durante este processo.

Pendencias:
- Executar o gate de divergencia em ambiente com PowerShell Core disponivel e
  credenciais remotas configuradas.
- Gate Python/CI de artefatos gerados entregue; manter execucao em todo fechamento.

Proximos passos naturais:
1. Rodar `scripts/check_git_sync.ps1` no fechamento de cada incremento.
2. Corrigir credenciais locais de push para `origin` ou `fork`.
3. Manter `scripts/check_generated_artifacts.py` no CI e nos fechamentos locais Linux.

### Fase 1 - Estabilizacao Docker e runtime local

Objetivo: todos os servicos essenciais precisam subir de forma previsivel.

Status: 100%

Entregas ja existentes:
- `postgres`, `rabbitmq`, `mongodb` e `redis` sobem.
- Migrations rodam via servico `migrations`.
- 13 microservicos FastAPI sobem no compose com healthcheck HTTP.
- `api-hub`, `identity`, `finance`, `jobs` e `outbox-dispatcher` permanecem ativos.
- `depends_on` padronizado para aguardar migrations em modulos PostgreSQL.
- `ALL_IN_ONE_*_POSTGRES_DSN` injetado no compose para stores PostgreSQL tipados.
- `/health` validado em `localhost:8100` a `localhost:8112` com stores PostgreSQL.

Pendencias:
- Reduzir tempo de rebuild dos containers Python.
- Acompanhar primeira execucao do workflow `compose-health.yml` no GitHub.

Proximos passos naturais:
1. Executar compose em banco limpo e validar migrations 001-015.
2. Otimizar Dockerfiles com cache de dependencias.
3. Registrar evidencias por execucao em `STATUS.md`.

### Fase 2 - Banco de dados e stores PostgreSQL

Objetivo: trocar o contrato local por persistencia PostgreSQL real, auditavel e testada.

Status: 84%

Entregas ja existentes:
- 15 migrations PostgreSQL.
- `BasePostgresStore` compartilhado.
- Stores especializados para `jobs`, `identity`, `finance`, `api_hub`, `business`, `marketplace`, `delivery`, `services` e `mobility`.
- Stores gerados para os demais modulos.
- Idempotencia espalhada nas principais tabelas.

Pendencias:
- Validar migrations 001-015 em banco limpo e banco ja populado.
- Criar testes CRUD reais para cada store PostgreSQL.
- Confirmar audit log append-only em todos os fluxos sensiveis.
- Confirmar outbox para eventos de todos os modulos.
- Substituir stores genericos por mapeamentos tipados nos modulos de maior risco.

Prioridade de tipagem por risco:
1. `finance`
2. `identity`
3. `business`
4. `api_hub`
5. `marketplace`
6. `delivery`
7. `services`
8. `mobility`
9. `jobs`
10. Demais modulos operacionais

Proximos passos naturais:
1. Criar suite `tests/test_postgres_stores_matrix.py`.
2. Testar create/get/list/update/soft_delete/idempotency por modulo.
3. Testar audit/outbox por modulo.
4. Corrigir cada store gerado que tentar gravar colunas inexistentes.
5. Atualizar docs de DSN e operacao.

### Fase 3 - Eventos, RabbitMQ e observabilidade

Objetivo: garantir comunicacao assincroma confiavel e rastreavel.

Status: 87%

Entregas ja existentes:
- `audit.domain_events`.
- Worker `outbox-dispatcher`.
- Testes de integracao com RabbitMQ para fluxo critico.
- Allowlist segura do dispatcher cobre eventos Valley de concessao manual de
  Pepitas e cotacao progressiva Stock sem expor ledger privado, custo ou margem.
- Allowlist segura cobre `valley.catalog.offer.synced`, sem expor custo interno,
  margem, markup ou endereco sensivel.
- Mutacoes HTTP aceitam `X-Correlation-Id`, geram UUID quando ausente e gravam
  `correlation_id` em auditoria/outbox SQLite e eventos PostgreSQL.
- Falhas do dispatcher registram `failed_retryable`, mantem eventos pendentes e
  atualizam `retry_count`, `retry_delay_seconds`, `next_retry_at` e ultimo erro
  em `audit.domain_events.metadata`.
- Worker da outbox expoe metricas Prometheus text por `--metrics`, cobrindo
  pendentes, retries vencidos, publicados, falhas retryable, maior retry e idade
  do pendente mais antigo.
- Alertas da outbox agora estao materializados em JSON versionado e em
  `PrometheusRule`/`AlertmanagerConfig` Kubernetes para fila parada, backlog,
  retry e idade do pendente.
- Dashboard Grafana da outbox agora esta materializado em JSON versionado e em
  `ConfigMap` Kubernetes para visoes de backlog, retry, publicacoes e tendencia.
- Catalogo de fixtures de eventos de dominio materializado em
  `config/events/domain_event_fixtures.json` a partir de
  `config/module_catalog.json`.
- Matriz de dispatch do outbox coberta em `tests/test_domain_event_dispatch_matrix.py`
  para todos os eventos versionados.
- Eventos reais de AI Core e API Hub cobertos em
  `tests/test_ai_core_api_hub_completed_events.py` e
  `tests/test_integration_sandbox_adapters.py`, validando conclusao real no
  store compartilhado e no provider sandbox.

Pendencias:
- Validar eventos reais de todos os modulos.
- Consolidar dashboards Grafana para consumo operacional em cluster real.

Proximos passos naturais:
1. Rodar dispatcher contra eventos reais de cada dominio usando o catalogo de fixtures versionado e a matriz de dispatch.
2. Conectar metricas Prometheus text a dashboards Grafana.
3. Consolidar dashboards Grafana para consumo operacional em cluster real.

### Fase 4 - Jornadas E2E por app

Objetivo: transformar microservicos em jornadas de produto.

Status: 63%

Apps e prioridades:
- `all-in-one-user`: cadastro, wallet, busca, compra, delivery, jobs.
- `all-in-one-business`: empresa, aprovacao, usuarios, jobs, ERP, relatorios.
- `all-in-one-riders`: candidatura, documento, veiculo, entrega/corrida, ganhos.
- `all-in-one-services`: prestador, visita, orcamento, contrato, evidencia.
- `all-in-one-health`: paciente, agenda, prontuario, consulta.
- `all-in-one-mobility`: corrida, ticket, QR/NFC, historico.
- `valley`: consumidor, saldo Pepitas, descontos Stock e notificacoes.
- `valley-business`: loja local, Plano Essencial por CNPJ e concessao manual de Pepitas.
- `valley-rider`: entregador/corridas vinculadas ao ecossistema Valley.
- Catalogo Valley backend agrupa ofertas em linguagem simples por `food`,
  `product`, `service`, categoria amigavel e raio regional em km.

Pendencias:
- Implementar interfaces funcionais reais.
- Ligar cada app aos endpoints FastAPI.
- Criar Playwright E2E por jornada; as jornadas contratuais locais
  `identity -> wallet -> marketplace order`, `business -> jobs -> candidate access`,
  Delivery, Riders, Services, Mobility e Health ja estao cobertas por pytest.
- Regras Valley de Pepitas, desconto Stock, idempotencia e Plano Essencial ja
  estao cobertas por pytest contratual.
- Sincronizar design Stitch remoto com credencial rotacionada.

Proximos passos naturais:
1. Corrigir/validar plano Stitch local.
2. Definir shell frontend por app.
3. Consolidar as 7 jornadas contratuais locais como base de regressao de produto.
4. Levar as jornadas contratuais para Playwright desktop/mobile quando houver shell frontend.
5. Rodar testes E2E desktop/mobile.

### Fase 5 - Integracoes externas homologadas

Objetivo: substituir mocks/contratos por provedores reais.

Status: 38%

Pendencias por area:
- Identity: OIDC, MFA real, KYC/KYB, liveness, biometria e consentimento LGPD.
- Finance: PSP/Pix, split, escrow, refund, conciliacao, antifraude e fiscal.
- Jobs: verificador oficial CTPS Digital ou integrador autorizado.
- Marketplace/Stock: fornecedores homologados, catalogo, preco, pedido e tracking.
- Delivery/Mobility: mapas, ETA, tracking, roteirizacao, comprovante e antifraude.
- Health: governanca de prontuario, prescricao, telemedicina e consentimento.
- API Hub: OAuth2, API keys, webhooks assinados, sandbox e rate limits reais.

Entregas ja existentes:
- Matriz `config/integrations/provider_matrix.json` cobre provedores candidatos,
  adapter sandbox, eventos, variaveis de ambiente, dados sensiveis, custo minimo
  e gate de producao.
- Teste `tests/test_integration_provider_matrix.py` valida cobertura dos modulos
  criticos e impede versionamento acidental de valores de segredo.
- Adapters sandbox em `modules/shared/integration_sandbox.py` implementam
  KYC/KYB, Pix/PSP/escrow, fiscal, CTPS hash-only, mapas/ETA, consentimento
  clinico, API Hub/webhooks e catalogo fornecedor sem chamada externa.
- Teste `tests/test_integration_sandbox_adapters.py` valida contratos,
  eventos, determinismo e protecao contra vazamento de dado sensivel bruto.
- Endpoints administrativos `/integrations/sandbox/*` conectam os adapters aos
  modulos Identity, Business, Finance, ERP, Jobs, Delivery, Mobility, TMS,
  Health, API Hub, Stock, Riders e Services.
- Teste `tests/test_integration_sandbox_routes.py` valida autorizacao e contratos
  HTTP desses endpoints.

Proximos passos naturais:
1. Conectar respostas sandbox a recursos reais/auditaveis dos modulos prioritarios.
2. Separar sandbox/homologacao/producao.
3. Implementar adapters por provider real com testes de contrato.
4. Registrar evidencias de homologacao.

### Fase 6 - Seguranca, compliance e producao

Objetivo: sair de beta tecnica para producao auditavel.

Status: 59%

Pendencias:
- Aplicar mutacoes finais nos stores de dominio apos homologacao de dry-run por modulo.
- Aplicar manifests de monitoramento no cluster real e validar disparo controlado dos alertas.
- DPIA assinada por modulo critico.
- Pentest e SAST/DAST.
- Testes de carga.
- Backup/restore e disaster recovery.
- Observabilidade completa.
- Runbooks de incidentes.
- Revisao de permissoes para dados sensiveis de saude, identidade, financeiro e trabalho.

Proximos passos naturais:
1. Aplicar manifests de monitoramento no cluster real e validar disparo controlado dos alertas.
2. Aplicar mutacoes finais nos stores de dominio apos homologacao de dry-run.
3. Expandir a cobertura dos scans obrigatorios do CI para mais imagens e jornadas.
4. Testar restore de Postgres/Mongo.
5. Definir SLOs e alertas.

## 3. Matriz por modulo

| Modulo | Conclusao | Estado | Pendencia principal | Proximo passo |
| --- | ---: | --- | --- | --- |
| `identity` | 86% | Contrato, runtime, PostgreSQL especializado, cadastro/login/KYC/MFA E2E e container healthy | KYC/KYB/liveness reais | Homologar provedor KYC/KYB e ampliar testes negativos |
| `business` | 77% | Companies, memberships, idempotencia, store tipado e criacao/aprovacao de empresa coberta na jornada Jobs | Fluxo KYB real e convite operacional de usuarios | Testar convite de usuario e homologar KYB |
| `permissions` | 64% | RBAC/ABAC modelado e store gerado | Enforcement profundo em todos endpoints | Criar matriz de permissoes e testes negativos |
| `finance` | 74% | Wallet, ledger, escrow, store tipado e ledger Gold Valley append-only | PSP/Pix/split/fiscal reais | Conectar compra Gold a PSP/Pix e saldo derivado por ledger |
| `marketplace` | 68% | Catalogo, pedidos e store tipado | Checkout, pagamento e fulfillment | Jornada produto -> carrinho -> pedido -> pagamento |
| `stock` | 62% | Dropshipping e fornecedores modelados | Integracoes reais de fornecedores | Adapter inicial de fornecedor sandbox |
| `delivery` | 73% | Entregas, riders, cotacao, atribuicao, coleta/conclusao e store tipado | Tracking real, matching e POD com arquivo | Levar jornada pedido -> cotacao -> rider -> entrega para Playwright |
| `riders` | 68% | Candidatura, documentos, aprovacao, ativacao e veiculos cobertos por pytest | Ganhos reais e antifraude documental | Integrar ganhos Finance e validacao documental sandbox |
| `services` | 73% | Prestadores, aprovacao, contrato, escrow referenciado e conclusao cobertos por pytest | Anti-burla avancado e escrow Finance real | Integrar contrato Services ao escrow Finance |
| `mobility` | 73% | Rides, tickets, tarifa, aceite/conclusao e QR token cobertos por pytest | ETA, QR/NFC real e tarifas dinamicas | Levar jornada corrida e ticket para Playwright |
| `jobs` | 87% | Mais maduro: CTPS/cofre/outbox/testes e jornada candidato -> vaga -> recrutador coberta por pytest | Homologacao CTPS oficial e Playwright E2E | Expandir fluxo para triagem, entrevista e notificacoes |
| `api_hub` | 82% | API keys/webhooks, SQL refinado, rotas gateway de API key/webhook e testes de rate limit | OAuth2 real e testes de proxy com servicos vivos | Testar OAuth2 real, assinatura de webhooks de saida e rate limit com Redis real |
| `erp` | 60% | Fiscal/accounting modelado e store gerado | Fluxos contabeis reais | Tipar store ERP e testar payables/receivables |
| `wms` | 60% | Armazem/inventario modelados | Operacao real de estoque | Tipar store WMS e testar recebimento/picking |
| `tms` | 60% | Fretes/transportadoras modelados | Torre de controle e POD | Tipar store TMS e testar frete |
| `crm` | 60% | Leads/oportunidades modelados | Pipeline e campanhas reais | Tipar store CRM e testar lead -> oportunidade |
| `bpm` | 58% | Processos/workflows modelados | Engine real de workflow | Implementar timers/SLA/escalonamento |
| `document` | 58% | GED/OCR/assinatura modelados | Storage, OCR e assinatura reais | Tipar store e implementar upload/versionamento |
| `hr` | 58% | HCM/ATS/LMS modelado | Folha, ponto e LMS reais | Fluxo colaborador -> folha -> treinamento |
| `health` | 66% | Pacientes, agenda, protecao de dado sensivel e consulta cobertos por pytest | Consentimento, prontuario e telemedicina reais | Implementar consentimento auditavel e prontuario |
| `vision` | 55% | Dispositivos/streams/alertas modelados | Ingestao de video e IA | Prova de stream e alerta |
| `legal` | 55% | Casos/prazos/audiencias modelados | Integracoes tribunal/calendario | Fluxo caso -> prazo -> alerta |
| `property` | 55% | Imoveis/unidades/locacoes modelados | Condominio e manutencao reais | Fluxo locacao/manutencao |
| `bi` | 55% | Datasets/dashboards modelados | ETL e permissao analitica | Primeiro dashboard auditavel |
| `ai_core` | 55% | Memoria/moderacao/model runs modelados | Providers IA e governanca | Adapter de provider e custo por execucao |

## 4. Criterios de beta

O projeto entra em beta quando todos os itens abaixo estiverem verdes:

- Docker Compose sobe todos os servicos essenciais sem restart.
- Migrations PostgreSQL 001-015 aplicam em banco limpo.
- Stores PostgreSQL passam CRUD/idempotencia/audit/outbox em todos os modulos prioritarios.
- Pelo menos 6 jornadas E2E passam, uma por app; 7 jornadas contratuais locais ja passam por pytest.
- API Hub funciona com API key, webhook assinado e rate limit.
- Identity tem login/MFA/KYC sandbox.
- Finance tem pagamento/escrow/refund sandbox.
- Observabilidade basica registra logs, metricas e erros.
- CI bloqueia regressao de OpenAPI, testes, migrations e seguranca.

## 5. Primeira sprint de execucao

Sequencia recomendada:

1. Criar teste matriz de stores PostgreSQL.
2. Corrigir stores gerados que falharem contra Postgres.
3. Rodar migrations e testes em ambiente limpo.
4. Implementar gate CI de compose/healthcheck.
5. Testar OAuth2 real, webhooks de saida e rate limit Redis no API Hub.
6. Implementar jornada E2E `business -> jobs -> candidate access`. Concluido em 2026-05-30.
7. Expandir jornadas E2E para delivery, riders, services, health e mobility. Concluido em 2026-05-31.
8. Levar jornadas contratuais para shell frontend e Playwright.
9. Atualizar `STATUS.md`.
10. Sincronizar Git.
