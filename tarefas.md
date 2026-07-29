# Tarefas da IA Desenvolvedora

**Versão:** 2.5
**Data e hora:** 29/07/2026 03:56:22
**Fuso horário:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/auditoria-valley-rider-2026-07-28`  
**Commit local antes da integração:** `c11559c7990072f53dbb1dffecfe36455dcb425a`
**Commit integrado de `origin/main`:** `77dd7791ea8bc649a01a3f1d534b609fdd479a34`
**Pull Requests relacionadas:** `#62`, `#64`, `#65`, `#71`, `#72`
**Issue de orquestração:** `#51`

## 1. Objetivo

Concluir a integração segura da correção do timeout persistente do Gradle Server
no VS Code, preservar as configurações locais da branch e deixar a validação
Android independente do transporte JSON-RPC instável.

## 2. Contexto

- o erro observado registrou timeout após 30 segundos e conexão tardia do
  Gradle Server no mesmo task pipe;
- o PR `#72` corrigiu a causa em `origin/main` no commit `77dd779`;
- a solução desativa o build server JSON-RPC automático, mantém a importação
  oficial pelo wrapper e adiciona tarefas Gradle multiplataforma;
- a integração encontrou conflitos apenas aditivos em `.vscode/settings.json`
  e `all-in-one.code-workspace`;
- as opções locais de análise Python e busca Java foram preservadas junto com
  todas as proteções do Gradle;
- o teste contratual direcionado foi aprovado no ambiente Python do projeto.

## 3. Escopo

### Incluído

1. integrar o commit `77dd779` sem reset, limpeza destrutiva ou force-push;
2. preservar as configurações locais não conflitantes;
3. resolver os dois arquivos não mesclados;
4. validar JSON e `tests/test_gradle_vscode_contract.py`;
5. validar o wrapper Gradle sem depender do servidor JSON-RPC;
6. publicar somente a branch de trabalho e atualizar o pull request aplicável.

### Fora do escopo

- alterar ou remover módulos por associação a trabalhos antigos;
- modificar as duas alterações locais preexistentes em `.github/skills/`;
- fazer push direto em `main`;
- encerrar à força processos Gradle pertencentes a outro agente;
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
.venv/bin/pytest -q tests/test_gradle_vscode_contract.py
cd apps/valley-android && ./gradlew --version --no-daemon
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
- `java.gradle.buildServer.enabled` permanece `off` nas duas configurações;
- wrapper Gradle responde sem iniciar o servidor JSON-RPC do VS Code;
- branch publicada sem force-push e sem push direto em `main`;
- pull request atualizado com testes e evidências;
- gates remotos verdes no mesmo commit antes do Squash and Merge.

## 9. Riscos

| Risco | Tratamento |
|---|---|
| alterações locais concorrentes | preservar fora do stage e registrar explicitamente |
| novos avanços em `origin/main` | repetir preflight antes do push |
| testes Android demorados ou indisponíveis | reportar como não verificados, nunca como aprovados |
| daemon Gradle concorrente | usar `--no-daemon`; não encerrar processo alheio sem validar propriedade |
| dependências externas sem credenciais | manter bloqueadas e não simular homologação |
| conflito recorrente em documento central | sempre incrementar versão e consolidar o histórico |

## 10. Bloqueios

- o reload efetivo da janela do VS Code depende da ação no cliente gráfico;
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
2. recarregar a janela do VS Code para aplicar a configuração efetiva;
3. confirmar que não surge novo processo `gradle-server` automático;
4. publicar a branch e atualizar o pull request;
5. acompanhar os gates remotos e as homologações externas pendentes.

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
| 2.5 | 29/07/2026 03:56:22 | Correção do timeout do Gradle Server integrada do PR #72 e contrato direcionado validado. |
