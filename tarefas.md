# Tarefas da IA Desenvolvedora

**Versão:** 2.3  
**Data:** 28/07/2026  
**Fuso:** `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/a1-admin-web-mobile-figma-2026-07-28`  
**Commit-base:** `f9fa3dcb81e56f6164e4de8c39c25bc1247bd565`  
**Commit da implementação:** `41efb617c177941dbae598c1eaceefbb70a4dd25`  
**Commit do lockfile:** `2297047a4271005a755997685d9bee630d84c028`  
**Issue:** `#68`  
**Classificação:** `Pendências > Técnico e Conceitual > Equipe Técnica`

## 1. Regra mandatória de prioridade

Antes de qualquer nova evolução, tratar nesta ordem:

1. workflows falhos ou bloqueados;
2. merges pendentes ou conflitantes;
3. pull requests abertas;
4. commits e branches não integrados;
5. issues executáveis;
6. somente depois, nova evolução autorizada.

A política autoritativa permanece em `config/autonomy/pending_work_priority_policy.json` e `AGENTS.md`.

## 2. Objetivo atual

Entregar um template unificado do **A1 Admin** para web e mobile, com fonte visual única, integração segura com o APK Admin e pacote rastreável para criação de um novo projeto no Figma.

## 3. Estado implementado

- shell React/Vite em `apps/all-in-one-admin`;
- sidebar desktop e navegação inferior mobile;
- dashboard, aprovações, empresas, módulos, operações, segurança, relatórios e configurações;
- command palette e interações demonstrativas;
- estados de loading, vazio, erro e sucesso;
- responsividade para desktop, tablet e celular;
- dados identificados como protótipo;
- uso exclusivo da marca canônica `assets/brand/all-in-one-logo-official.png`;
- tokens Figma, manifesto de telas, brief e checklist;
- APK Admin com URL configurável por Gradle ou variável de ambiente;
- política de HTTPS e mesma origem coberta por testes unitários;
- navegação preditiva Android por `OnBackPressedDispatcher`;
- tema compatível com Android 24 e recursos específicos em `values-v27`;
- `package-lock.json` versionado;
- workflow dedicado usando `npm ci` e permissão somente de leitura.

## 4. Fontes de verdade

1. `AGENTS.md`;
2. `config/autonomy/pending_work_priority_policy.json`;
3. `config/branding/authorized_assets.json`;
4. este `tarefas.md`;
5. issue `#68`;
6. `apps/all-in-one-admin/README.md`;
7. `apps/all-in-one-admin/design/FIGMA_PROJECT_BRIEF.md`;
8. `apps/all-in-one-admin/design/figma.tokens.json`;
9. `apps/all-in-one-admin/design/figma-screen-manifest.json`;
10. `apps/valley-android/admin/README.md`;
11. `docs/relatorios/pendencias/RELATORIO_VARREDURA_STATUS_v3.5_2026-07-28.md`;
12. `docs/relatorios/pendencias/PLANO_ACAO_CODEX_v3.5_2026-07-28.md`.

## 5. Validação obrigatória

```bash
cd apps/all-in-one-admin
npm ci
npm run check
npm audit --omit=dev --audit-level=critical

cd ../../apps/valley-android
./gradlew :admin:testDebugUnitTest :admin:lintDebug :admin:assembleDebug
```

Gates esperados:

- A1 Admin Template / web-template;
- A1 Admin Template / android-admin;
- All in One Admin Android APK;
- Continuous Integration;
- Security;
- Docker Compose Health Gate;
- Valley Android Security.

## 6. Sequência imediata

### P0 — fechar esta entrega

1. executar os gates no SHA final;
2. corrigir toda falha reproduzível na branch;
3. revisar diff, marca, segredos e mergeabilidade;
4. verificar threads e mudanças do head;
5. integrar por Squash and Merge;
6. atualizar e encerrar a issue #68 somente após evidências;
7. revisar novamente PRs, merges, commits, workflows e issues.

### P1 — publicação do shell

1. publicar `apps/all-in-one-admin` em domínio administrativo homologado;
2. configurar `A1_ADMIN_URL` no build Android;
3. validar autenticação, sessão, deep links e logout;
4. executar QA visual web/mobile com dados não produtivos;
5. gerar APK homologado apontando para a nova URL.

### P1 — novo projeto Figma

1. criar o arquivo `A1 Admin — Web & Mobile — 2026` em conta Figma autorizada;
2. importar tokens e manifesto;
3. inserir a marca oficial sem modificação;
4. construir pages, componentes, variantes e frames descritos;
5. publicar biblioteca e anexar links ao README.

A criação externa do arquivo Figma depende de uma integração ou sessão Figma autorizada. O repositório já contém todas as entradas técnicas necessárias e não deve receber links fictícios.

## 7. Critérios de aceite

- lint, validação de design e build web verdes;
- auditoria de dependências sem vulnerabilidade crítica;
- testes, lint e APK Android verdes;
- marca oficial preservada;
- URL Android somente HTTPS e mesma origem;
- layouts web/mobile responsivos;
- tokens e manifesto válidos;
- lockfile versionado e `npm ci` comprovado;
- nenhum dado produtivo ou segredo versionado;
- PR mesclável e integrada por Squash and Merge;
- issue #68 atualizada com commit final e evidências.

## 8. Riscos e bloqueios

- o shell é um template e ainda não consome APIs produtivas;
- o domínio definitivo do novo painel ainda precisa ser publicado;
- a criação do arquivo externo no Figma exige acesso autorizado à conta;
- nenhuma dessas limitações autoriza declarar produção ou projeto Figma externo como concluídos.

## 9. Histórico

| Versão | Data | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web + Mobile, Android seguro e pacote pronto para Figma. |
