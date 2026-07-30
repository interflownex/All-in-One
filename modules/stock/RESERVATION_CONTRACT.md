# Contrato de Inventário e Reservas do Stock

**Versão:** 0.2.2  
**Data e hora:** 30/07/2026 06:18, `America/Sao_Paulo`  
**Status:** implementação concluída na branch e aguardando gates verdes no mesmo SHA  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/stock-reservations-foundation-20260730`  
**Issue:** `#83`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Objetivo

Criar a fonte única de saldo e o ciclo de reservas necessário ao checkout futuro do Marketplace.

`marketplace.products.stock_quantity` não é saldo transacional. A feature flag `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada. Checkout, pagamento, ledger, Delivery, atribuição de Rider e Vision estão fora desta entrega.

## 2. Fontes autoritativas

- migration: `database/postgres/migrations/031_stock_inventory_reservations.sql`;
- rollback: `database/postgres/rollbacks/031_stock_inventory_reservations.sql`;
- store: `modules/shared/stock_postgres_store.py`;
- API: `modules/stock/main.py`;
- OpenAPI: `modules/stock/OPENAPI.yaml`, versão `0.3.0`;
- integração real: `tests/test_stock_reservations_integration.py`;
- contrato estático: `tests/test_stock_reservation_contract.py`.

A numeração 031 foi definida após a CI comprovar que a `main` já possuía migrations até 030 e que o prefixo 027 já pertencia ao adaptador legado.

## 3. Inventário autoritativo

### `stock.inventory_items`

Campos principais:

```text
id
user_id
company_id
warehouse_id
product_id
sku
physical_quantity
reserved_quantity
available_quantity
version
status
metadata
created_at
updated_at
created_by
updated_by
```

Saldo disponível:

```text
available_quantity = physical_quantity - reserved_quantity
```

Invariantes:

```text
physical_quantity >= 0
reserved_quantity >= 0
reserved_quantity <= physical_quantity
version >= 0
```

Unicidade:

```text
(company_id, warehouse_id, sku)
```

O PostgreSQL deriva `active` ou `depleted` por trigger, conforme a disponibilidade real. Estados administrativos `blocked` e `archived` não são sobrescritos pela derivação.

## 4. Reservas

### `stock.stock_reservations`

Campos principais:

```text
id
user_id
company_id
order_id
inventory_item_id
quantity
status
idempotency_key
request_hash
correlation_id
causation_id
expires_at
committed_at
released_at
release_reason
metadata
created_at
updated_at
created_by
updated_by
```

Estados:

```text
pending -> reserved
pending -> rejected
reserved -> committed
reserved -> released
reserved -> expired
```

`committed`, `released`, `expired` e `rejected` são terminais. Repetir confirmação ou liberação já concluída não duplica o efeito.

## 5. Idempotência

A chave é única por usuário, empresa e operação.

Mesmo corpo:

- retorna a reserva existente;
- não altera saldo novamente;
- não publica evento duplicado.

Corpo diferente:

- retorna conflito;
- registra `idempotency_conflict`;
- preserva a reserva original.

O corpo normalizado gera SHA-256 estável. Quantidades equivalentes, como `2` e `2.0000`, geram o mesmo hash.

## 6. Concorrência

A reserva ocorre em uma única transação:

1. localizar idempotência anterior com bloqueio;
2. localizar inventário com `FOR UPDATE`;
3. calcular disponibilidade no servidor;
4. atualizar saldo reservado e versão;
5. criar a reserva;
6. registrar auditoria;
7. inserir evento no outbox;
8. confirmar a transação.

A expiração em lote usa `FOR UPDATE SKIP LOCKED`.

É proibido:

- confiar em saldo enviado pelo cliente;
- ler e gravar saldo em transações separadas;
- usar estoque paralelo no Marketplace;
- criar essas entidades pelas rotas CRUD genéricas.

## 7. APIs especializadas

```http
POST  /inventory/items
PATCH /inventory/items/{inventory_item_id}
POST  /reservations
POST  /reservations/{reservation_id}/commit
POST  /reservations/{reservation_id}/release
POST  /reservations/expire?limit=100
```

Requisitos:

- autenticação pelo runtime oficial;
- `X-Correlation-Id` obrigatório;
- `X-Idempotency-Key` obrigatório para reserva;
- contexto Business ativo para administração do inventário;
- titular opera a própria reserva;
- operador só atua na empresa autenticada;
- expiração global exige o escopo `stock:reservations:expire`.

A DSN `ALL_IN_ONE_STOCK_POSTGRES_DSN` deve permanecer fora do Git.

## 8. Confirmação, liberação e expiração

Confirmação:

- aceita somente `reserved` não vencida;
- reduz saldo físico e reservado na mesma transação;
- marca `committed`;
- publica `stock.reservation.committed`.

Liberação:

- aceita somente `reserved`;
- devolve saldo reservado;
- marca `released`;
- registra motivo;
- publica `stock.reservation.released`.

Expiração:

- seleciona reservas vencidas;
- bloqueia reserva e inventário;
- devolve saldo;
- marca `expired`;
- publica `stock.reservation.expired`.

## 9. Eventos

```text
stock.reservation.created
stock.reservation.rejected
stock.reservation.committed
stock.reservation.released
stock.reservation.expired
```

O envelope inclui identificadores de evento, ator, usuário, empresa, agregado, correlação, causação, versão e payload minimizado.

## 10. Auditoria

Auditar:

- criação e ajuste do inventário;
- criação e rejeição de reserva;
- confirmação;
- liberação;
- expiração;
- conflito de idempotência.

Não registrar credenciais, segredos, dados brutos de pagamento ou payloads excessivos.

## 11. Migration e rollback

Migration:

```text
031_stock_inventory_reservations.sql
```

Rollback:

```text
database/postgres/rollbacks/031_stock_inventory_reservations.sql
```

O rollback remove primeiro reservas, depois inventário e por último a função derivadora. Ele só é executado automaticamente no banco efêmero do workflow Database, nunca em produção.

## 12. Testes de aceite

- aplicação em PostgreSQL 16 limpo;
- constraints e índices;
- reserva válida;
- saldo insuficiente;
- concorrência sem estoque negativo;
- idempotência com corpo equivalente;
- conflito com corpo diferente;
- confirmação, liberação e expiração;
- estados terminais idempotentes;
- evento único;
- auditoria;
- isolamento por empresa;
- status derivado no banco;
- rollback reproduzível;
- ausência de checkout, Delivery e Vision no OpenAPI.

## 13. Critério de conclusão

A issue #83 só pode ser encerrada quando todos os workflows acionados pelo diff estiverem verdes no mesmo head SHA, o diff estiver revisado, não houver segredos ou conflitos e a PR for integrada por Squash and Merge protegido por `expected_head_sha`.
