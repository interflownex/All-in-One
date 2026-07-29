# Plano de Ação Codex — A1 Admin

**Versão:** 3.5  
**Data:** 28/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/a1-admin-web-mobile-figma-2026-07-28`  
**Issue:** `#68`  
**Público-alvo:** Equipe Técnica

## Objetivo

Concluir, validar e integrar o template unificado A1 Admin Web + Mobile, deixando uma fonte de verdade pronta para o novo projeto Figma e para o APK Android.

## Bloco 1 — PR e validação

1. abrir PR da branch para `main`;
2. revisar todos os arquivos alterados;
3. confirmar uso exclusivo da marca canônica;
4. executar o workflow `A1 Admin Template`;
5. analisar logs de qualquer job falho;
6. corrigir a causa na mesma branch;
7. repetir os gates no novo SHA;
8. baixar o artefato `a1-admin-package-lock`;
9. versionar `package-lock.json` e trocar o workflow para `npm ci`;
10. repetir build, lint, audit e Android no SHA final.

## Bloco 2 — revisão e merge

1. verificar mergeabilidade e conflitos;
2. verificar threads e reviews;
3. confirmar que o head não mudou após os testes;
4. marcar PR pronta;
5. integrar por Squash and Merge;
6. comentar e encerrar a issue #68 com evidências;
7. revisar novamente PRs, merges, commits, workflows e issues.

## Bloco 3 — publicação posterior

1. publicar o shell em domínio administrativo homologado;
2. configurar `A1_ADMIN_URL` no pipeline Android;
3. validar login, sessão, logout e links externos;
4. gerar APK homologado;
5. executar QA em desktop, tablet e Android físico.

## Bloco 4 — Figma

1. usar uma sessão Figma autorizada;
2. criar `A1 Admin — Web & Mobile — 2026`;
3. importar `figma.tokens.json`;
4. seguir `figma-screen-manifest.json`;
5. construir componentes e variantes;
6. conectar os fluxos do protótipo;
7. publicar a biblioteca;
8. registrar os links reais no README.

## Testes obrigatórios

```bash
cd apps/all-in-one-admin
npm ci
npm run check
npm audit --omit=dev --audit-level=critical

cd ../../apps/valley-android
./gradlew :admin:testDebugUnitTest :admin:lintDebug :admin:assembleDebug
```

## Critérios de aceite

- web-template verde;
- android-admin verde;
- segurança sem crítico;
- lockfile versionado;
- marca íntegra;
- sem segredo ou dado real;
- PR mesclável;
- merge por Squash and Merge;
- issue #68 encerrada somente após integração.
