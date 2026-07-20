# Padrão global de UI inspirado na home Brasil Desconto

Data: 2026-07-20
Escopo: `apps/all-in-one-business`

## Decisão mandatória

A tela home pública do Brasil Desconto é a referência visual do ambiente web All-in-One. Todos os módulos devem herdar o mesmo padrão de composição, linguagem, cores, cartões, botões, formulários, painéis e comportamento responsivo.

## Regra de nomenclatura

O fluxo de cadastro deve se chamar somente:

- `Cadastre-se`

Não usar variações como `A um`, `A1`, `Cadastrar empresa` como CTA principal da home ou do menu público. `Cadastrar empresa` pode aparecer apenas como texto descritivo interno quando necessário, mas o botão principal e o item de entrada devem ser `Cadastre-se`.

## Padrão visual aplicado

### Cores

- Verde principal: `#126b45`
- Verde escuro: `#0d5135`
- Verde suave: `#e2f2ea`
- Texto principal: `#17211c`
- Texto secundário: `#536159`
- Fundo: `#f5f7f6`
- Superfície: `#ffffff`

### Estrutura

- Hero verde com borda forte, sombra marcada e anel decorativo suave.
- Cards brancos com borda escura e sombra deslocada.
- Botões fortes, arredondados, com peso visual de ação.
- Formulários com labels visíveis, campos de altura mínima e foco acessível.
- Painéis de métricas com números grandes em verde.
- Layout responsivo em grids que viram coluna no mobile.

### Componentes cobertos

- `.hero`, `.a1-home-hero`, `.a1-module-hero`
- `.btn-primary`, `.btn-secondary`, `.a1-cta`
- `.metric-card`, `.offer-card`, `.audit-panel`
- `.neo-form`, `.neo-brutalism`, `.a1-card`, `.a1-panel`
- `input`, `select`, `textarea`
- `.type-filter`, `.pill`, `.notice`

## Implementação realizada

1. `apps/all-in-one-business/src/index.css`
   - Recebeu tokens globais do padrão Brasil Desconto.
   - Padronizou hero, cards, botões, filtros, formulários, métricas e estados.
   - Criou classes reutilizáveis `a1-*` para módulos novos.

2. `apps/all-in-one-business/src/components/Navigation.tsx`
   - Item de cadastro corrigido para `Cadastre-se`.
   - CTA lateral `Cadastre-se` adicionado abaixo da logomarca.
   - Categorias e títulos revisados para pt-BR com acentuação.
   - Mantém `BrandLogo`, sem alterar a logomarca oficial.

3. `apps/all-in-one-business/src/pages/business/CompaniesForm.tsx`
   - Título principal e botão de envio corrigidos para `Cadastre-se`.
   - Tela aderente ao padrão global por classes `hero`, `a1-module-hero`, `neo-form` e `a1-card`.

## Critérios de aceite

- A home e os módulos usam o mesmo vocabulário visual.
- O CTA principal do cadastro é `Cadastre-se`.
- A logomarca oficial continua protegida e não é alterada.
- O CSS global é aplicado sem exigir reescrever cada página individual neste ciclo.
- Novas telas devem usar as classes `a1-*` e evitar estilos soltos incompatíveis.
