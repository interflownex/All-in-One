# Operacao

## Gates por release

Execute scaffold check, validador de repositorio, testes Python, migrations em
banco limpo, validacao OpenAPI, scans de dependencia e imagem. Publique apenas
apos aprovacao manual das alteracoes financeiras, de identidade ou saude.

## Gates automatizados

- `scripts/check_git_sync.ps1`: valida merge/rebase em andamento, arvore local e
  divergencia entre a branch local e os remotos configurados.
- `scripts/validate_compose_health.ps1`: valida `docker compose config`, sobe o
  ambiente local e confirma `/health` nas 13 APIs FastAPI principais.
- `scripts/check_generated_artifacts.ps1` e `scripts/check_generated_artifacts.py`: executam scaffold/validadores e falham
  se algum artefato gerado alterar a arvore de trabalho sem commit; a versao Python cobre CI/Linux sem PowerShell.
- `.github/workflows/git-sync.yml`: executa a verificacao de sincronizacao da
  `main` em eventos de push e sob demanda.
- `.github/workflows/compose-health.yml`: executa o healthcheck Docker Compose
  quando runtime, migrations, workers ou compose forem alterados.
- `.github/workflows/security.yml`: executa `pip-audit`, `bandit`, o smoke runtime `tests/test_security_gates.py` e o scan de imagem com Trivy para `api_hub`, `identity` e `jobs`.

## Evidencias

Auditoria critica e ledger sao append-only. Eventos devem manter
`correlation_id`; logs de aplicacao nao devem expor dados sensiveis.

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
