# Operacao

## Gates por release

Execute scaffold check, validador de repositorio, testes Python, migrations em
banco limpo, validacao OpenAPI, scans de dependencia e imagem. Publique apenas
apos aprovacao manual das alteracoes financeiras, de identidade ou saude.

## Gates automatizados

- `scripts/check_git_sync.ps1`: valida merge/rebase em andamento, arvore local e
  divergencia entre a branch local e os remotos configurados.
- `scripts/validate_compose_health.ps1` e `scripts/validate_compose_health.py`:
  validam `docker compose config`, sobem o ambiente local e confirmam `/health`
  nas 13 APIs FastAPI principais; a versao Python e usada no CI Linux.
- `scripts/check_generated_artifacts.ps1` e `scripts/check_generated_artifacts.py`: executam scaffold/validadores e falham
  se algum artefato gerado alterar a arvore de trabalho sem commit; a versao Python cobre CI/Linux sem PowerShell.
- `.github/workflows/git-sync.yml`: executa a verificacao de sincronizacao da
  `main` em eventos de push e sob demanda.
- `.github/workflows/compose-health.yml`: executa o healthcheck Docker Compose
  no CI e falha se alguma API principal nao retornar `/health` com `status=ok`.

## Evidencias

Auditoria critica e ledger sao append-only. Eventos devem manter
`correlation_id`; logs de aplicacao nao devem expor dados sensiveis.

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

## Incidentes

Revogue sessoes/API keys, preserve trilha imutavel, suspenda publicacao ou
pagamento afetado, notifique compliance e registre decisao e recuperacao.

## Excecao Cloudflare Tunnel

Quando houver autorizacao explicita para publicar o endpoint local
`http://localhost:58578/stream` por HTTPS publico, use
`scripts/setup_cloudflare_stream_tunnel.ps1` com os parametros descritos em
`docs/CLOUDFLARE_TUNNEL_STREAM.md`. O fluxo instala `cloudflared` como servico
Windows persistente, mata `code-tunnel.exe` se estiver ativo e limita a
publicacao ao caminho `/stream`.
