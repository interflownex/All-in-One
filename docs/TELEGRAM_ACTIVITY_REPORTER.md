# Executor Telegram de Atividades e Pendências

**Versão:** 0.1  
**Data e hora:** 26/07/2026 às 23:06:33  
**Status:** implementação inicial, aguardando CI e configuração de secrets

## Objetivo

Enviar notificações de início e encerramento de atividades e relatórios de
pendências sem versionar credenciais e sem depender de rede durante os testes.

## Arquivos

- `scripts/telegram_activity_reporter.py`;
- `tests/test_telegram_activity_reporter.py`;
- `config/autonomy/telegram_delivery_policy.json`.

## Simulação segura

### Atividade iniciada

```bash
python3 scripts/telegram_activity_reporter.py --dry-run activity-started \
  --activity-name "Revisar pendências" \
  --technical-description "Cruzar documentação, código, issues e PRs" \
  --estimated-completion-time "2 horas" \
  --reported-difficulty 4 \
  --initial-progress-percent 0
```

### Atividade concluída

```bash
python3 scripts/telegram_activity_reporter.py --dry-run activity-completed \
  --activity-name "Revisar pendências" \
  --status partial_success \
  --completion-percent 70 \
  --pending-item "Executar CI" \
  --next-step "Atualizar issue"
```

### Relatório de pendências

```bash
python3 scripts/telegram_activity_reporter.py --dry-run pending-report \
  --report-index 1 \
  --open-pending "Homologar API Hub" \
  --blocked-pending "Stitch sem secret" \
  --risk-summary "PRs desatualizados" \
  --eta-summary "Ciclo de oito horas"
```

## Envio real

O envio real exige variáveis fora do Git:

```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python3 scripts/telegram_activity_reporter.py activity-started \
  --activity-name "Atividade autorizada" \
  --technical-description "Descrição" \
  --estimated-completion-time "1 hora" \
  --reported-difficulty 3
```

Nunca colocar os valores em documentação, argumentos persistidos, commits ou
logs.

## Testes

```bash
python3 -m pytest -q tests/test_telegram_activity_reporter.py
```

Os testes cobrem:

- dry-run sem credenciais;
- mensagem de início;
- mensagem de conclusão;
- limite de quatro relatórios;
- retry em falha transitória;
- rejeição de política que permita credenciais no Git.

## Critérios antes de agendar quatro relatórios

1. testes aprovados no commit atual;
2. revisão de segurança;
3. secrets legítimos configurados;
4. workflow com timeout e concorrência controlada;
5. dry-run registrado;
6. canal e chat confirmados pelo proprietário;
7. política de retenção de logs definida.

## Pendências

- executar CI;
- adicionar agenda após aprovação;
- integrar fonte real das pendências;
- criar artefato de evidência sem dados sensíveis;
- validar comportamento de rate limit HTTP 429.

## Revalidação de integração

Branch submetida a novo ciclo completo contra a `main` estabilizada em
28/07/2026, preservando todos os gates de CI e segurança.
