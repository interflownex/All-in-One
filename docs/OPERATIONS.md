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

Alertas obrigatorios ficam versionados em
`config/observability/outbox_alerts.json` e materializados em
`infra/kubernetes/base/outbox-alerting.yaml`:

- `OutboxPublishStalled`: pendencias existentes sem novas publicacoes na janela.
- `OutboxBacklogHigh`: backlog de eventos pendentes acima do limite.
- `OutboxDueHigh`: fila de retry pronta acima do limite.
- `OutboxRetryFailuresHigh`: aumento de falhas retryable recente.
- `OutboxOldestPendingTooOld`: evento pendente mais antigo acima de 1 hora.

As notificacoes nunca devem carregar payload sensivel; as evidencias aceitas
sao contadores, ids de eventos, logs do worker e ticket de incidente.

O dashboard operacional da outbox fica versionado em
`config/observability/outbox_dashboard.json` e materializado em
`infra/kubernetes/base/outbox-dashboard.yaml`, com visoes de pendentes,
retry, publicacoes e tendencia temporal.

### Runbook de incidentes

1. Confirmar o alerta disparado, abrir ticket e registrar `event_id`,
   `correlation_id`, `retry_count`, `next_retry_at`, `last_error_type` e a
   janela observada.
2. Se `OutboxPublishStalled` ou `OutboxBacklogHigh`:
   - verificar `outbox-dispatcher`, RabbitMQ e PostgreSQL;
   - identificar o modulo que mais cresce no backlog;
   - pausar o produtor afetado ate corrigir a causa raiz;
   - nao editar payload pendente manualmente.
3. Se `OutboxDueHigh` ou `OutboxRetryFailuresHigh`:
   - inspecionar logs do worker e `audit.event_deliveries`;
   - corrigir serializacao, allowlist, contrato ou dependencia externa;
   - aguardar o proximo ciclo de retry ou reiniciar o worker somente se ele
     estiver travado.
4. Se `OutboxOldestPendingTooOld`:
   - localizar o evento mais antigo e a origem;
   - verificar bloqueio de banco, mensageria ou falta de `publisher_confirmed`;
   - escalar o incidente quando o atraso tocar modulos regulados, financeiros
     ou de identidade.
5. Ao recuperar:
   - confirmar que `all_in_one_outbox_published_total` volta a subir;
   - verificar queda de `all_in_one_outbox_pending` e `all_in_one_outbox_due`;
   - anexar metricas e logs ao ticket;
   - preservar a trilha imutavel de auditoria.
6. Nunca incluir payload sensivel nas notificacoes ou no ticket.

## Observabilidade Comercial

O Marketplace expoe indicadores comerciais em `/metrics` com prefixo
`all_in_one_marketplace_*`, permitindo que o Prometheus historize volume de
pedidos, casos de suporte, avaliacoes, nota media e conversao. O resumo
funcional da jornada continua disponivel em `/valley/insights/commercial` e o
dashboard Grafana esta materializado em `config/observability/commercial_dashboard.json`
e `infra/kubernetes/base/commercial-dashboard.yaml`.

Metricas expostas:

- `all_in_one_marketplace_orders_total`: total de pedidos nao removidos.
- `all_in_one_marketplace_orders_paid`: pedidos em estados monetizados.
- `all_in_one_marketplace_orders_completed`: pedidos concluidos.
- `all_in_one_marketplace_support_cases_total`: casos de suporte e disputa.
- `all_in_one_marketplace_support_cases_open`: casos ainda abertos.
- `all_in_one_marketplace_support_cases_resolved`: casos resolvidos.
- `all_in_one_marketplace_reviews_total`: avaliacoes publicadas.
- `all_in_one_marketplace_average_rating`: nota media historica.
- `all_in_one_marketplace_conversion_rate_percent`: taxa de conversao comercial.

Ao investigar queda de receita ou reputação:

1. Conferir `/metrics` do Marketplace e a tendência histórica no Grafana.
2. Validar `/valley/insights/commercial` para o retrato funcional da jornada.
3. Correlacionar pedidos, suporte e avaliações com auditoria e outbox.

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

## Backup, Restore E DR

Antes de promover qualquer mudanca sensivel para producao, execute pelo menos
um ciclo de backup e restauracao em ambiente de homologacao ou scratch. O
objetivo e provar que PostgreSQL, MongoDB e storage privado conseguem ser
restaurados sem perda silenciosa de dados nem quebra de contratos.

Checklist minimo:

1. Gerar backup logico de PostgreSQL com `pg_dump`.
2. Restaurar o backup em banco de teste com `pg_restore`.
3. Gerar backup de colecoes MongoDB com `mongodump`.
4. Restaurar o backup MongoDB com `mongorestore`.
5. Validar um restore de storage privado ou bucket de artefatos.
6. Medir e registrar `rpo_minutes`, `rto_minutes`, `backup_id`, `restore_id`
   e `incident_ticket`.
7. Executar smoke tests nas APIs criticas apos a restauracao.
8. Registrar o resultado no runbook e manter a evidencia para auditoria.

Em desastre real:

1. Congelar novos deploys e abrir incidente.
2. Verificar escopo afetado, ultimo backup consistente e ponto de recuperacao.
3. Restaurar na ordem: banco, mensageria, storage, runtime.
4. Validar `health`, `audit.events`, outbox e principais jornadas de negocio.
5. Retomar o trafego somente apos smoke e aprovacao de operacao/compliance.

SLOs operacionais sugeridos:

- RPO maximo: 15 minutos para dados criticos.
- RTO maximo: 60 minutos para modulos criticos e 180 minutos para demais.
- Drill de restore: mensal, com ticket e evidencia anexada.
- Revisao de DR: trimestral, incluindo falha de banco e falha de storage.

## Incidentes

Revogue sessoes/API keys, preserve trilha imutavel, suspenda publicacao ou
pagamento afetado, notifique compliance e registre decisao e recuperacao.
