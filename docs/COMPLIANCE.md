# Compliance LGPD E Producao

Este documento consolida a primeira matriz operacional de compliance do
All-in-One. A fonte versionada esta em
`config/compliance/data_classification.json` e cobre os 25 modulos do catalogo.
O fluxo operacional de direitos do titular fica em
`config/compliance/data_subject_rights.json`. O contrato dos jobs de retencao,
anonimizacao, descarte e legal hold fica em
`config/compliance/retention_jobs.json`.

## Principios

- Minimizar dados por finalidade, modulo e jornada.
- Separar dados sensiveis brutos de payloads publicos, eventos e mockups.
- Guardar trilhas criticas em auditoria append-only.
- Aplicar retencao por obrigacao legal, contrato, consentimento ou defesa de
  direito.
- Exigir KMS/vault para segredos, documentos, biometria, prontuario, CTPS e
  credenciais.
- Dar suporte aos direitos do titular: acesso, correcao, portabilidade,
  anonimizacao, revogacao de consentimento e exclusao quando legalmente
  permitida.

## Matriz De Dados Sensiveis

| Grupo | Modulos | Risco | Controles minimos |
| --- | --- | --- | --- |
| Identidade e acesso | `identity`, `permissions`, `api_hub` | Critico/alto | DPIA, MFA, KMS/vault, credenciais hash-only, rotacao, testes negativos de permissao |
| Dinheiro, fiscal e empresa | `finance`, `business`, `erp` | Critico/alto | PSP/fiscal homologado, ledger append-only, conciliacao, segregacao de funcoes, backup/restore |
| Trabalho e pessoas | `jobs`, `hr`, `riders` | Critico/alto | Consentimento, cofre documental, retencao trabalhista, auditoria de acessos, validacao documental |
| Saude, documentos e IA | `health`, `document`, `ai_core`, `vision` | Critico | DPIA especifica, KMS, consentimento explicito, retencao curta quando aplicavel, governanca de modelo |
| Operacao local | `delivery`, `services`, `mobility`, `property`, `tms`, `wms` | Alto/medio | Opt-in de localizacao, minimizacao de endereco, POD seguro, retencao operacional, permissao por papel |
| Comercial e analytics | `marketplace`, `stock`, `crm`, `bpm`, `bi`, `legal` | Alto/medio | Anti-burla, opt-out, mascaramento, logs de exportacao, sigilo profissional, controle de margem/custo |

## Gates De Producao

Antes de producao ampla:

1. Validar a matriz `config/compliance/data_classification.json` contra o
   catalogo de modulos.
2. Executar DPIA para modulos `critical` e registrar aprovacao.
3. Homologar DPAs com provedores de KYC/KYB, PSP, fiscal, mapas, saude,
   assinatura, IA e armazenamento.
4. Ativar vault/KMS e rotacao de chaves.
5. Testar direitos do titular por modulo: exportacao, correcao, revogacao,
   anonimizacao e exclusao permitida.
6. Validar backup/restore e retencao para PostgreSQL, MongoDB e storage privado.
7. Rodar pentest, SAST/SCA, DAST e testes negativos de permissao.

## Direitos Do Titular

O atendimento operacional LGPD passa a ter contrato versionado. Cada pedido
deve informar `request_id`, `subject_id`, `right_type`,
`identity_verification_level`, `requested_at` e `source_channel`.

Direitos cobertos:

- Acesso aos dados.
- Correcao de dados.
- Portabilidade.
- Anonimizacao.
- Revogacao de consentimento.
- Exclusao quando legalmente permitida.

Regras obrigatorias:

- Todo fluxo comeca por validacao de identidade.
- Todo fluxo termina com auditoria em
  `compliance.data_subject_request.processed`.
- Saidas publicas nunca incluem segredos reais, chaves privadas, dados de
  cartao, biometria bruta, prontuario de terceiros ou documentos brutos sem
  revalidacao do titular.
- Modulos criticos (`identity`, `finance`, `jobs`, `document`, `hr`,
  `health`, `vision`, `ai_core` e `api_hub`) exigem cobertura completa dos
  direitos e revisao por papel de compliance quando houver dado sensivel.
- Quando houver obrigacao legal, contrato ativo, defesa de direito ou disputa,
  o pedido pode ser parcialmente atendido com justificativa registrada.

## Retencao, Anonimizacao E Descarte

Os jobs operacionais de retencao agora possuem contrato versionado antes da
ativacao produtiva:

- `retention_review_daily`: revisa dados vencidos por politica, contrato ou
  consentimento.
- `anonymization_worker_hourly`: anonimiza dados permitidos apos avaliacao de
  base legal.
- `deletion_worker_daily`: descarta dados excluiveis sem obrigacao legal ou
  disputa ativa.
- `legal_hold_reconciliation_daily`: bloqueia descarte quando houver obrigacao
  legal, fiscal, trabalhista, regulatoria ou defesa de direito.

Cada modulo declara acao padrao, razoes de legal hold, job minimo e dominio de
evidencia. Descartes produtivos exigem dry-run inicial, auditoria imutavel e
revisao legal para registros financeiros, fiscais, medicos, trabalhistas ou
contratos assinados.

A primeira implementacao executavel esta em
`modules/shared/retention_worker.py` e pode ser acionada por
`python -m workers.retention_worker.main --job <job> --input <arquivo.jsonl>`.
Ela processa candidatos em JSONL, aplica dry-run, bloqueia legal hold, redige
campos sensiveis em anonimizacao e gera recibo hash para descarte.

O modo operacional PostgreSQL usa `compliance.retention_candidates` como fila de
entrada e grava cada resultado em `compliance.retention_decisions`, `audit.logs`
e `audit.domain_events`. Para executar um lote:

```bash
python -m workers.retention_worker.main --postgres --job retention_review_daily --dry-run
```

O DSN vem de `ALL_IN_ONE_RETENTION_POSTGRES_DSN` e o tamanho do lote de
`ALL_IN_ONE_RETENTION_BATCH_SIZE`.

O agendamento declarativo foi adicionado em dois modos:

- Docker Compose: `retention-worker` roda em loop horario local, mantendo
  revisao, anonimizacao e descarte em `--dry-run` ate homologacao por modulo.
- Kubernetes: `CronJob retention-worker` roda `retention_review_daily --dry-run`
  de hora em hora, com DSN vindo de Secret/Vault e `concurrencyPolicy: Forbid`.

## Evidencia Atual

- `docs/SECURITY.md` descreve controles implementados e obrigatorios.
- `config/integrations/provider_matrix.json` inclui gates de producao por
  provedor externo.
- `config/compliance/data_classification.json` versiona a classificacao de
  dados, base legal, retencao e gates por modulo.
- `config/compliance/data_subject_rights.json` versiona SLA, workflow,
  evidencias, guardrails e cobertura por modulo para direitos do titular.
- `config/compliance/retention_jobs.json` versiona jobs de retencao,
  anonimizacao, descarte e legal hold por modulo.
- `modules/shared/retention_worker.py` e `workers/retention_worker/main.py`
  executam o processamento local dos candidatos de retencao.
- `database/postgres/migrations/016_compliance_retention_jobs.sql` cria a fila
  PostgreSQL de candidatos e a tabela append-by-policy de decisoes.
- `infra/docker/docker-compose.yml` e `infra/kubernetes/base/platform.yaml`
  declaram o agendamento seguro do worker de retencao.
- `config/observability/retention_alerts.json` versiona alertas de falha,
  atraso, backlog, idade do candidato mais antigo e ausencia de decisoes.
- `infra/kubernetes/base/retention-alerting.yaml` materializa esses alertas em
  `PrometheusRule` e `AlertmanagerConfig`.
- `tests/test_compliance_matrix.py` bloqueia ausencia de modulo, campos
  obrigatorios e classificacao invalida.
- `tests/test_data_subject_rights.py` bloqueia ausencia de direito, SLA
  invalido, modulo sem cobertura e exportacao de dados proibidos.
- `tests/test_retention_jobs.py` bloqueia ausencia de job, modulo sem regra,
  evidencia fraca e descarte destrutivo sem revisao legal.
- `tests/test_retention_worker.py` valida dry-run, anonimizacao, descarte,
  legal hold, revisao legal e processamento em lote.
- `tests/test_retention_scheduling.py` valida Compose e CronJob de retencao.
- `tests/test_retention_alerts.py` valida cobertura, expressoes Prometheus,
  SLA de resposta, proibicao de payload sensivel e materializacao Kubernetes.
- `.github/workflows/security.yml` agora bloqueia regressao com `pip-audit`,
  `bandit`, smoke runtime do API Hub e scan de imagem via Trivy para
  `api_hub`, `identity` e `jobs`.
- `tests/test_security_gates.py` valida a superficie publica do gateway,
  a validacao de API key/webhook e o contrato do workflow de seguranca.

## Pendencias

- Aplicar mutacoes definitivas nos stores de dominio apos homologacao de dry-run
  por modulo.
- Aplicar manifests de monitoramento no cluster real e validar disparo controlado
  dos alertas.
- Gerar evidencias de DPIA assinadas por modulo critico.
- Expandir a cobertura dos scans obrigatorios do CI para mais imagens e
  jornadas de runtime.
