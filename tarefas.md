# Tarefas da IA Desenvolvedora

**Versão:** 1.2  
**Data da entrega:** 26/07/2026  
**Hora da entrega:** 23:06:33  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/pendencias-documentacao-v2-7-telegram-2026-07-26`  
**Commit-base:** `77fa6fab5f1c881ba6289dc288dc64e20421614a`  
**Issue:** `#45`  
**Classificação:** `Pendências > Técnico > Equipe técnica`  
**Destino:** Codex e IAs desenvolvedoras autorizadas

## 1. Objetivo

Executar a versão 2.7 das pendências a partir da documentação consolidada,
regularizar entregas paralelas e concluir a implementação inicial do executor
Telegram sem expor credenciais.

## 2. Fontes de verdade

1. `AGENTS.md`;
2. `docs/Pendências Do desenvolvedor.md`, versão 2.7;
3. `docs/STATUS_ATUAL.md`, versão 1.0;
4. `docs/DOCUMENTATION_INDEX.md`, versão 1.0;
5. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v2.7_2026-07-26.md`;
6. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v2.7_2026-07-26.md`;
7. issue `#45`;
8. PRs `#34`, `#36`, `#37`, `#38` e `#40`;
9. `config/module_catalog.json`;
10. `config/autonomy/telegram_delivery_policy.json`;
11. `scripts/telegram_activity_reporter.py`;
12. `tests/test_telegram_activity_reporter.py`.

## 3. Estado confirmado

- catálogo com 24 módulos ativos;
- Vision fora do catálogo operacional;
- auditor v7 versionado;
- README e Roadmap alinhados nesta branch;
- documentação atual classificada em índice próprio;
- issue `#45` aberta;
- implementação do executor Telegram iniciada.

## 4. Prioridades do ciclo

### Prioridade 1: validar a branch v2.7

```bash
python3 scripts/audit_confirmation_v7.py
python3 scripts/validate_repository.py
python3 -m pytest -q tests/test_telegram_activity_reporter.py
```

Registrar saídas, falhas e versão do Python. Não usar resultados antigos como
evidência do commit atual.

### Prioridade 2: concluir Telegram

- validar `activity-started` em `--dry-run`;
- validar `activity-completed` em `--dry-run`;
- validar `pending-report` para índices 1 a 4;
- confirmar retry e timeout;
- confirmar que token e chat ID não aparecem em logs;
- configurar secrets somente fora do Git;
- criar agenda de quatro relatórios após os testes passarem.

### Prioridade 3: regularizar PRs

- comparar `#34` e `#37` por arquivos e escolher uma fonte de verdade;
- atualizar ou encerrar o PR duplicado;
- atualizar a base dos PRs `#36`, `#38` e `#40`;
- não integrar PR com `mergeable=false`, base antiga ou checks ausentes.

### Prioridade 4: validar artefatos

- gerar e instalar o APK Admin do PR `#36`;
- validar HTTPS, navegação externa e URL do painel;
- gerar o PDV Desktop do PR `#38` em Windows autorizado;
- testar operação offline, backup, restauração e idempotência.

### Prioridade 5: ambiente público

- identificar e remover `tmp-valley` da superfície pública;
- validar domínio, HTTPS e artefato publicado;
- obter URL do API Hub;
- testar `/health` e CORS;
- registrar evidência vinculada ao commit.

### Prioridade 6: encerramento

- atualizar issue `#45`;
- atualizar pendências, relatório, plano e `tarefas.md`;
- abrir ou atualizar Pull Request;
- integrar apenas por Squash and Merge após checks;
- liberar lock multiagente.

## 5. Ciclo de tempo

| Janela | Atividade |
|---|---|
| 0h a 1h | Gates e testes da branch v2.7 |
| 1h a 2h30 | Telegram executável e testes |
| 2h30 a 4h | Triage dos PRs e duplicidade `#34`/`#37` |
| 4h a 5h30 | Ambiente público e API Hub |
| 5h30 a 7h | APK Admin e PDV Desktop |
| 7h a 8h | Evidências, issues e passagem operacional |

Tolerância normal: até 4 horas. Após 12 horas, não iniciar nova frente.

## 6. Critérios de aceite do executor Telegram

1. subcomandos aceitam apenas os campos esperados;
2. política JSON é carregada e validada;
3. `--dry-run` funciona sem token e sem rede;
4. envio real exige `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`;
5. falhas de rede usam retry limitado;
6. mensagens respeitam limite seguro;
7. relatório aceita somente índices 1 a 4;
8. testes unitários não acessam a internet;
9. nenhuma credencial aparece no Git ou nos logs;
10. documentação e issue são atualizadas.

## 7. Riscos

- PRs antigos podem reintroduzir 25 módulos ou Vision ativo;
- `#34` e `#37` podem duplicar centenas de arquivos;
- artefatos podem existir sem homologação;
- agenda Telegram pode falhar repetidamente sem secrets;
- documentos históricos podem ser confundidos com estado atual;
- ambiente público pode apontar para artefato temporário;
- alterações administrativas do repositório dependem de configuração do GitHub.

## 8. Condições de parada

Parar e registrar bloqueio diante de:

- lock de outro agente;
- merge ou rebase em andamento;
- credencial legítima ausente para ação externa;
- risco de sobrescrever trabalho;
- billing, IAM ou aceite jurídico;
- alteração de marca sem autorização;
- conflito de PR sem fonte de verdade definida.

## 9. Entrega obrigatória

A próxima IA deve entregar:

1. resumo simples para o gestor;
2. versão, data e hora;
3. arquivos alterados;
4. testes e comandos executados;
5. resultados, falhas e causas;
6. evidências e artefatos;
7. issues e PRs atualizados;
8. pendências restantes;
9. nova versão deste arquivo;
10. integração por Squash and Merge quando os critérios forem atendidos.

## 10. Histórico

| Versão | Data e hora | Alteração principal |
|---|---|---|
| 1.0 | 26/07/2026 13:49:32 | Diretriz permanente de Estudar, Pesquisa Avançada e versionamento. |
| 1.1 | 26/07/2026 14:01:53 | Primeiro teste completo e ciclo v2.6. |
| 1.2 | 26/07/2026 23:06:33 | Consolidação documental v2.7 e início do executor Telegram. |