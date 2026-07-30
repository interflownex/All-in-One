# Relatório de Varredura de Pendências v4.1

**Data e hora:** 30/07/2026 17:19:59, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/orquestrar-pendencias-reais-20260730`
**Commit-base:** `d3b3ef594b1e14347fca785a800980e2f7d39c01`
**Issue de orquestração:** `#51`

## Resultado executivo

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Workflows | CI, Security, Compose, marca e Git Sync verdes; GKE bloqueado por billing | Aguardar habilitação administrativa do billing | 2 | 90% | externo | 10 | 9 | 1 |
| PRs e merges | Nenhuma PR aberta ou merge parcial | Monitoramento | 1 | 100% | concluído | 4 | 4 | 0 |
| Governança de merge | Somente Squash habilitado; merge/rebase/auto-merge desativados | Confirmado via API | 2 | 100% | concluído | 5 | 5 | 0 |
| Branches concluídas | 84 refs removidas com prova de merge ou ancestralidade | Concluído | 3 | 100% | concluído | 84 | 84 | 0 |
| Branches divergentes | Sete backups e 22 refs sem PR contêm commits únicos | Auditoria individual preservada | 4 | 25% | 4 h | 29 | 0 | 29 |
| Dependabot | Alertas npm/Maven reconciliados | Confirmado via API | 2 | 100% | concluído | 83 | 83 | 0 |
| Issues abertas | Oito issues classificadas por dependência e execução | Atualizar evidências na issue #51 | 3 | 70% | 2 h | 8 | 0 | 8 |
| Validação raiz | Contratos legados reconciliados sem supressão | Gate e 982 testes não E2E aprovados | 3 | 100% | concluído | 6 | 6 | 0 |
| E2E Playwright | Primeiros testes do bloco E2E excederam dez minutos e bloquearam teardown | Diagnosticar fixture/browser | 4 | 20% | 2 h | 5 | 1 | 4 |
| Documentação | Pendências, relatório, plano e tarefas sincronizados | PR e gates | 2 | 80% | 1 h | 5 | 4 | 1 |

## Relações e coerência

1. `#51` é a issue-mãe da sequência Marketplace → Stock → Finance → Delivery.
2. `#95` bloqueia ativação financeira, Delivery e Rider por depender de PSP,
   sandbox, credenciais e decisão comercial.
3. `#69` permanece bloqueada pela ausência da fonte funcional reproduzível;
   a branch preservada `codex/rodada-002-decisoes-funcional-2026-07-28` deve
   ser auditada antes de reafirmar definitivamente a ausência.
4. `#89` permanece bloqueada pela exportação da fonte produtiva AppDeploy v9.
5. `#24` possui backend parcial de promoção, mas não satisfaz modal funcional,
   frequência, telemetria, E2E e evidência Stitch; permanece executável.
6. `#47` possui fundação documental integrada, mas não satisfaz o critério
   funcional Android/Wear OS; permanece P0 executável.
7. `#39` e `#55` são escopos agregadores; devem ser decompostos e vinculados,
   sem duplicar `#24`, `#47`, `#69` ou `#95`.

## Evidências

- `gh pr list --state open`: zero;
- Dependabot aberto: zero;
- workflow atual de Security: sucesso;
- workflow atual de CI: sucesso;
- workflow atual de marca: sucesso;
- deploy GKE: WIF aprovado e API recusada por billing desabilitado;
- configuração GitHub: squash `true`, merge `false`, rebase `false`,
  auto-merge `false`, delete branch `true`;
- conectividade Git: `git fsck --connectivity-only --no-dangling` aprovado;
- árvore local inicialmente limpa e alinhada a `origin/main`.
- `validate_repository.py` e `validate_repository_compat.py`: aprovados sem
  exceções suprimidas;
- 31 testes focados: aprovados;
- suíte não E2E: 982 aprovados, 85 ignorados e um aviso;
- suíte integral: interrompida após mais de dez minutos no teardown Playwright,
  com erros/falhas no início do bloco `tests/e2e`; não conta como aprovação;
- integridade de marca, compilação Python, `git diff --check` e `git fsck`:
  aprovados.

## Riscos e bloqueios

- habilitar billing é decisão administrativa externa e pode gerar custo;
- nenhuma das 29 branches divergentes preservadas pode ser removida até
  inventariar seus commits únicos e confirmar substituição ou arquivamento;
- a `main` ainda não possui proteção administrativa obrigatória configurada;
- PSP/AppDeploy/fontes externas exigem autoridade ou dados que não estão no Git.
- a suíte E2E Playwright ainda exige diagnóstico isolado da fixture e do
  teardown; nenhum gate foi enfraquecido ou ocultado.

O inventário exato de refs e SHAs está em
`INVENTARIO_BRANCHES_DIVERGENTES_v4.1_2026-07-30.md`.
