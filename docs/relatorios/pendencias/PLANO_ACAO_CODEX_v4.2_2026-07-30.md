# Plano de Ação Codex v4.2

**Janela:** 8 horas, tolerância operacional máxima de 4 horas
**Data:** 30/07/2026, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/corrigir-pendencias-relacionais-v42-20260730`

## Objetivo e escopo

Consolidar PRs, commits, merges, branches, issues, workflows e alertas de
segurança; corrigir pendências técnicas reproduzíveis sem misturar as oito
evoluções funcionais abertas.

## Fontes de verdade e pré-requisitos

- Git/GitHub (`origin/main`, GraphQL/REST, Actions e Dependabot);
- `config/autonomy/pending_work_priority_policy.json`;
- `modules/shared/domain_rules.py`;
- `docs/Pendências Do desenvolvedor.md`;
- Node/npm, Python `.venv`, Playwright e credenciais GitHub já autenticadas.

## Sequência e prioridades

1. workflows falhos e bloqueados: distinguir falha interna de billing externo;
2. merges, PRs, commits e branches: comparar ancestralidade e PR associada;
3. segurança: fixar dependência vulnerável sem salto major indevido;
4. correção relacional: alinhar UI, API Hub e transições autoritativas;
5. testes: unitários, build e E2E focal;
6. documentação, commit, PR, gates, Squash and Merge e sincronização final.

## Testes e critérios de aceite

- `npm ci --ignore-scripts` e auditoria crítica nos 11 pacotes alterados;
- build do Business;
- testes de segurança do API Hub;
- E2E Business vivo, Health e Mobility sem proxy local;
- scanner de marca, segredos e validadores de repositório;
- PR sem conflito e gates internos verdes no mesmo head SHA.

## Riscos, bloqueios e mitigação

- billing GKE externo: documentar e não falsificar sucesso;
- branches divergentes: preservar todo tip com commit exclusivo;
- React Router RSC: manter dispensa documentada enquanto os apps forem SPAs Vite;
- testes longos: executar grupos focais reproduzíveis e registrar resultados;
- trabalho concorrente: lock multiagente obrigatório até o fim da integração.

## Evidências esperadas e procedimento de entrega

Diff conhecido, logs de testes, inventário v4.2, commit publicado, PR vinculada à
issue #51, checks do head, Squash and Merge e confirmação de igualdade entre
`main`, `origin/main` e commit integrado. Após 12 horas, se a atividade ainda
estiver aberta, atualizar falhas, causas, bloqueios e próximos passos.

## Pendências restantes

As issues #24, #39, #47, #55, #69, #89 e #95 mantêm seus próprios critérios de
aceite. A #51 continua como orquestração. Nenhuma é considerada concluída por
esta correção transversal.
