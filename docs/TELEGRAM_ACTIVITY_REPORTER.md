# Executor Telegram de Atividades e Pendências

**Versão:** 0.2  
**Data de reconstrução:** 28/07/2026  
**Classificação:** Técnico  
**Público-alvo:** Equipe Técnica  
**Status:** implementação inicial reconstruída sobre a `main` estabilizada; envio real e agendamento permanecem bloqueados até CI verde e configuração legítima de secrets.

## Objetivo

Enviar notificações de início e encerramento de atividades e relatórios de pendências sem versionar credenciais e sem depender de rede durante os testes.

## Arquivos

- `scripts/telegram_activity_reporter.py`;
- `tests/test_telegram_activity_reporter.py`;
- `config/autonomy/telegram_delivery_policy.json`.

## Simulação segura

```bash
python3 scripts/telegram_activity_reporter.py --dry-run activity-started \
  --activity-name "Revisar pendências" \
  --technical-description "Cruzar documentação, código, issues e PRs" \
  --estimated-completion-time "2 horas" \
  --reported-difficulty 4 \
  --initial-progress-percent 0
```

```bash
python3 scripts/telegram_activity_reporter.py --dry-run activity-completed \
  --activity-name "Revisar pendências" \
  --status partial_success \
  --completion-percent 70 \
  --pending-item "Executar CI" \
  --next-step "Atualizar issue"
```

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

Nunca colocar os valores em documentação, argumentos persistidos, commits ou logs.

## Testes

```bash
python3 -m pytest -q tests/test_telegram_activity_reporter.py
```

A cobertura inclui:

- `dry-run` sem credenciais;
- mensagem de início;
- mensagem de conclusão;
- limite de quatro relatórios;
- repetição limitada em falha transitória;
- rejeição de política que permita credenciais no Git.

## Critérios antes do agendamento

1. CI e segurança aprovados no commit atual;
2. secrets legítimos configurados fora do Git;
3. `dry-run` registrado;
4. timeout e concorrência controlados;
5. canal e chat confirmados pelo proprietário;
6. política de retenção de logs definida.

## Decisão de reconstrução

A antiga PR #46 misturava o executor com documentos de governança que já evoluíram na `main`, criando conflito e impedindo o início dos checks. Esta reconstrução preserva somente o núcleo funcional, a política e os testes, sem substituir roadmap, status ou relatórios mais novos.
