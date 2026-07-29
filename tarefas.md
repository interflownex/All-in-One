# Tarefas da IA Desenvolvedora

**Versão:** 2.4  
**Data e hora:** 28/07/2026 23:23:37  
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/auditoria-valley-rider-2026-07-28`  
**Commit local antes da integração:** `4e7b6d9d09d18110c19fd4b75105cfde191ec469`  
**Commit integrado de `origin/main`:** `869371979c7f622a75e7aa022cf8ab44a42f6d62`  
**Pull Requests relacionadas:** `#62`, `#64`, `#65`, `#71`  
**Issue de orquestração:** `#51`

## 1. Objetivo

Concluir a sincronização segura da branch de auditoria do Valley Rider com
`origin/main`, eliminar o conflito recém-detectado em `tarefas.md`, preservar
as entregas posteriores já integradas e manter rastreabilidade para a próxima
etapa.

## 2. Contexto

- a branch local continha as correções de auditoria e estabilização de testes do
  Valley Rider;
- `origin/main` avançou com Rodada 005 do Valley Consumidor, Marketplace Fase 1
  e A1 Admin Web/Mobile;
- o histórico divergiu em 2 commits locais e 4 commits remotos;
- a integração automática conciliou todos os arquivos, exceto `tarefas.md`;
- o conflito documental foi resolvido consolidando as entregas locais e remotas;
- duas alterações locais preexistentes em `.github/skills/` pertencem a outro
  trabalho e devem permanecer fora do commit desta sincronização.

## 3. Escopo

### Incluído

1. integrar `origin/main` sem reset, limpeza destrutiva ou force-push;
2. preservar as correções de auditoria do Valley Rider;
3. preservar Rodada 005, Marketplace Fase 1 e A1 Admin;
4. resolver marcadores de conflito em `tarefas.md`;
5. validar integridade Git, repositório e marca;
6. publicar somente a branch de trabalho e atualizar o pull request aplicável.

### Fora do escopo

- alterar ou remover módulos por associação a trabalhos antigos;
- modificar as duas alterações locais preexistentes em `.github/skills/`;
- fazer push direto em `main`;
- declarar integrações externas homologadas sem evidência no ambiente correto.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. `config/autonomy/multi_agent_sync_policy.json`;
3. `config/autonomy/pending_work_priority_policy.json`;
4. `config/branding/authorized_assets.json`;
5. `config/stitch/screen_manifest.json`;
6. `config/stitch/sync_state.json`;
7. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v3.5_2026-07-28.md`;
8. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v3.5_2026-07-28.md`;
9. este `tarefas.md`;
10. histórico Git local e `origin/main`.

## 5. Pré-requisitos

- executar no worktree correto;
- confirmar ausência de merge ou rebase concorrente;
- buscar referências remotas acessíveis;
- adquirir o lock multiagente após a reconciliação do histórico;
- manter segredos somente em variáveis de ambiente ou cofres externos;
- usar Node, npm, Python e Gradle compatíveis com os lockfiles.

## 6. Sequência de execução e prioridades

### P0 — concluir a sincronização

1. confirmar que não existem marcadores de conflito;
2. adicionar somente os arquivos da integração e `tarefas.md`;
3. preservar fora do stage as alterações preexistentes em `.github/skills/`;
4. concluir o merge com mensagem rastreável em português;
5. executar o preflight e adquirir o lock multiagente;
6. executar as validações obrigatórias;
7. verificar o diff final, os pais do merge e a conectividade Git;
8. publicar a branch de trabalho;
9. atualizar o pull request ou registrar o bloqueio se a operação não estiver
   disponível;
10. liberar o lock multiagente.

### P1 — validar entregas integradas

1. repetir os gates do Valley Rider no SHA final;
2. executar os checks do A1 Admin Web/Mobile;
3. executar os testes do Marketplace e Valley Consumidor;
4. aguardar os gates remotos obrigatórios no mesmo SHA;
5. integrar em `main` exclusivamente por Squash and Merge após aprovação.

## 7. Testes

```bash
rg -n '^(<<<<<<<|=======|>>>>>>>)' --glob '!package-lock.json' .
git diff --check
git fsck --connectivity-only --no-dangling
python3 scripts/check_brand_integrity.py
python3 scripts/validate_repository.py
.venv/bin/pytest -q tests/test_valley_rider_stitch_contract.py
.venv/bin/pytest -q tests/test_marketplace_discovery.py
.venv/bin/pytest -q tests/test_valley_consumer_innovation_round_005.py
```

Quando os ambientes estiverem disponíveis:

```bash
cd apps/valley_rider
npm ci
npm run lint
npm run build

cd ../all-in-one-admin
npm ci
npm run check
npm audit --omit=dev --audit-level=critical

cd ../valley-android
./gradlew :admin:testDebugUnitTest :admin:lintDebug :admin:assembleDebug
```

## 8. Critérios de aceite

- nenhum arquivo permanece em estado não mesclado;
- nenhum marcador de conflito permanece no conteúdo versionado;
- o merge contém os dois históricos esperados;
- as mudanças preexistentes de outro trabalho permanecem intactas e fora do
  commit;
- `git diff --check` e conectividade Git aprovados;
- integridade de marca e validação do repositório aprovadas;
- testes direcionados aprovados;
- branch publicada sem force-push e sem push direto em `main`;
- pull request atualizado com testes e evidências;
- gates remotos verdes no mesmo commit antes do Squash and Merge.

## 9. Riscos

| Risco | Tratamento |
|---|---|
| alterações locais concorrentes | preservar fora do stage e registrar explicitamente |
| novos avanços em `origin/main` | repetir preflight antes do push |
| testes Android demorados ou indisponíveis | reportar como não verificados, nunca como aprovados |
| dependências externas sem credenciais | manter bloqueadas e não simular homologação |
| conflito recorrente em documento central | sempre incrementar versão e consolidar o histórico |

## 10. Bloqueios

- nenhum bloqueio confirmado para concluir a resolução local;
- abertura/atualização de pull request depende de acesso autenticado ao GitHub;
- homologações Mapbox, KYC, PSP, Play Integrity e dispositivo real continuam
  externas ao escopo desta sincronização.

## 11. Evidências esperadas

- saída do preflight e estado do lock;
- `git status --short --branch` sem entradas `UU`;
- busca sem marcadores de conflito;
- saída dos testes e validadores;
- SHA e pais do commit de merge;
- URL/número do pull request e checks vinculados ao SHA;
- confirmação da liberação do lock.

## 12. Pendências restantes

1. concluir e validar o commit de merge;
2. publicar a branch e atualizar o pull request;
3. acompanhar os gates remotos;
4. executar as homologações externas pendentes nos ambientes corretos;
5. revisar a fila de PRs, workflows, branches e issues após esta sincronização.

## 13. Procedimento de entrega

1. revisar o stage e excluir alterações alheias;
2. concluir o merge com mensagem concisa em português;
3. executar testes e registrar resultados reais;
4. publicar somente a branch de trabalho;
5. atualizar o pull request com SHA, testes, riscos e bloqueios;
6. aguardar gates obrigatórios;
7. integrar exclusivamente por Squash and Merge;
8. liberar o lock e registrar o estado final.

## 14. Histórico resumido

| Versão | Data e hora | Alteração |
|---|---|---|
| 1.7 | 27/07/2026 07:12:49 | Fase 0 implementada e regressão final preparada. |
| 1.8 | 28/07/2026 00:52:26 | Rodada 004 do APK Valley registrada. |
| 1.9 | 28/07/2026 08:39:01 | Auditoria do Valley Rider e correção dos gates locais. |
| 2.0 | 28/07/2026 14:51:13 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web/Mobile, Android seguro e pacote Figma. |
| 2.4 | 28/07/2026 23:23:37 | Conflito de sincronização resolvido e históricos consolidados. |
