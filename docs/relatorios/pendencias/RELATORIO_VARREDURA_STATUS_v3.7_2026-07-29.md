# Relatório de Varredura e Status

**Versão:** 3.7  
**Data e hora:** 29/07/2026 04:40, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/marketplace-checkout-idempotente-2026-07-29`  
**Issues:** `#51`, `#78` e `#79`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Resumo executivo

O ciclo executou primeiro as pendências de integração e segurança:

- PR #74 integrada por Squash and Merge;
- PR #75 encerrada sem merge por escopo divergente;
- PR #76 integrada por Squash and Merge após CI, Security, Compose e A1 Admin verdes;
- PR #77 encerrada sem merge por base ultrapassada e sobreposição com o PR #76;
- issue #79 criada para preservar e reaplicar os ajustes de branding sem excluir ativos às cegas.

Depois da limpeza da fila, a issue #78 e a branch do checkout foram iniciadas.

## 2. Achado principal do checkout

O Marketplace já possui catálogo, feed, promoções, favoritos e carrinho. O carrinho calcula total e disponibilidade a partir dos campos `price_brl` e `stock_quantity` do próprio produto.

O módulo Stock ainda não oferece uma fonte única de inventário nem reservas transacionais. A matriz tipada registra somente suppliers, catalog_products, price_rules, supplier_orders e discount_quotes. O módulo específico expõe apenas conversão de unidades além das rotas genéricas.

Criar uma reserva dentro do Marketplace seria uma duplicação insegura de saldo. Por isso, o checkout completo permanece bloqueado até a fundação transacional do Stock.

## 3. Ações executadas

- issue #78 criada;
- branch `feat/marketplace-checkout-idempotente-2026-07-29` criada sobre `6f76c6359eca268aaafc301a51c0f754be8998c8`;
- `tarefas.md` atualizado para v2.5;
- `modules/marketplace/CHECKOUT_CONTRACT.md` criado na versão 0.1.0;
- máquina de estados, idempotência, snapshot, eventos, observabilidade, rollback e testes definidos;
- feature flag definida como desligada por padrão;
- nenhum pedido, pagamento ou reserva fictícia foi criado;
- Delivery permaneceu bloqueado.

## 4. Tabela de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| PR #74 | Isolar artefato local | Integrada | 3 | 100% | concluído | 6 | 6 | 0 |
| PR #75 | Correção Android contaminada | Encerrada sem merge | 5 | 100% | concluído | 5 | 5 | 0 |
| PR #76 | Correção Android limpa | Integrada | 4 | 100% | concluído | 8 | 8 | 0 |
| PR #77 | Branding e CI sobrepostos | Encerrada e preservada | 4 | 100% | concluído sem merge | 5 | 5 | 0 |
| Issue #79 | Reaplicar branding oficial | Escopo preservado | 4 | 20% | ciclo próprio | 5 | 1 | 4 |
| Contrato checkout | Definir fronteiras transacionais | Versionado v0.1 | 5 | 100% | concluído | 10 | 10 | 0 |
| Stock transacional | Inventário e reservas | Bloqueio confirmado | 5 | 10% | próximo incremento | 8 | 1 | 7 |
| Pedido idempotente | Criar pedido após reserva | Não iniciado | 5 | 0% | posterior | 8 | 0 | 8 |
| Finance | Autorizar pelo ledger | Não iniciado | 5 | 0% | posterior | 8 | 0 | 8 |
| Delivery | Jornada logística | Bloqueado | 5 | 0% | terceira fase | 8 | 0 | 8 |

## 5. Riscos

1. `stock_quantity` no produto não pode ser tratado como saldo transacional.
2. Duas compras concorrentes poderiam gerar estoque negativo sem reserva atômica.
3. Criar pedido antes da reserva pode deixar pedido sem saldo.
4. Criar lançamento fora do ledger pode gerar dupla cobrança.
5. Mocks financeiros não podem ser declarados como liquidação real.
6. Ativos de marca da PR #77 precisam ser reaplicados sem exclusão automática.

## 6. Próxima ação técnica

1. criar entidades tipadas `inventory_items` e `stock_reservations` no Stock;
2. criar migrations reversíveis;
3. implementar store PostgreSQL com bloqueio concorrente;
4. criar reserva, confirmação, liberação e expiração idempotentes;
5. testar banco limpo e concorrência;
6. somente depois conectar o endpoint de checkout e o ledger.

## 7. Estado final

O checkout foi iniciado em nível de contrato, mas não foi declarado funcional. A decisão evita inventar um estoque paralelo e preserva a ordem Marketplace → Stock → Delivery.
