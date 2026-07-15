# Plano de Execucao Ordenada - All-in-One

Data-base: 2026-05-29  
Branch operacional: `main`  
Meta: transformar o MVP backend/data atual em beta operacional validado, com infraestrutura estavel, PostgreSQL real por modulo, jornadas E2E e integracoes externas homologadas.

Coordenada operacional atual:
- Executar em modo `local-first`, sem custo obrigatorio de Google Cloud neste momento.
- Manter compatibilidade com futura migracao para Google/AlloyDB preservando migrations, DSNs PostgreSQL, manifests e contratos ja versionados.

## 1. Estado consolidado

| Area | Conclusao | Evidencia atual | Leitura operacional |
| --- | ---: | --- | --- |
| Git e sincronizacao remota | 99% | `worktree-sync` alinhado com `origin/main`; remoto `fork` indisponivel neste checkout | Fluxo de entrega via `origin` esta operacional; `fork` deve ser reconfigurado ou tratado como opcional quando ausente. |
| Contratos de microservicos | 100% | 25 modulos com OpenAPI, contratos, Dockerfile, docs e testes base | Superficie contratual completa para evoluir. |
| PostgreSQL estrutural | 90% | 15 migrations SQL, stores para 25 modulos, suite de matriz estrutural para todos os adapters PostgreSQL e suite viva preparada para os 25 modulos tipados | Schema amplo existe; falta converter a cobertura pronta em evidencia real de banco vivo. |
| Runtime FastAPI modular | 88% | Runtime comum, autorizacao, auditoria, outbox, catalogo Valley regionalizado, carregamento dinamico por DSN validado em containers e resolucao obrigatoria de store tipado para modulos conhecidos | Base local estabilizada; falta ampliar testes E2E por jornada. |
| Mensageria/outbox | 91% | RabbitMQ, dispatcher com correlation_id, retry/backoff observavel, metricas Prometheus text, alertas e dashboard versionados, testes criticos e payload seguro para eventos Valley/catalogo, Jobs, retencao e dominios operacionais centrais | Falta aplicar observabilidade no cluster real e conectar consumidores downstream reais. |
| MongoDB/NoSQL | 62% | Contrato versionado para AI/social/telemetria, script inicial com JSON Schema, indices de usuario/geoespacial/TTL e teste anti-drift | Precisa validacao viva em MongoDB real e uso operacional pelos modulos. |
| Docker local | 100% | Postgres, RabbitMQ, MongoDB, Redis, outbox, 13 APIs FastAPI healthy, gate CI Linux com validacao HTTP real, contexto Docker higienizado por `.dockerignore`, Docker DX persistente em `config/autonomy/docker_dx_policy.json` + `.env.docker-dx`, reparo sem sudo para plugins Compose/Buildx em `~/.docker/cli-plugins` e gate vivo `all-in-one-dx` validado neste host com 13 APIs healthy | Frente Docker local fechada; manter observacao do workflow remoto e regressao a cada mudanca de runtime/compose. |
| Apps/frontend | 100% | 9 apps prioritarios catalogados em `config/apps/frontend_journeys.json`, shells React dedicados/nomeados, trilha Valley com telas funcionais e Playwright, quatro shells fora Valley conectados a rotas proxy do API Hub, `all-in-one-user` e `all-in-one-business` com Playwright inicial desktop/mobile, dependencias Node materializadas, Playwright verde com interceptacao/API Hub vivo, User Jobs com busca/notificacoes/pos-candidatura, pos-corrida Mobility, filtros/auditoria Business, self-management API Hub para API clients/keys/webhooks/integration runs e acoes reais Services/Mobility/Riders/Health/Business/ERP/BI/WMS/TMS/CRM/BPM/Document/HR/Legal/Property/Vision/AI Core, Stitch remoto concluido com 25 projetos/180 telas e jornadas contratuais locais por pytest | Frente local concluida; proximas evidencias dependem de provedores/ambiente externos. |
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
- Gate Git Sync Linux `scripts/check_git_sync.py` cobre o workflow remoto sem
  depender de PowerShell Core no runner.
- Em 2026-07-15, `scripts/check_git_sync.py` passou a resolver o branch do
  upstream configurado antes de cair no nome da branch local; neste worktree
  `worktree-sync -> origin/main`, o gate padrao valida `origin/main:
  behind=0 ahead=0` e apenas avisa quando `fork` esta ausente.
- Em 2026-07-15, `scripts/check_generated_artifacts.py` voltou a passar sem
  rebaixar docs operacionais dos shells vivos; `scripts/scaffold_modules.py`
  preserva os README/STATUS customizados dos apps com API Hub conectado.

Pendencias:
- Reconfigurar o remoto `fork` neste checkout ou manter fechamento operacional
  via `origin` quando `fork` estiver indisponivel.
- Executar o gate de divergencia em ambiente com PowerShell Core disponivel e
  credenciais remotas configuradas.
- Gate Python/CI de artefatos gerados e Git Sync Linux entregues; manter
  execucao em todo fechamento.

Proximos passos naturais:
1. Rodar `scripts/check_git_sync.py` no fechamento de cada incremento; usar
   `scripts/check_git_sync.ps1` apenas quando PowerShell Core estiver
   disponivel no host.
2. Corrigir ou recriar o remoto `fork` quando ele voltar a ser necessario para
   escrita alternativa.
3. Manter `scripts/check_generated_artifacts.py` no CI e nos fechamentos locais Linux.

### Fase 1 - Estabilizacao Docker e runtime local

Objetivo: todos os servicos essenciais precisam subir de forma previsivel.

Status: 100%

Entregas ja existentes:
- `postgres`, `rabbitmq`, `mongodb` e `redis` sobem.
- Flags Google/AlloyDB/Stitch remoto podem permanecer desativadas sem bloquear a operacao local obrigatoria.
- Migrations rodam via servico `migrations`.
- 13 microservicos FastAPI sobem no compose com healthcheck HTTP.
- `api-hub`, `identity`, `finance`, `jobs` e `outbox-dispatcher` permanecem ativos.
- `depends_on` padronizado para aguardar migrations em modulos PostgreSQL.
- `ALL_IN_ONE_*_POSTGRES_DSN` injetado no compose para stores PostgreSQL tipados.
- `/health` validado em `localhost:8100` a `localhost:8112` com stores PostgreSQL.
- Gate CI Linux `compose-health.yml` executa
  `scripts/validate_compose_health.py`, validando `docker compose config`,
  subida do ambiente e `/health` com `status=ok` nas 13 APIs FastAPI
  principais.
- `.dockerignore` reduz o contexto de build removendo `.git`, `.venv`, caches,
  testes, apps, docs, relatorios, PDFs, node_modules e arquivos `.env*`
  sensiveis, preservando `.env.example`.
- Docker DX persistente foi versionado em
  `config/autonomy/docker_dx_policy.json`, com `.env.docker-dx` seguro,
  BuildKit ativo, projeto Compose `all-in-one-dx`, defaults locais sem segredos
  e fallback para `docker mcp` ausente.
- `scripts/configure_docker_dx.py` materializa/valida a DX sem travar quando o
  daemon Docker, Compose ou Buildx nao respondem.
- `scripts/configure_docker_dx.py` tambem repara, sem sudo, Compose/Buildx
  quebrados por symlinks antigos do Docker Desktop, criando links de usuario em
  `~/.docker/cli-plugins` para os plugins validos de `/usr/libexec`.
- Neste host, `docker compose version`, `docker buildx version`,
  `docker mcp version`, `python3 scripts/configure_docker_dx.py --check` e
  `docker compose --env-file .env.docker-dx -f infra/docker/docker-compose.yml
  config --quiet` responderam com sucesso apos o reparo.
- O gate vivo
  `python3 scripts/validate_compose_health.py --env-file .env.docker-dx
  --project-name all-in-one-dx --require-free-ports --down-after
  --command-timeout-seconds 900 --timeout-seconds 600
  --probe-timeout-seconds 1` passou neste host com banco limpo, migrations e 13
  APIs FastAPI healthy.

Pendencias:
- Medir tempo de rebuild dos containers Python no runner remoto apos reducao do
  contexto Docker.
- Acompanhar execucoes do workflow `compose-health.yml` no GitHub em ambiente
  remoto apos mudancas de runtime/compose.
- Executar o smoke test opt-in de banco limpo para migrations PostgreSQL em ambiente com imagem/base disponivel.

Proximos passos naturais:
1. Observar o gate `compose-health.yml` apos pushes que alterem runtime,
   migrations, workers ou compose.
2. Rodar `python3 scripts/configure_docker_dx.py --print-status` e a validacao
   Compose viva como regressao antes de alteracoes de runtime/compose.
3. Otimizar Dockerfiles com cache de dependencias se a medicao remota ainda
   indicar gargalo.
4. Registrar evidencias por execucao em `STATUS.md`.

### Fase 2 - Banco de dados e stores PostgreSQL

Objetivo: trocar o contrato local por persistencia PostgreSQL real, auditavel e testada.

Diretriz de menor manutencao:
- O banco operacional atual deve ser PostgreSQL local/self-managed, usando os mesmos contratos e migrations preparados para futura migracao a AlloyDB.

Status: 93%

Entregas ja existentes:
- 15 migrations PostgreSQL.
- `BasePostgresStore` compartilhado.
- Stores especializados para `jobs`, `identity`, `finance`, `api_hub`, `business`, `marketplace`, `delivery`, `services` e `mobility`.
- Stores gerados para os demais modulos.
- Idempotencia espalhada nas principais tabelas.

Pendencias:
- Validar migrations 001-015 em banco limpo e banco ja populado fora do GitHub
  Actions via smoke efemero ou `scripts/validate_postgres_real_dsn.py` com DSN
  real de homologacao.
- Rodar o gate opt-in `tests/test_postgres_migrations_smoke.py` com `ALL_IN_ONE_ENABLE_POSTGRES_SMOKE=1` em ambiente com Docker e imagem PostgreSQL pronta.
- Evoluir o CRUD amplo de `tests/test_postgres_stores_matrix.py` para fixtures
  completas por modulo; a cobertura estrutural e a existencia das tabelas contra
  schema vivo ja rodam no workflow `Database`.
- Replicar a suite `tests/test_postgres_priority_stores_integration.py` fora do
  GitHub Actions, em DSN PostgreSQL real de homologacao, para os 25 stores ja
  validados no workflow `Database`.
- Confirmar audit/outbox append-only em todos os fluxos sensiveis; `audit.logs`
  e `audit.event_deliveries` ja sao verificados pelo validador DSN com
  `--write-checks`.
- Confirmar outbox para eventos de todos os modulos.
- Eliminar usos reais remanescentes de stores genericos em fluxos PostgreSQL e manter o runtime falhando rapido quando um store tipado obrigatorio estiver ausente.

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
1. Rodar `scripts/validate_postgres_real_dsn.py --apply-migrations --repeat-migrations --write-checks` com `ALL_IN_ONE_POSTGRES_MATRIX_DSN` apontando para PostgreSQL real.
2. Rodar `tests/test_postgres_migrations_smoke.py` com `ALL_IN_ONE_ENABLE_POSTGRES_SMOKE=1` em ambiente com imagem PostgreSQL pronta, quando o daemon Docker local estiver estavel.
3. Rodar `tests/test_postgres_priority_stores_integration.py` em ambiente com DSN real para obter prova CRUD viva adicional nos 25 stores tipados.
4. Evoluir `tests/test_postgres_stores_matrix.py` com fixtures completas antes
   de habilitar `ALL_IN_ONE_ENABLE_POSTGRES_MATRIX_CRUD=1` no CI.
5. Testar create/get/list/update/soft_delete/idempotency por modulo.
6. Testar audit/outbox por modulo.
7. Corrigir cada store gerado que tentar gravar colunas inexistentes.

Nota operacional atual:
- O smoke opt-in ja esta endurecido para falhar rapido quando o host nao consegue
  iniciar `postgres:16` efemero; neste host especifico o resultado observado foi
  `SKIPPED` por timeout do Docker ao iniciar o contêiner, entao a pendencia
  restante depende de um daemon/host com PostgreSQL efemero funcional.
- Para nao depender apenas desse daemon, `scripts/validate_postgres_real_dsn.py`
  agora valida banco real por DSN, aplica/reaplica migrations quando solicitado
  e confirma evidencias append-only/outbox com `--write-checks`.
- O workflow `Database` tambem executa esse validador contra PostgreSQL de
  servico do GitHub Actions e roda a suite viva dos 25 stores tipados com
  `ALL_IN_ONE_POSTGRES_MATRIX_DSN`.
- O mesmo workflow agora executa a matriz PostgreSQL contra o schema vivo,
  validando que os 25 adapters apontam para tabelas existentes apos migrations;
  o CRUD amplo da matriz permanece opt-in ate receber fixtures completas.
- A falha publica do workflow `Database #132` no passo DSN foi reduzida no
  repositorio: o contrato agora exige as tabelas reais de retencao
  `compliance.retention_candidates`/`compliance.retention_decisions` e apenas
  indices declarados nas migrations; a proxima execucao deve confirmar se ha
  nova falha viva a tratar.
- A execucao publica `Database #133` confirmou o avanco do passo DSN e revelou
  a proxima falha em `Exercise all typed PostgreSQL stores`; a primeira correcao
  aplicada foi reconhecer `rider.%` como alias historico de outbox do modulo
  `riders`.
- A execucao publica `Database #134` manteve o contrato DSN verde e indicou que
  a falha segue na suite viva dos stores; foi corrigido o uso indevido de IDs de
  usuarios operacionais como `actor_entity_id` de auditoria em services,
  delivery e mobility.
- Como `Database #135` ainda falhou no step agregado de stores sem traceback
  publico, o workflow foi dividido em steps por store prioritario para expor o
  proximo modulo quebrado via API publica do GitHub Actions.
- `Database #136` revelou `Exercise Identity PostgreSQL store` como primeiro
  modulo quebrado; a suite foi corrigida para gerar `phone_e164` unico e nao
  colidir com o usuario criado pelo validador DSN.
- `Database #137` concluiu com sucesso no GitHub Actions, validando migrations,
  contrato DSN, os 25 stores tipados, matriz PostgreSQL viva, Jobs PostgreSQL e
  outbox RabbitMQ no PostgreSQL de servico do CI.
- O traceback de Telegram em
  `C:\Users\ereta\.codex\worktrees\VALLEY\scripts\valley_communication_bridge.py`
  pertence a fluxo externo VALLEY e nao e requisito deste plano; a contenção
  persistente fica em `scripts/stop_conflicting_valley_runtime.ps1`, que
  desabilita a tarefa `ValleyCommunicationBridge` e encerra o processo
  `valley_communication_bridge.py` quando necessario.

### Fase 3 - Eventos, RabbitMQ e observabilidade

Objetivo: garantir comunicacao assincroma confiavel e rastreavel.

Status: 91%

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
- Alertas Prometheus/Alertmanager versionados cobrem backlog alto, pendente
  antigo, falhas retryable e ausencia de publicacoes confirmadas.
- Dashboard versionado da outbox cobre todos os sinais Prometheus exportados
  pelo worker.
- Runbook de incidentes da outbox em `docs/OPERATIONS.md#outbox` cobre triagem,
  mitigacao, recuperacao e encerramento dos alertas versionados sem expor
  payload sensivel.
- `Database #137` validou emissao de audit/outbox nos 25 stores PostgreSQL
  prioritarios e despacho RabbitMQ em PostgreSQL de servico do CI.
- Contratos seguros de payload downstream cobrem dominios operacionais centrais
  fora de Valley, catalogo, Jobs e retencao, incluindo empresas, carteiras,
  API clients, logistica, mobilidade, warehouses, provedores, RBAC, datasets,
  processos, carriers e documentos fiscais, sempre por allowlist.

Pendencias:
- Aplicar `infra/kubernetes/base/outbox-alerting.yaml` e importar
  `config/observability/outbox_dashboard.json` no cluster/ferramenta real.
- Conectar consumidores downstream reais e validar comportamento ponta a ponta
  por dominio.
- Ampliar contratos apenas para dominios sensiveis que exigirem autorizacao
  explicita, mantendo CPF/CNPJ, saldos, hashes, segredos, localizacao,
  enderecos, prontuario e payload bruto fora das mensagens.

Proximos passos naturais:
1. Aplicar alertas e dashboard no ambiente Kubernetes/observabilidade real.
2. Criar fixtures de consumidor reais para payloads publicados por dominio.
3. Rodar dispatcher contra consumidores reais de cada dominio.
4. Exercitar o runbook de incidentes de fila em simulado operacional.

### Fase 4 - Jornadas E2E por app

Objetivo: transformar microservicos em jornadas de produto.

Status: 91%

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
- `config/apps/frontend_journeys.json` fixa o contrato versionado dos 9 apps
  prioritarios, mapeando diretorio canonico, shell React atual, pacote NPM,
  modulos de API Hub, evidencias pytest/Playwright e proximo E2E esperado.
- Shells React existentes agora usam nomes de pacote persistentes:
  `@all-in-one/user-shell`, `@all-in-one/business-shell`,
  `@all-in-one/valley`, `@all-in-one/valley-business` e
  `@all-in-one/valley-rider`.
- `all-in-one-riders`, `all-in-one-services`, `all-in-one-health` e
  `all-in-one-mobility` agora tambem possuem shells React/Vite dedicados,
  com jornada prioritaria, contratos API Hub visiveis, package name proprio e
  base para Playwright desktop/mobile.
- Esses quatro shells usam `VITE_API_HUB_URL`, proxy Vite local e rotas vivas
  do API Hub como `/riders/resources/rider_profiles`,
  `/services/resources/providers`, `/health/resources/patients` e
  `/mobility/resources/rides`, preservando fallback visual quando o hub nao
  estiver rodando.
- `tests/e2e/test_all_in_one_phase4_shells.py` cobre desktop e mobile dos
  quatro shells fora Valley com interceptacao das rotas do API Hub, validando
  estado `online` e marcadores de jornada.
- Em 2026-07-12, os quatro `package-lock.json` fora Valley foram materializados
  com `npm install --ignore-scripts --no-audit --no-fund`, e
  `./.venv/bin/python -m pytest -q tests/e2e/test_all_in_one_phase4_shells.py`
  passou com 8 testes.
- Em 2026-07-12, a mesma suite passou a subir API Hub e modulos FastAPI reais em
  portas efemeras, semear fixtures SQLite autenticadas por JWT e validar os
  quatro shells sem interceptacao de rede; o comando completo passou com 12
  testes.
- O contrato Health foi alinhado ao recurso Identity versionado
  `/identity/resources/consents`, e o proxy do API Hub passou a encaminhar
  `/modulo/resources/...` para `/resources/...` no servico alvo.
- `all-in-one-services` agora possui acao viva no shell para aceitar e concluir
  um contrato retornado pelo API Hub, validada por Playwright contra modulos
  FastAPI reais e fixtures SQLite.
- `all-in-one-services` tambem cobre pos-atendimento vivo: o shell mostra
  prestador, escrow operacional, evidencia documental e retorno do cliente
  usando metadados do API Hub.
- `all-in-one-mobility` agora possui acao viva no shell para aceitar/concluir
  corrida e usar ticket QR/NFC retornados pelo API Hub, tambem validada por
  Playwright contra modulos FastAPI reais e fixtures SQLite.
- `all-in-one-mobility` tambem cobre pos-corrida viva: o shell mostra rota,
  operador, ticket QR/NFC, wallet e comprovante operacional usando metadados
  do API Hub sem expor token bruto.
- `all-in-one-riders` agora possui acao viva no shell para submeter, aprovar e
  ativar perfil de rider retornado pelo API Hub; o gateway tambem propaga claims
  JWT de roles/scopes/MFA para headers internos `X-Actor-*`, mantendo a regra de
  aprovacao compliance auditavel.
- `all-in-one-riders` tambem cobre pos-ativacao viva: o shell mostra
  documento/veiculo, eventos de entrega/corrida e ganhos operacionais usando
  metadados do API Hub sem expor saldo bruto.
- `all-in-one-health` agora possui acao viva no shell para aprovar e concluir
  consulta retornada pelo API Hub, validada por Playwright contra modulos
  FastAPI reais e fixtures SQLite, mantendo aprovacao clinica com MFA e
  prontuario protegido.
- `all-in-one-health` tambem cobre governanca clinica viva: o shell mostra
  consentimento LGPD verificado, prontuario protegido e retorno pos-consulta
  usando apenas metadados operacionais retornados pelo API Hub.
- `config/apps/frontend_journeys.json` foi reconciliado em 2026-07-12 para que
  os quatro shells ja cobertos por Playwright vivo apontem seus proximos E2E
  para aprofundamento funcional por dominio, nao mais para "evoluir para API Hub
  vivo".
- `all-in-one-user` agora possui Playwright inicial desktop/mobile em
  `tests/e2e/test_all_in_one_user_shell.py`, percorrendo o shell compartilhado
  `apps/all-in-one` pela jornada Identity, Wallet, Marketplace Orders, Delivery
  e Jobs com rotas `/gateway/...` interceptadas.
- `all-in-one-user` tambem possui cobertura Playwright viva no mesmo arquivo,
  subindo API Hub e modulos FastAPI reais para Identity, Wallet, Marketplace
  Orders, Delivery e Jobs, com acoes reais de pagamento sandbox (`paid`) e
  entrega (`completed`) no frontend.
- `all-in-one-user` tambem cobre candidatura Jobs viva via API Hub: a fixture
  focada publica a vaga semeada, o frontend cria curriculo do usuario
  autenticado e registra candidatura `submitted` contra o modulo Jobs real.
- `all-in-one-user` tambem cobre a camada funcional de consumidor em Jobs:
  busca vagas publicadas por `/jobs/vacancies?q=...`, mostra notificacoes de
  busca/candidatura e exibe painel pos-candidatura com status, candidatura e
  curriculo contra API Hub e Jobs reais.
- O gateway de pagamento sandbox deixou de persistir metadados internos com o
  termo `pix` no payload protegido de pedido, preservando a politica anti-burla
  do Marketplace enquanto permite o fluxo server-side de pagamento.
- `all-in-one-business` agora possui Playwright inicial desktop/mobile em
  `tests/e2e/test_all_in_one_business_shell.py`, percorrendo Companies, Catalog
  Offers, Job Postings, Applications e Resume Access Logs com rotas
  `/gateway/...` interceptadas.
- `all-in-one-business` tambem possui cobertura Playwright viva no mesmo
  arquivo, subindo API Hub e modulos FastAPI reais para Business e Jobs, com
  acoes reais de aprovacao de empresa (`approved`), publicacao de vaga
  (`published`) e registro auditavel de acesso a curriculo no frontend.
- `all-in-one-business` tambem cobre ERP/BI vivos no API Hub: a fixture
  Playwright semeia `erp/fiscal_documents` e `bi/dashboards`, e o frontend
  aprova documento fiscal e dashboard BI por `actions/approve` contra modulos
  FastAPI reais.
- `all-in-one-business` tambem cobre WMS/TMS/CRM vivos no API Hub: a fixture
  Playwright semeia `wms/warehouses`, `tms/freights` e `crm/opportunities`, e o
  frontend aprova operacoes de estoque, transporte e pipeline comercial por
  `actions/approve` contra modulos FastAPI reais.
- `all-in-one-business` tambem cobre BPM/Document/HR vivos no API Hub: a fixture
  Playwright semeia `bpm/processes`, `document/documents` e `hr/employees`, e o
  frontend aprova fluxos BPM, documentos e registros HR por `actions/approve`
  contra modulos FastAPI reais.
- `all-in-one-business` tambem cobre Legal/Property/Vision/AI Core vivos
  no API Hub: a fixture Playwright semeia `legal/cases`,
  `property/properties`, `vision/devices` e `ai_core/moderation_decisions`, e o
  frontend aprova esses registros por
  `actions/approve` contra modulos FastAPI reais.
- `all-in-one-business` agora cobre pos-acoes, filtros e auditoria operacional:
  `SmartCRUD` exibe filtro de status, metricas de registros, painel de auditoria
  da ultima acao viva e badges de status validados por Playwright.
- O API Hub passou a expor self-management pelos endpoints nativos
  `/resources/...`: o Business shell aprova `api_clients`, `api_keys`,
  `webhooks` e `integration_runs` vivos com auditoria visual sem expor segredo
  bruto.

Pendencias:
- Homologar as jornadas contra provedores externos reais quando credenciais e
  ambientes responsivos estiverem disponiveis.
- Acompanhar regressao Playwright/pytest dos shells vivos em cada mudanca de
  frontend, gateway ou regras de dominio.

Proximos passos naturais:
1. Manter as 7 jornadas contratuais locais e os Playwright vivos como base de
   regressao de produto.
2. Homologar KYB, Apigee API Hub e provedores externos quando o ambiente
   responsivo e credenciais legitimas estiverem disponiveis.
3. Registrar evidencias por app em `STATUS.md`.

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
- Respostas sandbox agora carregam bloco `audit` comum com `audit_id`,
  `payload_sha256`, eventos emitidos e retencao `sandbox_audit_90d_no_raw_sensitive_input`,
  permitindo rastreabilidade sem persistir entrada sensivel bruta.
- Configuracao `config/integrations/environment_profiles.json` separa
  `sandbox`, `homologacao` e `producao`, com `ALL_IN_ONE_INTEGRATION_ENV`,
  evidencias obrigatorias, politica de segredos e rollback por ambiente.
- `tests/test_integration_provider_matrix.py` valida a matriz de provedores e a
  promocao entre ambientes para impedir ativacao externa sem contrato, secret
  store e gate de producao.
- Plano persistente `config/cloud/apigee_api_hub_plan.json` registra o inicio do
  fluxo Apigee/API Hub no Google Cloud: projeto host `all-in-one-498012`,
  service identity `service-864981916504@gcp-sa-apihub.iam.gserviceaccount.com`,
  location `southamerica-west1`, CMEK obrigatorio antes de apply e grants IAM
  esperados para KMS/API Hub.
- Em 2026-07-15, com ADC responsivo, o apply remoto criou/verificou a service
  identity do API Hub e aplicou no projeto os roles `roles/apihub.admin` e
  `roles/apihub.runtimeProjectServiceAgent`. O grant KMS
  `roles/cloudkms.cryptoKeyEncrypterDecrypter` na chave `Software` ficou
  bloqueado por `BILLING_DISABLED` no projeto `864981916504`.
- Checagem posterior no mesmo ciclo voltou a indicar ADC
  `missing_or_unresponsive`; antes de novo apply remoto, renovar ADC em fluxo
  interativo legitimo.
- A chave KMS `projects/all-in-one-498012/locations/southamerica-east1/keyRings/Github/cryptoKeys/Software`
  foi selecionada no plano Apigee/API Hub por estar `ENABLED` no inventario
  autoritativo, e `scripts/configure_apigee_api_hub.py` materializa a verificacao
  e o apply idempotente da service identity/IAM com timeout anti-travamento.
- Em 2026-07-15, `scripts/configure_apigee_api_hub.py` foi endurecido para
  aceitar `--status` como alias de diagnostico, preferir `GCLOUD_BIN`/SDK Linux
  antes do SDK Windows montado e redigir o token de ADC no status.
- `scripts/google_cloud_control.py` tambem respeita `GCLOUD_TIMEOUT_SECONDS` e
  nao bloqueia mais a rodada quando `gcloud auth list` nao responde.
- `scripts/google_cloud_control.py auth` valida o pre-requisito do Google Cloud
  Data Agent Kit: login do Google Cloud CLI e Application Default Credentials,
  sem imprimir tokens e com suporte a `GCLOUD_BIN` para evitar SDK Windows
  montado no WSL quando ele nao responder.
- SDK Linux do Google Cloud instalado em `~/google-cloud-sdk/bin/gcloud`
  (`Google Cloud SDK 576.0.0`) e validado no WSL. O diagnostico atual segue
  com `cli_responsive=true` e conta ativa `nazareteandersoncarvalho@gmail.com`;
  o ADC esta intermitente entre token redigido obtido por `configure_apigee_api_hub.py --status`
  e `missing_or_unresponsive` no gate `google_cloud_control.py auth`, portanto
  ainda deve ser renovado antes de apply remoto.

Proximos passos naturais:
1. Reativar/associar billing do projeto `all-in-one-498012` sem contornar
   politica de provedor.
2. Renovar ADC com `~/google-cloud-sdk/bin/gcloud auth application-default
   login` em terminal interativo e definir o projeto com `gcloud config set
   project all-in-one-498012` se `--status` mostrar `(unset)`.
3. Reexecutar `PATH="$HOME/google-cloud-sdk/bin:$PATH" python3
   scripts/configure_apigee_api_hub.py --apply --timeout 120` para aplicar o
   grant KMS restante.
4. Validar importacao automatica dos proxies Apigee para o API Hub do projeto
   host.
5. Implementar adapters por provider real com testes de contrato.
6. Registrar evidencias de homologacao.

### Fase 6 - Seguranca, compliance e producao

Objetivo: sair de beta tecnica para producao auditavel.

Status: 64%

Pendencias:
- Aplicar mutacoes finais nos stores de dominio apos homologacao de dry-run por modulo.
- Aplicar manifests de monitoramento no cluster real e validar disparo controlado dos alertas.
- DPIA assinada por modulo critico.
- Pentest e DAST contra ambiente homologado.
- Executar testes de carga em homologacao com evidencias reais.
- Executar restore real de PostgreSQL/Mongo/storage e exercicio DR trimestral.
- Observabilidade produtiva completa aplicada no cluster real.
- Exercitar runbooks de incidentes em simulado operacional.
- Executar revisao trimestral de permissoes sensiveis com evidencias reais.

Proximos passos naturais:
1. Aplicar manifests de monitoramento no cluster real e validar disparo controlado dos alertas.
2. Aplicar mutacoes finais nos stores de dominio apos homologacao de dry-run.
3. Executar restore de Postgres/Mongo/storage privado contra ambiente isolado
   usando `config/operations/backup_restore_plan.json`.
4. Materializar PrometheusRules de API Hub, Identity, Finance e Jobs apos as
   metricas finais estarem expostas no cluster real.
5. Executar a primeira revisao operacional de permissoes usando
   `config/security/sensitive_permissions_review.json`.
6. Exercitar o primeiro simulado de incidente usando
   `config/operations/incident_response_runbooks.json`.
7. Executar os cenarios de carga em homologacao usando
   `config/operations/load_test_plan.json`.

## 3. Matriz por modulo

| Modulo | Conclusao | Estado | Pendencia principal | Proximo passo |
| --- | ---: | --- | --- | --- |
| `identity` | 88% | Contrato, runtime, PostgreSQL especializado, cadastro/login/KYC/MFA E2E, container healthy, negativas de documento/telefone no registro publico e entidades sensiveis alinhadas a catalogo/migrations/store cobertas por testes | KYC/KYB/liveness reais | Homologar provedor KYC/KYB/liveness e repetir evidencias negativas com dados controlados |
| `business` | 80% | Companies, memberships, idempotencia, store tipado, criacao/aprovacao de empresa, convite operacional com atribuicao de papel e negativas de role invalido/ativacao nao autorizada cobertos por testes | Fluxo KYB real homologado | Homologar KYB real e repetir evidencias de membership com dados produtivos controlados |
| `permissions` | 73% | RBAC/ABAC modelado, store gerado, matriz versionada, consumidores sensiveis de dominio ligados a `sensitive_permissions_review` e testes HTTP negativos/positivos para endpoints Identity/Finance/Health | Homologar enforcement RBAC/ABAC em ambiente real e revisar ABAC fino por tenant/contexto | Executar revisao RBAC/ABAC com dados homologados e ampliar evidencias por modulo critico restante |
| `finance` | 75% | Wallet, ledger, escrow, store tipado, ledger Gold Valley append-only e catalogo Finance reconciliado com `valley_gold_ledger_entries`/evento `valley.gold.ledger.posted` | PSP/Pix/split/fiscal reais | Conectar compra Gold a PSP/Pix real e manter saldo derivado por ledger em homologacao |
| `marketplace` | 74% | Catalogo, pedidos, store tipado, jornada pytest consumidor -> wallet -> escrow -> pedido -> pagamento sandbox, suporte/disputa, reviews com moderacao basica auditavel e observabilidade comercial segura no API Hub | Checkout completo, pagamento real, fulfillment com provider homologado e notificacoes vivas | Expandir checkout/fulfillment com provedor homologado e conectar notificacoes/dashboards ao ambiente vivo |
| `stock` | 69% | Dropshipping, fornecedores modelados, adapter sandbox `SupplierCatalogSandbox` com rota administrativa/testes e lifecycle local de `supplier_orders` com tracking/eventos | Integracoes reais de fornecedores | Homologar fornecedor real e repetir tracking de pedido fornecedor com provider homologado |
| `delivery` | 78% | Entregas, riders, cotacao, atribuicao, coleta/conclusao, POD append-only com hash/storage privado e entrega `completed` coberta por pytest/Playwright | Tracking real, matching e mapas/antifraude homologados | Homologar tracking/matching/POD com provider real e arquivos em storage final |
| `riders` | 70% | Candidatura, documentos, aprovacao, ativacao, veiculos e painel pos-ativacao com ganhos/documentos cobertos por pytest/Playwright | Ganhos financeiros reais e antifraude documental homologada | Homologar repasse de ganhos e validacao documental com providers reais |
| `services` | 75% | Prestadores, aprovacao, contrato, escrow operacional referenciado, evidencia documental e pos-atendimento cobertos por pytest/Playwright | Anti-burla avancado e escrow Finance homologado | Homologar liberacao de escrow, disputa e anti-burla com provider real |
| `mobility` | 78% | Rides, tickets QR/NFC tokenizados, ETA auditavel, tarifa versionada, aceite/conclusao e corrida/ticket cobertos por pytest/Playwright | ETA dinamico, NFC real e tarifas produtivas homologadas | Homologar mapas/ETA, NFC e tarifas dinamicas com providers reais |
| `jobs` | 89% | CTPS/cofre/outbox/testes, jornada candidato -> vaga -> recrutador e fluxo triagem -> shortlist -> entrevista com notificacoes via outbox cobertos por pytest | Homologacao CTPS oficial e Playwright E2E final | Homologar CTPS oficial e levar triagem/entrevista para Playwright vivo |
| `api_hub` | 82% | API keys/webhooks, SQL refinado, rotas gateway de API key/webhook e testes de rate limit | OAuth2 real e testes de proxy com servicos vivos | Testar OAuth2 real, assinatura de webhooks de saida e rate limit com Redis real |
| `erp` | 70% | Fiscal/accounting modelado, `ErpPostgresStore` tipado, billing create/detail/cancel, payables aprovados/baixados e receivables recebidos/conciliados com MFA cobertos por pytest | Fluxos contabeis reais e conciliacao fiscal homologados | Homologar integracoes contabeis/fiscais reais e conciliacao bancaria produtiva controlada |
| `wms` | 70% | Armazem/inventario modelados, `WmsPostgresStore` tipado, recebimento/alocacao, picking fechado com MFA e despacho auditavel cobertos por pytest | Operacao real de estoque homologada | Homologar coletores/estoque fisico real e ampliar evidencias com operacao controlada |
| `tms` | 70% | Fretes/transportadoras modelados, `TmsPostgresStore` tipado, frete aprovado/despachado/concluido, POD privado append-only e auditoria fechada com MFA cobertos por pytest | Torre de controle e POD real homologados | Homologar torre de controle/POD real e ampliar evidencias com transportadoras controladas |
| `crm` | 70% | Leads/oportunidades modelados, `CrmPostgresStore` tipado, lead qualificado, atividade concluida, oportunidade proposta/ganha com MFA e campanha lancada cobertos por pytest | Pipeline e campanhas reais homologados | Homologar pipeline/campanhas reais e ampliar evidencias com dados comerciais controlados |
| `bpm` | 70% | Processos/workflows modelados, `BpmPostgresStore` tipado, timers/SLA, tarefas com `due_at`, escalonamento MFA e eventos `bpm.task.escalated`/`bpm.task.completed` cobertos por pytest | Engine real de workflow homologada | Homologar engine/worker de timers em ambiente real e ampliar evidencias de escalonamento produtivo |
| `document` | 70% | GED/OCR/assinatura modelados, `DocumentPostgresStore` tipado, upload com cofre privado/KMS/hash, versoes append-only e eventos `document.uploaded`/`document.versioned` cobertos por pytest | OCR, assinatura e storage final homologados | Homologar bucket/KMS/OCR/assinatura reais e ampliar evidencias com arquivos produtivos |
| `hr` | 70% | HCM/ATS/LMS modelado, `HrPostgresStore` tipado, colaborador admitido, folha fechada com MFA, treinamento atribuido/concluido e eventos HR cobertos por pytest | Folha, ponto e LMS reais homologados | Homologar folha/ponto/LMS reais e ampliar evidencias com dados produtivos controlados |
| `health` | 68% | Pacientes, agenda, dado sensivel, consulta, consentimento LGPD e prontuario protegido cobertos por pytest/Playwright | Telemedicina, prescricao e governanca clinica homologadas | Homologar telemedicina/prescricao e governanca clinica com provider real |
| `vision` | 67% | Dispositivos, streams com URL hasheada, gravacoes append-only, alertas de movimento, triagem/resolucao com MFA e eventos Vision cobertos por pytest | Ingestao de video e IA produtivas homologadas | Homologar ingestao de video/IA e ampliar evidencias com streams reais controlados |
| `legal` | 67% | Casos/prazos/audiencias modelados, `LegalPostgresStore` tipado, casos com tipo/abertura/risco e fluxo prazo -> alerta MFA -> conclusao coberto por pytest | Integracoes tribunal/calendario homologadas | Homologar integracoes tribunal/calendario e ampliar evidencias com prazos reais controlados |
| `property` | 67% | Imoveis/unidades/locacoes modelados, `PropertyPostgresStore` tipado, locacao ativada com MFA e manutencao solicitada/agendada/concluida cobertas por pytest | Condominio e manutencao reais homologados | Homologar operacao condominial/manutencao real e ampliar evidencias com prestadores controlados |
| `bi` | 68% | Datasets/dashboards modelados, `BiPostgresStore` tipado, dataset com origem/refresh, publicacao MFA, dashboard com `allowed_roles` e exportacao auditavel cobertos por pytest | ETL, permissao analitica e datasets reais homologados | Homologar fontes ETL/permissoes analiticas reais e ampliar evidencias com datasets produtivos controlados |
| `ai_core` | 68% | Memoria/moderacao/model runs modelados, `AiCorePostgresStore` tipado, memorias indexaveis e execucao com adapter/provider/modelo/tokens/custo aprovado por MFA cobertos por pytest | Providers IA e governanca produtiva homologados | Homologar providers IA reais, governanca de modelos e custos produtivos controlados |

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
4. Manter gate CI de compose/healthcheck com validacao HTTP real.
5. Testar OAuth2 real, webhooks de saida e rate limit Redis no API Hub.
6. Implementar jornada E2E `business -> jobs -> candidate access`. Concluido em 2026-05-30.
7. Expandir jornadas E2E para delivery, riders, services, health e mobility. Concluido em 2026-05-31.
8. Levar jornadas contratuais para shell frontend e Playwright.
9. Atualizar `STATUS.md`.
10. Sincronizar Git.
