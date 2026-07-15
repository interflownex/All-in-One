# Operacao

## Gates por release

Execute scaffold check, validador de repositorio, testes Python, migrations em
banco limpo, validacao OpenAPI, scans de dependencia e imagem. Publique apenas
apos aprovacao manual das alteracoes financeiras, de identidade ou saude.

## Gates automatizados

- `scripts/check_git_sync.ps1` e `scripts/check_git_sync.py`: validam
  merge/rebase em andamento, arvore local e divergencia entre a branch local e
  os remotos configurados; a versao Python e usada no CI Linux.
- `scripts/validate_compose_health.ps1` e `scripts/validate_compose_health.py`:
  validam `docker compose config`, sobem o ambiente local e confirmam `/health`
  nas 13 APIs FastAPI principais; a versao Python e usada no CI Linux.
- `scripts/check_generated_artifacts.ps1` e `scripts/check_generated_artifacts.py`: executam scaffold/validadores e falham
  se algum artefato gerado alterar a arvore de trabalho sem commit; a versao Python cobre CI/Linux sem PowerShell.
- `.github/workflows/git-sync.yml`: executa a verificacao de sincronizacao da
  `main` em eventos de push e sob demanda usando o gate Python.
- `.github/workflows/compose-health.yml`: executa o healthcheck Docker Compose
  no CI e falha se alguma API principal nao retornar `/health` com `status=ok`.

## Evidencias

Auditoria critica e ledger sao append-only. Eventos devem manter
`correlation_id`; logs de aplicacao nao devem expor dados sensiveis.

## Backup, Restore E DR

O contrato operacional de backup/restore fica em
`config/operations/backup_restore_plan.json`. Ele cobre PostgreSQL, MongoDB,
storage privado de documentos e configuracao GitOps com RPO/RTO, frequencia de
backup, frequencia de teste de restore, validadores obrigatorios, evidencias
aceitas e rollback por ativo.

Regras obrigatorias:

- Backup sem restore testado nao conta como gate de producao atendido.
- Restore produtivo exige aprovacao humana, `incident_ticket` e ambiente
  isolado para validacao antes de liberar escrita.
- Evidencias nunca incluem dumps, documentos brutos, tokens, URLs assinadas ou
  payload sensivel; use hashes, contadores, IDs auditaveis e logs sanitizados.
- PostgreSQL restaurado deve passar migrations repetiveis, triggers
  append-only, `audit.logs`, `audit.domain_events` e outbox antes de promover.
- O exercicio DR trimestral deve comparar RPO/RTO observado com o contratado e
  registrar acao corretiva quando houver desvio.

## Validacao PostgreSQL Real

Quando o host local nao conseguir subir `postgres:16` efemero para o smoke
opt-in, use um PostgreSQL real ja provisionado por DSN. O validador abaixo nao
depende de Docker e cobre schemas, tabelas criticas, indices, triggers
append-only e, com flag explicita, evidencias de escrita em `audit.logs` e
`audit.domain_events`.

Validacao estrutural sem escrita:

```bash
ALL_IN_ONE_POSTGRES_MATRIX_DSN="postgresql://..." \
  ./.venv/bin/python scripts/validate_postgres_real_dsn.py
```

Banco limpo com migrations:

```bash
ALL_IN_ONE_POSTGRES_MATRIX_DSN="postgresql://..." \
  ./.venv/bin/python scripts/validate_postgres_real_dsn.py --apply-migrations
```

Banco ja populado ou validacao de idempotencia:

```bash
ALL_IN_ONE_POSTGRES_MATRIX_DSN="postgresql://..." \
  ./.venv/bin/python scripts/validate_postgres_real_dsn.py --apply-migrations --repeat-migrations
```

Homologacao com evidencias append-only/outbox:

```bash
ALL_IN_ONE_POSTGRES_MATRIX_DSN="postgresql://..." \
  ./.venv/bin/python scripts/validate_postgres_real_dsn.py \
    --apply-migrations --repeat-migrations --write-checks
```

Depois de um banco real validado, execute a suite viva dos 25 stores tipados:

```bash
ALL_IN_ONE_POSTGRES_MATRIX_DSN="postgresql://..." \
  ./.venv/bin/python -m pytest -q tests/test_postgres_priority_stores_integration.py
```

## Outbox

O dispatcher publica eventos `pending` e registra cada tentativa em
`audit.event_deliveries`. Falhas ficam `failed_retryable`, preservam o evento
como `pending` e atualizam `audit.domain_events.metadata` com `retry_count`,
`retry_delay_seconds`, `next_retry_at`, `last_error_type` e `last_error`.

Use `ALL_IN_ONE_OUTBOX_RETRY_BASE_SECONDS` e
`ALL_IN_ONE_OUTBOX_RETRY_MAX_SECONDS` para ajustar o backoff por ambiente.
Alertas operacionais devem observar eventos pendentes com `next_retry_at`
vencido, crescimento de `retry_count` e ausencia de entregas
`publisher_confirmed`.

Para coletar as metricas em formato Prometheus text, execute:

```bash
python -m workers.outbox_dispatcher.main --metrics
```

Metricas expostas:

- `all_in_one_outbox_pending`: eventos pendentes ainda nao publicados.
- `all_in_one_outbox_due`: eventos pendentes prontos para nova tentativa.
- `all_in_one_outbox_published_total`: eventos publicados.
- `all_in_one_outbox_failed_retryable_total`: tentativas retryable falhas.
- `all_in_one_outbox_max_retry_count`: maior contador de retry observado.
- `all_in_one_outbox_oldest_pending_age_seconds`: idade do pendente mais antigo.

Alertas Kubernetes/Prometheus ficam em
`infra/kubernetes/base/outbox-alerting.yaml` e cobrem backlog alto, evento
pendente antigo, crescimento de falhas retryable e ausencia de publicacoes
confirmadas quando ha eventos prontos para entrega. A politica versionada em
`config/observability/outbox_alerts.json` exige evidencias operacionais sem
incluir payload sensivel.

O dashboard versionado em `config/observability/outbox_dashboard.json` cobre os
mesmos sinais exportados pelo worker para importacao em Grafana ou ferramenta
compativel com PromQL.

### Runbook de incidentes da outbox

Escopo: use este runbook para os alertas `OutboxBacklogHigh`,
`OutboxOldestPendingTooOld`, `OutboxRetryableFailuresHigh` e
`OutboxDueWithoutDeliveries`. O objetivo e restaurar publicacao at-least-once
sem perder a trilha imutavel de `audit.domain_events` e
`audit.event_deliveries`.

Classificacao inicial:

- `critical`: `OutboxOldestPendingTooOld`, evento pendente mais antigo acima do
  SLA de 30 minutos ou impacto em fluxo financeiro, identidade, saude,
  trabalho ou compliance.
- `high`: backlog acima do limite ou crescimento de falhas retryable em 15
  minutos.
- `medium`: eventos vencidos existem, mas nao ha entregas confirmadas recentes.

Triagem nos primeiros 10 minutos:

- Abrir ticket de incidente e registrar horario, alerta, ambiente, commit e
  dashboard usado.
- Coletar apenas contadores e hashes: `pending_count`, `due_count`,
  `oldest_pending_age_seconds`, `failed_retryable_delta`, `published_delta`,
  `event_selector_hash`, `last_error_type` e logs do dispatcher sem payload.
- Confirmar se RabbitMQ aceita conexao, se o exchange
  `all-in-one.domain` existe e se o worker `outbox-dispatcher` esta em loop.
- Verificar se `next_retry_at` esta vencido para eventos pendentes e se
  `retry_count` cresce de forma compativel com o backoff configurado.

Mitigacao segura:

- Reiniciar apenas o worker `outbox-dispatcher` quando houver suspeita de pod,
  conexao AMQP ou deploy preso; nao alterar eventos manualmente.
- Se RabbitMQ estiver indisponivel, manter eventos como `pending`, preservar
  tentativas `failed_retryable` e escalar infraestrutura de fila.
- Se o erro for payload rejeitado por consumidor, pausar o consumidor afetado,
  manter a outbox ativa para outros dominios e abrir correcao de contrato.
- Nao publicar mensagens manualmente fora do dispatcher sem aprovacao de
  plataforma e registro no ticket; consumidores devem deduplicar por `event_id`.

Validacao de recuperacao:

- `all_in_one_outbox_due` volta a `0` ou cai de forma sustentada.
- `increase(all_in_one_outbox_published_total[15m]) > 0` apos a mitigacao.
- `all_in_one_outbox_oldest_pending_age_seconds` fica abaixo de `1800`.
- Novas tentativas aparecem em `audit.event_deliveries` sem violar
  append-only.

Encerramento:

- Registrar causa raiz, janela de impacto, dominios afetados, graficos antes e
  depois, hashes dos eventos amostrados e decisao de follow-up.
- Se houve dados sensiveis ou fluxo regulado afetado, acionar compliance antes
  de encerrar.
- Criar tarefa de prevencao quando a causa for contrato de payload, capacidade
  da fila, credencial, deploy ou consumidor downstream.

## Retencao LGPD

O worker de retencao LGPD processa candidatos em
`compliance.retention_candidates` e registra decisoes em
`compliance.retention_decisions`, `audit.logs` e `audit.domain_events`.

Execucao local avulsa:

```bash
python -m workers.retention_worker.main --postgres --job retention_review_daily --dry-run
```

Agendamento:

- Docker Compose: servico `retention-worker` roda em loop com
  `ALL_IN_ONE_RETENTION_POLL_SECONDS`.
- Kubernetes: `CronJob retention-worker` roda de hora em hora com
  `concurrencyPolicy: Forbid`.

Por seguranca, revisao, anonimizacao e descarte permanecem em `--dry-run` nos
agendamentos ate homologacao por modulo. A liberacao de mutacoes definitivas
exige DPIA/revisao legal e evidencia de dry-run sem bloqueios.

Alertas obrigatorios ficam versionados em
`config/observability/retention_alerts.json`:

- `RetentionCronJobFailed`: falha do job nas ultimas janelas.
- `RetentionCronJobDelayed`: atraso de conclusao acima de duas janelas.
- `RetentionBacklogHigh`: backlog de candidatos pendentes acima do limite.
- `RetentionOldestCandidateTooOld`: candidato mais antigo acima de 24 horas.
- `RetentionDecisionMissing`: candidatos pendentes sem novas decisoes.

As notificacoes nunca devem carregar payload sensivel; evidencias aceitas sao
hashes, contadores, logs do worker e ticket de incidente.

Para Kubernetes com Prometheus Operator, as regras aplicaveis ficam em
`infra/kubernetes/base/retention-alerting.yaml`, contendo `PrometheusRule` e
`AlertmanagerConfig` para rotear severidade critica tambem ao plantao de
plataforma.

## SLO E Alertas

O catalogo minimo de SLOs de producao fica em
`config/observability/slo_catalog.json`. Ele cobre API Hub, Identity, Finance,
Outbox, Retention e Jobs com objetivo, janela, SLI, PromQL, severidade,
evidencias aceitas e runbook. Notificacoes de SLO nunca devem incluir payload
sensivel; evidencias devem ser contadores, hashes, IDs auditaveis, logs
operacionais e `incident_ticket`.

SLOs de outbox e retencao reaproveitam alertas ja materializados em
`infra/kubernetes/base/outbox-alerting.yaml` e
`infra/kubernetes/base/retention-alerting.yaml`. SLOs de API Hub, Identity,
Finance e Jobs ficam definidos como contrato de observabilidade ate o cluster
real expor as metricas finais e receber os PrometheusRules correspondentes.

## Observabilidade Comercial

`GET /gateway/insights/commercial` consolida Marketplace, CRM e BI para operacao
comercial. O bloco `commercial_attention` deve ser usado para triagem de
reviews pendentes, suportes abertos e eventos CRM/BI aguardando consumo.

As notificacoes comerciais devem usar apenas contadores, status, runbook e
correlation_id. Payload de pedido, review, suporte, lead ou dashboard nao deve
ser enviado em alertas, e a politica exposta pela API deve manter
`include_sensitive_payload=false`.

Triagem padrao:

- Confirmar se o alerta representa erro de usuario, dependencia externa,
  deploy recente, saturacao de banco/fila ou regressao de codigo.
- Abrir `incident_ticket` com ambiente, commit, SLO afetado, janela,
  evidencias sem payload sensivel e responsavel.
- Mitigar por rollback, pausa de provider port, aumento de capacidade,
  reprocessamento idempotente ou fallback sandbox/homologacao quando aplicavel.
- Encerrar apenas apos o SLI voltar para dentro do objetivo e as evidencias
  ficarem anexadas ao ticket.

## Testes De Carga

O contrato de testes de carga fica em
`config/operations/load_test_plan.json`. Ele define cenarios criticos para API
Hub, Identity, Finance, Jobs e Retention, com duracao minima, RPS alvo,
metricas obrigatorias, criterios de sucesso, evidencias e gates de promocao.

Execucoes devem usar dados sinteticos/sanitizados, PSP sandbox, idempotency keys
sinteticas e nunca capturar senha, token, documento bruto, prontuario ou
payload de pagamento. Execucao em producao exige aprovacao humana, janela
operacional e bloqueio imediato quando o erro critico exceder o limite.

## Incidentes

O catalogo operacional de resposta a incidentes fica em
`config/operations/incident_response_runbooks.json`. Ele cobre acesso indevido a
dado sensivel, integridade de pagamentos/ledger, falhas da outbox, retencao
LGPD, backup/restore/DR e burn rate de SLO. Cada classe define severidade,
responsavel, sinais de disparo, contencao, evidencias sanitizadas, validadores
de recuperacao e exigencia de postmortem.

Revogue sessoes/API keys, preserve trilha imutavel, suspenda publicacao ou
pagamento afetado, notifique compliance e registre decisao e recuperacao.

## Excecao Cloudflare Tunnel

Quando houver autorizacao explicita para publicar o endpoint local
`http://localhost:58578/stream` por HTTPS publico, use
`scripts/setup_cloudflare_stream_tunnel.ps1` com os parametros descritos em
`docs/CLOUDFLARE_TUNNEL_STREAM.md`. O fluxo instala `cloudflared` como servico
Windows persistente, mata `code-tunnel.exe` se estiver ativo e limita a
publicacao ao caminho `/stream`.
