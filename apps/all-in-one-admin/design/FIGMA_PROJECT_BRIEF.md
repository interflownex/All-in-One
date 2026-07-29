# Projeto Figma — A1 Admin Web + Mobile

**Nome do novo projeto:** `A1 Admin — Web & Mobile — 2026`  
**Classificação:** `Apresentações > Conceitual e Técnico`  
**Público-alvo:** Equipe Técnica e administradores internos  
**Fonte técnica:** `apps/all-in-one-admin`  
**Ativo oficial:** `assets/brand/all-in-one-logo-official.png`

## Objetivo

Criar no Figma uma biblioteca única para o A1 Admin, com paridade entre desktop e mobile. O projeto deve representar uma ferramenta administrativa séria, clara e operacional, sem aparência de landing page e sem métricas fictícias apresentadas como produção.

## Direção visual

- tema escuro azul-marinho profundo;
- superfícies com contraste controlado, bordas discretas e baixa quantidade de sombras;
- verde oficial como cor de ação e confirmação;
- azul, violeta, âmbar e vermelho apenas para semântica;
- tipografia compacta e disciplinada, adequada a tabelas e ferramentas;
- sidebar no web e navegação inferior no mobile;
- tabelas preservadas no desktop, com resumo progressivo no celular;
- cards usados somente para métricas, filas e estados, sem grade decorativa excessiva;
- ícones lineares com stroke consistente;
- movimento curto e funcional;
- compatibilidade com `prefers-reduced-motion`.

## Regras de marca

1. importar a logomarca canônica do repositório;
2. não redesenhar, recolorir, distorcer, recortar ou substituir;
3. usar fundo transparente do ativo original;
4. manter proporção e área de respiro;
5. não criar símbolo alternativo para o A1 Admin.

## Páginas do arquivo

1. `00 — Foundations`
2. `01 — Components`
3. `02 — Web`
4. `03 — Mobile`
5. `04 — Prototype`
6. `05 — Handoff`

## Frames obrigatórios

Use o manifesto `figma-screen-manifest.json`. Crie todos os frames web em `1440 × 1024` e todos os frames mobile em `390 × 844`, com Auto Layout e constraints responsivas.

## Componentes

Crie componentes com propriedades e variantes para:

- App Shell;
- sidebar e bottom navigation;
- topbar;
- botões, campos e busca rápida;
- cards métricos;
- tabela e linha responsiva;
- fila e detalhe de aprovação;
- status, prioridade e saúde;
- alternador de módulo;
- modal e command palette;
- loading, vazio, erro, sucesso, offline e acesso restrito.

## Conteúdo

Todos os textos devem estar em português do Brasil. Dados de tela devem ser marcados como `Protótipo` ou `Demonstração`. Não inventar cobertura produtiva, homologações, usuários reais ou valores financeiros reais.

## Handoff

- aplicar os tokens de `figma.tokens.json` por Tokens Studio ou Variables;
- nomear componentes em português com estrutura `Grupo/Componente/Variante`;
- usar Auto Layout em todos os componentes;
- documentar comportamento responsivo;
- incluir anotações de foco, teclado, contraste e estados;
- conectar o protótipo aos três fluxos do manifesto;
- manter o shell React como referência de implementação.
