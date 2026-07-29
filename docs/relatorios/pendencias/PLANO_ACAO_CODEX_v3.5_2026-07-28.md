# Plano de Ação Codex — A1 Admin

**Versão:** 3.5  
**Data:** 28/07/2026  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/a1-admin-web-mobile-figma-2026-07-28`  
**Issue:** `#68`  
**Público-alvo:** Equipe Técnica

## Objetivo

Concluir, validar e integrar o template unificado A1 Admin Web + Mobile, deixando uma fonte de verdade pronta para o novo projeto Figma e para o APK Android.

## Bloco 1 — fechamento da PR

1. executar `npm ci`, lint, design, build e audit;
2. executar testes, lint e assemble Android;
3. confirmar integridade da marca;
4. analisar qualquer job falho;
5. corrigir a causa na mesma branch;
6. repetir os gates no novo SHA;
7. verificar mergeabilidade e conflitos;
8. verificar threads e reviews;
9. integrar por Squash and Merge;
10. encerrar a issue #68 com evidências.

## Bloco 2 — publicação posterior

1. publicar o shell em domínio administrativo homologado;
2. configurar `A1_ADMIN_URL` no pipeline Android;
3. validar login, sessão, logout e links externos;
4. gerar APK homologado;
5. executar QA em desktop, tablet e Android físico.

## Bloco 3 — Figma

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
