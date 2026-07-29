# Contrato de Checkout Marketplace

**Versão:** 0.1.0  
**Data:** 29/07/2026  
**Status:** contrato em estudo, feature flag desligada  
**Issue:** `#78`  
**Públicos:** Pessoa Física, Pessoa Jurídica e Equipe Técnica

## 1. Objetivo

Definir a fronteira transacional entre Marketplace, Stock, Orders e Finance sem criar fontes paralelas de saldo, cobrança ou pedido.

Este documento não declara o checkout implementado. Ele bloqueia implementações que ignorem reserva transacional, idempotência, ledger, auditoria ou compensação.

## 2. Feature flag

Nome proposto:

```text
MARKETPLACE_CHECKOUT_V1_ENABLED
```

Regras:

- desligada por padrão;
- nenhuma ativação em produção pela API;
- ativação somente por configuração de ambiente homologada;
- telemetria e rollback obrigatórios;
- desligamento não pode apagar pedidos ou reservas existentes.

## 3. Requisição

Endpoint proposto:

```http
POST /valley/checkout
```

Cabeçalhos obrigatórios:

```http
X-Actor-User-Id: <uuid>
X-Idempotency-Key: <string 16..120>
X-Correlation-Id: <uuid ou identificador rastreável>
```

Corpo mínimo:

```json
{
  "cart_id": "uuid",
  "currency": "BRL",
  "expected_total_brl": "199.90",
  "payment_method": "wallet"
}
```

O cliente não envia preço unitário autoritativo, saldo de estoque, comissão final ou estado de liquidação.

## 4. Resposta inicial

Enquanto o pagamento não estiver homologado, a resposta máxima permitida é um pedido pendente:

```json
{
  "checkout_id": "uuid",
  "order_id": "uuid",
  "status": "pending_stock_reservation",
  "currency": "BRL",
  "total_brl": "199.90",
  "reservation_expires_at": null,
  "payment_status": "not_started"
}
```

É proibido retornar `paid`, `settled` ou `completed` sem evidência do ledger e do provedor homologado.

## 5. Máquina de estados

### Checkout

```text
requested
  -> validating_cart
  -> pending_stock_reservation
  -> stock_reserved
  -> pending_payment
  -> payment_authorized
  -> confirmed
```

Estados de falha e compensação:

```text
rejected
expired
payment_failed
compensating
cancelled
```

### Reserva de Stock

```text
pending
reserved
committed
released
expired
```

Transições devem ser monotônicas, auditadas e idempotentes.

## 6. Snapshot imutável

No início do checkout, o servidor deve criar um snapshot contendo:

- product_id;
- store_id ou company_id;
- SKU;
- nome do produto;
- quantidade;
- preço unitário validado;
- subtotal;
- moeda;
- promoção aplicada e sua versão;
- versão ou timestamp do catálogo;
- referência da reserva de Stock.

O snapshot não pode ser reescrito depois da criação. Alterações de preço posteriores exigem novo checkout.

## 7. Regras de validação

O servidor deve rejeitar:

- carrinho vazio;
- carrinho de outro usuário;
- produto inexistente, privado, inativo ou pausado;
- loja inativa ou não aprovada;
- moeda diferente de BRL neste primeiro contrato;
- preço atual divergente de `expected_total_brl`;
- quantidade maior que o saldo reservável;
- produtos de empresas incompatíveis com a política do pedido;
- chave de idempotência vazia ou reutilizada com corpo diferente.

## 8. Idempotência

A chave deve ser única por ator e operação.

Repetição com o mesmo corpo:

- retorna o mesmo checkout e pedido;
- não cria nova reserva;
- não cria novo lançamento financeiro;
- não publica eventos duplicados.

Repetição com corpo diferente:

- retorna conflito;
- registra auditoria;
- não modifica a operação original.

## 9. Contrato obrigatório do Stock

Antes da ativação do checkout, o Stock deve fornecer:

- `inventory_items` como fonte única de saldo;
- `stock_reservations` com expiração;
- reserva atômica;
- prevenção de estoque negativo;
- confirmação e liberação idempotentes;
- controle de concorrência;
- auditoria;
- outbox.

Campos mínimos da reserva:

- reservation_id;
- user_id;
- company_id;
- order_id;
- product_id ou inventory_item_id;
- quantity;
- status;
- idempotency_key;
- expires_at;
- created_at;
- committed_at ou released_at.

## 10. Contrato financeiro

- valores são lançados somente no ledger;
- dados brutos de cartão não entram no repositório nem nos logs;
- pagamento pendente não reduz saldo definitivo;
- falha financeira libera a reserva;
- autorização duplicada não duplica lançamento;
- compensações são novos lançamentos, nunca edição destrutiva do histórico;
- mocks não podem ser divulgados como liquidação real.

## 11. Eventos mínimos

- `marketplace.checkout.started`;
- `stock.reservation.created`;
- `stock.reservation.rejected`;
- `marketplace.order.created`;
- `finance.payment.pending`;
- `finance.payment.authorized`;
- `finance.payment.failed`;
- `stock.reservation.committed`;
- `stock.reservation.released`;
- `marketplace.checkout.confirmed`;
- `marketplace.checkout.cancelled`.

Todos os eventos devem conter:

- event_id;
- occurred_at;
- actor_user_id;
- user_id;
- company_id quando aplicável;
- entity_id;
- correlation_id;
- causation_id;
- schema_version;
- payload minimizado.

## 12. Observabilidade

Métricas mínimas:

- checkout_started_total;
- checkout_confirmed_total;
- checkout_rejected_total por motivo;
- stock_reservation_latency;
- payment_authorization_latency;
- compensation_total;
- idempotency_replay_total;
- checkout_duration_p95.

Alertas:

- reserva sem pedido;
- pedido sem reserva;
- pagamento autorizado sem confirmação;
- reserva vencida ainda ativa;
- duplicidade de idempotência com corpo diferente;
- crescimento de compensações.

## 13. Rollback

O rollback da feature flag:

1. bloqueia novos checkouts;
2. preserva consultas de pedidos existentes;
3. permite finalizar ou compensar operações iniciadas;
4. libera reservas que não puderem ser concluídas;
5. não apaga auditoria, ledger ou outbox.

## 14. Testes de aceite

- mesma chave e mesmo corpo retornam o mesmo resultado;
- mesma chave e corpo diferente retornam conflito;
- duas compras concorrentes não tornam o estoque negativo;
- preço divergente bloqueia a confirmação;
- item indisponível bloqueia a reserva;
- reserva expirada libera saldo;
- falha financeira compensa a reserva;
- evento não é publicado duas vezes;
- pedido, reserva e ledger compartilham correlation_id;
- isolamento por usuário e empresa;
- migrations reversíveis em banco limpo;
- feature flag desligada por padrão.

## 15. Fora do escopo

- cálculo e despacho de Delivery;
- atribuição de Rider;
- parcelamento;
- múltiplas moedas;
- split produtivo de PSP sem homologação;
- dados de cartão;
- ativação automática em produção.
