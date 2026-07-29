# Relatório de Varredura e Status

**Versão:** 3.8  
**Data e hora:** 29/07/2026 04:54, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/marketplace-checkout-contract-v1-2026-07-29`  
**Commit-base:** `438d64f46ef341f6a3559dbcb6642cd950ba7291`  
**Issues:** `#51` e `#78`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, Equipe Técnica e gestão

## 1. Resumo executivo

O ciclo de pendências foi regularizado antes da continuidade funcional:

- PR #74 integrada por Squash and Merge;
- PR #75 encerrada sem merge por escopo divergente;
- PR #76 integrada com correção Android mínima e gates verdes;
- PR #77 encerrada sem merge por sobreposição e base ultrapassada;
- PR #80 integrou de forma limpa os ativos oficiais e a correção do scanner de branding;
- PR #81 teve todos os gates verdes, mas foi encerrada sem merge porque a `main` avançou e `tarefas.md` entrou em conflito com o PR #80.

O contrato de checkout foi reconstruído sobre a `main` atual, sem sobrescrever o branding ou a documentação integrada pelo PR #80.

## 2. Estado real do Marketplace

O PR #65 já entregou:

- catálogo público;
- busca, filtros e paginação;
- geolocalização e distância;
- feed vertical;
- promoção do dia;
- favoritos;
- carrinho isolado por usuário.

O carrinho ainda calcula preço e disponibilidade usando `products.payload.price_brl` e `products.payload.stock_quantity`.

## 3. Bloqueio estrutural confirmado

O módulo Stock não possui atualmente entidades tipadas para inventário e reserva transacional. As entidades existentes são:

- suppliers;
- catalog_products;
- price_rules;
- supplier_orders;
- discount_quotes.

Criar `stock_quantity` ou uma reserva dentro do Marketplace produziria uma segunda fonte de saldo, sem concorrência segura e com risco de estoque negativo.

Por isso, o checkout completo não foi declarado implementado.

## 4. Entregas desta rodada

- issue #78 mantida como frente oficial do checkout;
- `modules/marketplace/CHECKOUT_CONTRACT.md` versionado em 0.1.0;
- feature flag de checkout definida como desligada por padrão;
- máquina de estados definida;
- snapshot imutável definido;
- idempotência definida;
- contrato obrigatório de Stock definido;
- ledger e compensações definidos;
- eventos, telemetria, alertas e rollback definidos;
- `tarefas.md` preparado para v2.7;
- plano de ação v3.8 preparado;
- nenhuma reserva, cobrança ou liquidação fictícia criada;
- Delivery permaneceu bloqueado;
- Vision permaneceu excluído.

## 5. Tabela de acompanhamento

| Nome da atividade | Descrição | Passo sendo executado | Dificuldade [1 a 5] | % concluído | Tempo previsto | Etapas [Total] | Concluídas [X] | Pendentes [Y] |
|---|---|---|---:|---:|---|---:|---:|---:|
| Branding oficial | Restaurar ativos e scanner | Integrado pelo PR #80 | 4 | 100% | concluído | 8 | 8 | 0 |
| PR #81 | Contrato sobre base anterior | Encerrada e substituída | 3 | 100% | concluído sem merge | 5 | 5 | 0 |
| Contrato checkout | Definir fronteiras transacionais | Reaplicado na main atual | 5 | 100% | concluído | 10 | 10 | 0 |
| Stock transacional | Criar inventário e reservas | Próximo incremento | 5 | 10% | ciclo seguinte | 8 | 1 | 7 |
| Checkout idempotente | Conectar carrinho, reserva e pedido | Bloqueado pelo Stock | 5 | 25% | após Stock | 8 | 2 | 6 |
| Finance e Wallet | Autorizar pelo ledger | Contrato definido | 5 | 15% | posterior | 7 | 1 | 6 |
| Delivery | Jornada logística | Bloqueado | 5 | 0% | terceira fase | 8 | 0 | 8 |
| Governança de merge | Permitir somente squash | Configuração administrativa pendente | 4 | 55% | externo | 4 | 2 | 2 |

## 6. Riscos

1. `stock_quantity` do produto não é saldo transacional.
2. Compras concorrentes podem gerar estoque negativo sem reserva atômica.
3. Pedido criado antes da reserva pode ficar sem lastro.
4. Valor lançado fora do ledger pode gerar dupla cobrança.
5. Mock financeiro pode ser confundido com liquidação real.
6. Integração fora da ordem pode iniciar Delivery prematuramente.
7. Métodos de merge proibidos continuam habilitados administrativamente.

## 7. Próxima ação técnica

1. adicionar `inventory_items` e `stock_reservations` à matriz tipada do Stock;
2. criar migrations reversíveis;
3. implementar store PostgreSQL transacional;
4. bloquear a linha de inventário durante a reserva;
5. criar expiração, confirmação e liberação idempotentes;
6. publicar eventos por outbox;
7. testar concorrência e banco limpo;
8. somente depois implementar o endpoint de checkout e sua integração com Orders e ledger.

## 8. Estado final

O checkout está concluído em nível de contrato e governança, mas permanece funcionalmente incompleto. Essa classificação é intencional e evita a construção de um estoque paralelo inseguro.
