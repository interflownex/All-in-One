# A1 Admin — Template Web + Mobile

Shell responsivo do painel administrativo All in One, criado como fonte técnica para o painel web, o APK Admin e o novo projeto Figma.

## Escopo

- dashboard executivo;
- fila e detalhe de aprovações;
- empresas;
- governança de módulos;
- operações;
- segurança;
- relatórios;
- configurações;
- command palette;
- estados de carregamento, vazio, erro e sucesso;
- sidebar desktop e navegação inferior mobile.

Os dados são demonstrativos e aparecem em um ambiente explicitamente marcado como protótipo.

## Marca

A aplicação copia no `prebuild` somente o arquivo canônico:

`assets/brand/all-in-one-logo-official.png`

Nenhuma versão alternativa ou reconstruída é permitida.

## Execução

```bash
cd apps/all-in-one-admin
npm install
npm run check
npm run dev
```

## Projeto Figma

- brief: `design/FIGMA_PROJECT_BRIEF.md`;
- tokens: `design/figma.tokens.json`;
- manifesto: `design/figma-screen-manifest.json`;
- checklist: `design/FIGMA_IMPORT_CHECKLIST.md`.

O Figma deve criar um projeto novo chamado `A1 Admin — Web & Mobile — 2026`, usando esses arquivos como fonte de verdade.

## Integração Android

O módulo `apps/valley-android/admin` continua sendo o instalador Android. A URL do painel passa a ser configurável por propriedade Gradle ou variável de ambiente, permitindo apontar o APK para o novo shell quando ele for publicado.
