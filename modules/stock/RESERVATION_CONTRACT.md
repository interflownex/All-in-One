# Contrato de Inventário e Reservas do Stock

**Versão:** 0.1.0  
**Data e hora:** 29/07/2026 05:15, `America/Sao_Paulo`  
**Status:** fundação em implementação, sem migration criada  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/stock-reservations-foundation-2026-07-29`  
**Commit-base:** `002125a2b46d67f56a2651f797ec0392a06cb4c0`  
**Issue:** `#83`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Objetivo

Definir a fonte única de saldo e o ciclo de reservas necessário ao checkout do Marketplace.

Este contrato não autoriza usar `products.payload.stock_quantity` como saldo transacional e não declara a reserva implementada antes de migration, store e testes de concorrência.

## 2. Entidades

### `stock.inventory_items`

Responsabilidade:

- armazenar o saldo físico autoritativo;
- armazenar o saldo reservado;
- fornecer o saldo disponível;
- isolar inventário por empresa e localização;
- impedir quantidade negativa.

Campos mínimos:

```text
id
user_id
company_id
warehouse_id
product_id
sku
physical_quantity
reserved_quantity
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
```

### `stock.stock_reservations`

Responsabilidade:

- reservar saldo para um checkout ou pedido;
- impedir consumo concorrente do mesmo saldo;
- expirar e liberar reservas abandonadas;
- confirmar baixa após autorização válida;
- garantir idempotência.

Campos mínimos:

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

## 3. Estados e transições

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
- repetição da mesma transição retorna o estado atual sem duplicar efeito;
- uma reserva terminal não altera novamente o inventário.

## 4. Idempotência

A chave é escopada por usuário, empresa e operação.

Mesmo corpo:

- retorna a mesma reserva;
- não aumenta `reserved_quantity` novamente;
- não publica evento duplicado.

Corpo diferente:

- retorna conflito;
- registra auditoria;
- não modifica a reserva original.

O corpo normalizado deve gerar `request_hash` estável.

## 5. Concorrência

A criação da reserva deve ocorrer em uma única transação PostgreSQL:

1. localizar o item com bloqueio de linha;
2. verificar a versão e o saldo disponível;
3. rejeitar quantidade inválida ou insuficiente;
4. atualizar `reserved_quantity`;
5. criar a reserva;
6. gravar auditoria;
7. gravar evento no outbox;
8. confirmar a transação.

É proibido:

- ler saldo e atualizar em transações separadas;
- confiar em saldo enviado pelo cliente;
- calcular disponibilidade somente no Marketplace;
- compensar concorrência apenas em memória.

## 6. Reserva

Entrada mínima:

```json
{
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
X-Correlation-Id: <string>
```

Resultado permitido:

```json
{
  "reservation_id": "uuid",
  "status": "reserved",
  "quantity": 2,
  "expires_at": "timestamp"
}
```

## 7. Confirmação

A confirmação:

- aceita somente reserva `reserved` e não vencida;
- reduz `physical_quantity` e `reserved_quantity` na mesma transação;
- marca a reserva `committed`;
- publica `stock.reservation.committed`;
- é idempotente.

## 8. Liberação

A liberação:

- aceita somente reserva `reserved`;
- reduz `reserved_quantity`;
- marca a reserva `released`;
- registra motivo;
- publica `stock.reservation.released`;
- é idempotente.

## 9. Expiração

O worker de expiração:

- seleciona reservas `reserved` com `expires_at <= NOW()`;
- bloqueia a reserva e o inventário correspondente;
- devolve o saldo reservado;
- marca `expired`;
- publica `stock.reservation.expired`;
- pode ser executado repetidamente sem duplicar efeito.

## 10. Eventos

- `stock.reservation.created`;
- `stock.reservation.rejected`;
- `stock.reservation.committed`;
- `stock.reservation.released`;
- `stock.reservation.expired`.

Envelope mínimo:

- event_id;
- occurred_at;
- actor_user_id;
- user_id;
- company_id;
- aggregate_type;
- aggregate_id;
- correlation_id;
- causation_id;
- schema_version;
- payload minimizado.

## 11. Auditoria

Auditar:

- criação;
- rejeição;
- confirmação;
- liberação;
- expiração;
- conflito de idempotência;
- alteração administrativa de inventário.

Não registrar:

- credenciais;
- segredos;
- dados brutos de pagamento;
- payloads excessivos.

## 12. Migration

Antes de criar a migration:

1. listar o diretório real de migrations;
2. identificar o próximo número livre;
3. abrir a migration física atual do Stock;
4. preservar convenções de UUID, FK, timestamps, metadata e atores;
5. adicionar índices e constraints;
6. comprovar aplicação em banco limpo;
7. não reaplicar DDL de execução única no mesmo banco.

A sequência observada possui migrations até pelo menos `022`, mas o número seguinte não deve ser assumido sem listagem direta do diretório.

## 13. Testes de aceite

- reserva válida;
- saldo insuficiente;
- quantidade zero ou negativa rejeitada;
- concorrência sem estoque negativo;
- idempotência com mesmo corpo;
- conflito com corpo diferente;
- confirmação;
- liberação;
- expiração;
- estados terminais imutáveis;
- evento único;
- auditoria;
- isolamento por empresa;
- migration em banco limpo;
- rollback.

## 14. Fora do escopo

- checkout funcional antes da reserva comprovada;
- pagamento;
- ledger;
- Delivery;
- atribuição de Rider;
- previsão de estoque por IA;
- sincronização com fornecedor real;
- ativação produtiva automática.
