# Plano de Ação Estruturado para o Codex

**Versão:** 3.1
**Data e hora:** 28/07/2026 08:39:01
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/auditoria-valley-rider-2026-07-28`
**Commit-base:** `3834bec6383edd6da08e9fdcf3d74a0de1589df2`
**Issue:** `#51`
**Janela:** 8 horas, com tolerância operacional de até 4 horas

## Missão

Entregar a correção reproduzível dos gates locais do Valley Rider e preparar a homologação completa sem mascarar dependências externas.

## Plano de 8 horas

| Janela | Prioridade | Atividade | Saída |
|---|---|---|---|
| 0–1 h | P0 | Reproduzir lint, build e testes | diagnóstico com comandos e erros |
| 1–3 h | P0 | Corrigir React, GPS e SHA-256 | lint e build verdes |
| 3–4 h | P0 | Testes Stitch, marca e repositório | evidência local consolidada |
| 4–5 h | P1 | QA desktop/mobile no navegador integrado | DOM, console, interação e screenshots |
| 5–6 h | P0 | Atualizar pendências, relatórios e `tarefas.md` | documentação v3.1/v1.9 |
| 6–7 h | P0 | Revisar diff, segredos e sincronização | commit seguro e branch publicada |
| 7–8 h | P0 | Abrir PR, vincular issue e acompanhar gates | PR com CI, Security e Compose |

## Tolerância de até 4 horas

1. recuperar a disponibilidade do navegador integrado e repetir QA;
2. corrigir somente falhas reproduzíveis dos gates do novo SHA;
3. revisar vulnerabilidades npm de desenvolvimento;
4. atualizar PR e issue sem criar commit enquanto o SHA estiver em validação.

## Testes e critérios

Executar exatamente os testes definidos em `tarefas.md` v1.9. A conclusão exige:

- lint, build, contrato Stitch, marca e repositório aprovados;
- ausência de segredos;
- prova renderizada ou bloqueio objetivo registrado;
- commit e PR;
- gates verdes no mesmo SHA;
- issue `#51` atualizada;
- integração exclusivamente por Squash and Merge.

## Após 12 horas

Se a atividade ultrapassar 12 horas, atualizar `docs/Pendências Do desenvolvedor.md`, este plano e o relatório v3.1 com:

- tarefas concluídas;
- falhas e causas;
- bloqueios e responsáveis;
- evidências por ambiente;
- novo prazo;
- próximos passos e decisão de entrega.
