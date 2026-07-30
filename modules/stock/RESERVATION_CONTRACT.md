# Contrato de Inventário e Reservas do Stock

**Versão:** 0.2.1  
**Data e hora:** 30/07/2026 06:10, `America/Sao_Paulo`  
**Status:** implementação concluída na branch e aguardando validação integral dos workflows  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/stock-reservations-foundation-20260730`  
**Commit-base:** `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`  
**Issue:** `#83`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Objetivo

Definir e implementar a fonte única de saldo e o ciclo de reservas necessário ao checkout futuro do Marketplace.

Este contrato não autoriza usar `marketplace.products.stock_quantity` como saldo transacional. A feature flag `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada até que a fundação Stock seja integrada e o checkout seja implementado em atividade separada.

## 2. Estado da implementação

Implementado na branch:

- migration `database/postgres/migrations/027_stock_inventory_reservations.sql`;
- rollback manual `database/postgres/rollbacks/027_stock_inventory_reservations.sql`;
- store transacional `modules/shared/stock_postgres_store.py`;
- endpoints especializados em `modules/stock/main.py`;
- contrato OpenAPI `modules/stock/OPENAPI.yaml` versão `0.3.0`;
- testes estáticos e integração PostgreSQL real;
- gate Database com aplicação em banco limpo e prova de rollback.

A entrega somente será considerada concluída após todos os workflows acionados pelo diff terminarem verdes no mesmo SHA, revisão integral do diff e verificação de segredos.

## 3. Entidades

### `stock.inventory_items`

Responsabilidades:

- armazenar saldo físico e reservado;
- fornecer saldo disponível gerado pelo PostgreSQL;
- isolar inventário por empresa e localização;
- impedir saldo negativo;
- controlar concorrência por bloqueio de linha e versão;
- derivar `active/depleted` no banco conforme a disponibilidade real.

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
available_quantity (gerada)
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

### `stock.stock_reservations`

Responsabilidades:

- reservar saldo para checkout ou pedido;
- impedir consumo concorrente do mesmo saldo;
- expirar e liberar reservas abandonadas;
- confirmar baixa após autorização válida;
- garantir idempotência por usuário e empresa.

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

## 4. Estados e transições

```text
pending -> reserved
pending -> rejected
reserved -> committed
reserved -> released
reserved -> expired
```

Regras:

- nenhuma transição retorna a estado anterior;
- `committed`, `released`, `expired` e `rejected` são terminais;
- repetição da mesma confirmação ou liberação retorna o estado atual;
- uma reserva terminal não altera novamente o inventário;
- confirmação de reserva vencida executa a expiração e não baixa saldo físico.

## 5. Idempotência

A chave é escopada por usuário, empresa e operação.

Mesmo corpo:

- retorna a mesma reserva;
- não aumenta `reserved_quantity` novamente;
- não publica evento duplicado.

Corpo diferente:

- retorna conflito;
- registra auditoria `idempotency_conflict`;
- não modifica a reserva original.

O corpo normalizado gera `request_hash` SHA-256 estável. Valores decimais equivalentes, como `2` e `2.0000`, produzem o mesmo hash.

## 6. Concorrência

A reserva ocorre em uma única transação PostgreSQL:

1. localizar idempotência anterior com bloqueio de linha;
2. localizar o inventário com `FOR UPDATE`;
3. verificar saldo disponível no servidor;
4. atualizar `reserved_quantity` e `version`;
5. criar a reserva;
6. gravar auditoria;
7. gravar evento no outbox;
8. confirmar a transação.

O worker de expiração usa `FOR UPDATE SKIP LOCKED` para permitir processamento concorrente sem duplicação.

É proibido:

- ler e atualizar saldo em transações separadas;
- confiar em saldo enviado pelo cliente;
- calcular disponibilidade somente no Marketplace;
- compensar concorrência apenas em memória;
- criar recurso transacional pelas rotas CRUD genéricas.

## 7. APIs especializadas

### Criar inventário

```http
POST /inventory/items
```

Exige contexto Business ativo e `X-Correlation-Id`.

### Ajustar inventário

```http
PATCH /inventory/items/{inventory_item_id}
```

Exige `expected_version`, justificativa e empresa autenticada.

### Reservar

```http
POST /reservations
```

Entrada mínima:

```json
{
  "user_id": "uuid",
  "company_id": "uuid",
  "inventory_item_id": "uuid",
  "order_id": "uuid",
  "quantity": 2,
  "expires_in_seconds": 900
}
```

Cabeçalhos:

```http
X-Actor-User-Id: <uuid>
X-Idempotency-Key: <string>
X-Correlation-Id: <uuid>
X-Causation-Id: <uuid opcional>
```

O titular pode operar a própria reserva. Operadores só podem atuar quando pertencem à mesma empresa da reserva.

### Confirmar

```http
POST /reservations/{reservation_id}/commit
```

### Liberar

```http
POST /reservations/{reservation_id}/release
```

### Expirar globalmente

```http
POST /reservations/expire?limit=100
```

Exige obrigatoriamente o escopo `stock:reservations:expire`. Um papel operacional isolado não concede permissão global entre empresas.

## 8. Confirmação

A confirmação:

- aceita somente reserva `reserved` e não vencida;
- reduz `physical_quantity` e `reserved_quantity` na mesma transação;
- marca a reserva `committed`;
- publica `stock.reservation.committed`;
- é idempotente quando já confirmada.

## 9. Liberação

A liberação:

- aceita somente reserva `reserved`;
- reduz `reserved_quantity`;
- marca a reserva `released`;
- registra motivo;
- publica `stock.reservation.released`;
- é idempotente quando já liberada.

## 10. Expiração

O worker de expiração:

- seleciona reservas `reserved` com `expires_at <= NOW()`;
- bloqueia reserva e inventário;
- devolve saldo reservado;
- marca `expired`;
- publica `stock.reservation.expired`;
- pode ser executado repetidamente sem duplicar efeito.

## 11. Eventos

- `stock.reservation.created`;
- `stock.reservation.rejected`;
- `stock.reservation.committed`;
- `stock.reservation.released`;
- `stock.reservation.expired`.

Envelope obrigatório:

- `event_id`;
- `occurred_at`;
- `actor_user_id`;
- `user_id`;
- `tenant_id` derivado de `company_id`;
- `aggregate_type`;
- `aggregate_id`;
- `correlation_id`;
- `causation_id`;
- `schema_version`;
- payload minimizado e sanitizado.

## 12. Auditoria

Auditar:

- criação e ajuste do inventário;
- criação e rejeição de reserva;
- confirmação;
- liberação;
- expiração;
- conflito de idempotência.

Não registrar:

- credenciais;
- segredos;
- dados brutos de pagamento;
- payloads excessivos.

## 13. Migration e rollback

Migration:

```text
027_stock_inventory_reservations.sql
```

Rollback:

```text
database/postgres/rollbacks/027_stock_inventory_reservations.sql
```

O rollback remove primeiro reservas, depois inventário e por último a função derivadora. Ele não deve ser executado automaticamente em produção.

## 14. Testes de aceite

Implementados:

- estrutura da migration e ordem do rollback;
- aplicação em PostgreSQL 16 limpo;
- reserva válida;
- saldo insuficiente;
- concorrência sem estoque negativo;
- idempotência com mesmo corpo;
- conflito com corpo diferente;
- confirmação;
- liberação;
- expiração;
- estados terminais idempotentes;
- evento único;
- auditoria;
- isolamento por empresa;
- derivação de disponibilidade no banco;
- rollback reproduzível;
- ausência de checkout, Delivery e Vision no OpenAPI desta fundação.

## 15. Fora do escopo

- ativar checkout;
- criar pedido automaticamente;
- pagamento;
- ledger;
- Delivery;
- atribuição de Rider;
- previsão por IA;
- sincronização com fornecedor real;
- ativação produtiva automática;
- reativação do Vision.
