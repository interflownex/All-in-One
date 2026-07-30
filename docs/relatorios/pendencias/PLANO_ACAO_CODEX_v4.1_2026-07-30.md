# Plano de Ação Codex v4.1

**Janela:** 8 horas, tolerância operacional de até 4 horas
**Data:** 30/07/2026
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/orquestrar-pendencias-reais-20260730`

## Objetivo

Eliminar pendências de integração e transformar bloqueios remanescentes em
itens relacionais, testáveis e com fonte de verdade explícita.

## Sequência obrigatória

1. validar a PR deste relatório e integrar somente com gates verdes;
2. atualizar a issue `#51` com o resultado da varredura v4.1;
3. auditar as 29 branches preservadas por SHA, commits únicos, arquivos e issue;
4. reconciliar as expectativas legadas de `validate_repository.py` com os
   contratos autoritativos atuais, sem enfraquecer os gates;
5. criar tags de arquivo antes de remover qualquer branch sem PR;
6. manter `#95` bloqueada até PSP/sandbox/segredos legítimos;
7. manter `#69` e `#89` bloqueadas até as respectivas fontes existirem;
8. decompor `#39` e `#55`, absorvendo duplicações em `#24` e `#47`;
9. executar `#47` antes de evolução não crítica, por classificação P0;
10. executar `#24` com Stitch canônico, frontend, telemetria e E2E reais;
11. só liberar Delivery após o aceite integral da `#95`.

## Fontes de verdade

- `config/autonomy/pending_work_priority_policy.json`;
- `config/autonomy/multi_agent_sync_policy.json`;
- `docs/Pendências Do desenvolvedor.md`;
- `tarefas.md`;
- issues `#24`, `#39`, `#47`, `#51`, `#55`, `#69`, `#89`, `#95`;
- GitHub Actions e API do repositório;
- `config/stitch/screen_manifest.json` e `config/stitch/sync_state.json`.

## Testes e critérios de aceite

- `git diff --check`;
- `git fsck --connectivity-only --no-dangling`;
- validadores raiz afetados pelo diff;
- suíte não E2E integral;
- testes E2E isolados com limite explícito e teardown reproduzível;
- ausência de segredo no diff;
- PR sem conflito e sem conversa pendente;
- todos os gates obrigatórios verdes no mesmo head SHA;
- Squash and Merge com SHA esperado;
- `main` local e remota idênticas após integração;
- documentos e issue `#51` com commit de integração registrado.

## Bloqueios

- billing GCP desabilitado;
- PSP e credenciais de sandbox ausentes;
- fonte AppDeploy v9 não exportada;
- fonte funcional da Rodada 002 ausente;
- 29 branches com commits únicos ainda não classificados individualmente.
- teardown da suíte E2E Playwright excede o tempo operacional e precisa ser
  diagnosticado sem bloquear a evidência dos 982 testes não E2E aprovados.

## Evidências esperadas

- URL da PR e commit de merge;
- execução dos gates;
- tabela branch → SHA → commits únicos → decisão;
- comentários de classificação nas oito issues;
- resultado do workflow GKE após eventual habilitação de billing.

## Procedimento de entrega

Commit em português, push apenas da branch de trabalho, PR para `main`, revisão
do diff completo, verificação de segredos e Squash and Merge somente com gates
verdes. Após 12 horas, atualizar este plano com concluídos, falhas, causas,
bloqueios, evidências e próximos passos.
