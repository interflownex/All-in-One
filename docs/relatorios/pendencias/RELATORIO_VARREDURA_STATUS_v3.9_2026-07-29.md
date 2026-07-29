# Relatório de Varredura e Status

**Versão:** 3.9  
**Data e hora:** 29/07/2026 05:15, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/stock-reservations-foundation-2026-07-29`  
**Commit-base:** `002125a2b46d67f56a2651f797ec0392a06cb4c0`  
**Issues:** `#51`, `#78` e `#83`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Resumo executivo

O contrato de checkout do Marketplace foi integrado pelo PR #82 no commit `002125a2b46d67f56a2651f797ec0392a06cb4c0`, após CI, Security, Docker Compose e A1 Admin verdes no mesmo head.

A implementação funcional do checkout permanece corretamente bloqueada porque o Stock ainda não possui inventário e reservas transacionais. A issue #83 e a branch de fundação foram abertas para tratar essa dependência.

## 2. Achados

- Marketplace já possui catálogo, busca, feed, promoção, favoritos e carrinho;
- o carrinho usa `price_brl` e `stock_quantity` do payload do produto;
- `stock_quantity` não é uma fonte transacional de saldo;
- o store PostgreSQL do Stock reconhece apenas suppliers, catalog_products, price_rules, supplier_orders e discount_quotes;
- o módulo Stock específico possui conversão de unidades, mas não possui reserva atômica;
- as migrations ficam em `database/postgres/migrations`;
- a sequência observada possui arquivos até pelo menos `022`;
- a listagem integral do diretório ainda deve ser feita antes de numerar a nova migration.

## 3. Ações executadas

- issue #83 criada;
- branch `feat/stock-reservations-foundation-2026-07-29` criada;
- `tarefas.md` atualizado para v2.8;
- contrato de reservas do Stock v0.1.0 criado;
- estados, idempotência, concorrência, expiração, eventos, auditoria e testes definidos;
- nenhum SQL foi criado com numeração presumida;
- nenhum estoque paralelo foi criado no Marketplace;
- Delivery permaneceu bloqueado;
- Vision permaneceu excluído.

## 4. Tabela de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Contrato checkout | Fronteira Marketplace, Stock e Finance | Integrado pelo PR #82 | 5 | 100% | concluído | 10 | 10 | 0 |
| Issue #83 | Abrir fundação Stock | Concluído | 2 | 100% | concluído | 3 | 3 | 0 |
| Contrato Stock | Definir inventário e reservas | Versionado v0.1 | 5 | 100% | concluído | 12 | 12 | 0 |
| Numeração migration | Identificar próximo número livre | Pendente de listagem direta | 3 | 40% | 30min | 5 | 2 | 3 |
| Migration Stock | Criar tabelas e constraints | Não iniciada | 5 | 0% | 1h30 | 8 | 0 | 8 |
| Store transacional | Reserva e concorrência | Não iniciado | 5 | 0% | 2h | 10 | 0 | 10 |
| Testes PostgreSQL | Concorrência e idempotência | Não iniciados | 5 | 0% | 2h | 12 | 0 | 12 |
| Checkout funcional | Conectar pedido e ledger | Bloqueado | 5 | 25% | após Stock | 8 | 2 | 6 |
| Delivery | Jornada logística | Bloqueado | 5 | 0% | terceira fase | 8 | 0 | 8 |

## 5. Riscos

1. adivinhar a numeração da migration pode quebrar a ordem determinística;
2. usar `stock_quantity` como saldo autoritativo pode gerar estoque negativo;
3. reservar sem bloqueio de linha cria corrida concorrente;
4. confirmar e liberar sem idempotência duplica efeitos;
5. gravar evento fora da transação pode produzir estado sem outbox;
6. conectar pagamento antes da reserva pode deixar pedido sem lastro.

## 6. Próxima ação

1. listar diretamente `database/postgres/migrations`;
2. confirmar o próximo número livre;
3. abrir a migration física atual do Stock;
4. criar migration reversível;
5. atualizar matriz tipada e store;
6. implementar operações transacionais;
7. testar em banco limpo e concorrente;
8. somente depois conectar checkout, Orders e ledger.

## 7. Estado final

A implementação foi iniciada em nível de issue, branch, tarefas e contrato técnico. O SQL e o store não foram fabricados sem confirmação da sequência física de migrations.
