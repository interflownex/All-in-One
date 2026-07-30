# Contrato de Checkout Marketplace

**Versão:** 0.2.0  
**Issue:** #78  
**Classificação:** Pendências > Técnico > Equipe Técnica  
**Público-alvo:** Equipe Técnica  
**Feature flag:** `MARKETPLACE_CHECKOUT_V1_ENABLED=false` até homologação  
**Vision:** inativo  
**Delivery e Rider:** fora deste incremento

## 1. Objetivo

Confirmar um carrinho autenticado de forma idempotente, revalidando preço,
loja, publicação e disponibilidade diretamente nas fontes autoritativas. A
operação cria pedido pendente, snapshot imutável, reservas Stock, auditoria e
outbox na mesma transação PostgreSQL.

## 2. Endpoint de confirmação

```http
POST /api/v1/marketplace/valley/checkout
X-Actor-User-Id: <uuid>
X-Idempotency-Key: <16..120 caracteres>
X-Correlation-Id: <uuid>
X-Causation-Id: <uuid opcional>
Content-Type: application/json
```

```json
{
  "cart_id": "uuid",
  "wallet_id": "uuid",
  "currency": "BRL",
  "expected_total_brl": "199.90",
  "payment_method": "wallet",
  "reservation_ttl_seconds": 900
}
```

A feature flag desabilitada retorna `503`. A API não inicia pagamento externo,
Delivery ou Rider.

## 3. Regras de validação

- o carrinho precisa estar ativo e pertencer ao ator autenticado;
- o carrinho não pode estar vazio nem conter produtos repetidos;
- a carteira precisa estar ativa e pertencer ao mesmo usuário;
- cada produto precisa existir, estar publicado e não estar excluído;
- a loja precisa estar ativa ou aprovada e não estar excluída;
- o inventário autoritativo precisa existir em `stock.inventory_items`;
- o saldo disponível precisa comportar a quantidade solicitada;
- todos os itens precisam pertencer à mesma loja e empresa nesta versão;
- o preço é relido de `marketplace.products.price_brl`;
- o total é recalculado no servidor em BRL;
- divergência entre total esperado e atual retorna `409`;
- `marketplace.products.stock_quantity` não é usado como saldo autoritativo.

## 4. Idempotência

O escopo da confirmação é `(user_id, X-Idempotency-Key)`.

- mesma chave e mesmo corpo retornam o mesmo checkout;
- mesma chave e corpo diferente retornam `409` e geram auditoria;
- o carrinho muda para `checkout_pending`, impedindo outra confirmação
  concorrente com chave diferente;
- pedido, reserva e resultado financeiro possuem chaves derivadas próprias;
- resultados financeiros são idempotentes por checkout, operação e chave;
- um checkout terminal não cria novo lançamento, cobrança ou baixa Stock.

## 5. Snapshot imutável

`marketplace.checkouts.snapshot` e `marketplace.checkout_items` preservam:

- usuário, empresa, loja, carrinho, pedido e carteira;
- produto, SKU, nome e versão do catálogo;
- inventário e reserva Stock;
- quantidade, preço unitário e subtotal;
- promoção aplicada;
- moeda BRL e total calculado;
- data de criação e versão do snapshot.

Nenhuma transição posterior recalcula ou substitui o snapshot.

## 6. Stock

A confirmação bloqueia as linhas de inventário com `FOR UPDATE`, incrementa
`reserved_quantity` e cria uma reserva para cada item.

Estados:

```text
pending_payment -> approved -> committed
pending_payment -> rejected/cancelled/compensated -> released
pending_payment -> timeout -> expired
```

A quantidade física só é reduzida após resultado financeiro `approved`.
Falha, rejeição, cancelamento ou expiração devolvem o saldo reservado.

## 7. Ledger financeiro

A aprovação cria exatamente um registro em `finance.ledger_entries`:

- moeda `BRL`;
- `entry_type=marketplace_purchase_authorized`;
- `reference_type=marketplace.checkout`;
- referência ao checkout;
- chave idempotente única;
- valor do comprador registrado no ledger;
- metadados com pedido, empresa, correlação e referência do provedor.

Não existe saldo paralelo, atualização direta de saldo ou armazenamento de
dados brutos de cartão.

## 8. Resultado financeiro interno

```http
POST /api/v1/marketplace/valley/checkout/{checkout_id}/payment-result
X-Actor-User-Id: <uuid>
X-Actor-Scopes: marketplace:checkout:payment
X-Idempotency-Key: <16..120 caracteres>
X-Correlation-Id: <uuid>
```

```json
{
  "outcome": "approved|rejected|cancelled|compensated",
  "provider_reference": "referência opcional",
  "reason": "motivo opcional"
}
```

A rota é interna e continua disponível para finalizar operações já iniciadas,
mesmo quando a criação de novos checkouts estiver desligada.

## 9. Consulta e isolamento

```http
GET /api/v1/marketplace/valley/checkout/{checkout_id}
```

O consumidor só lê o próprio checkout. Operadores só podem consultar quando
possuem papel permitido e `X-Business-Id` correspondente à empresa do checkout.

## 10. Expiração

```http
POST /api/v1/marketplace/valley/checkout/expire
X-Actor-Scopes: marketplace:checkout:expire
X-Correlation-Id: <uuid>
```

A rotina usa `FOR UPDATE SKIP LOCKED`, expira reservas vencidas, reativa o
carrinho e registra auditoria e eventos. Não despacha entrega.

## 11. Eventos

```text
marketplace.checkout.started
marketplace.order.created
finance.payment.pending
stock.reservation.created
finance.payment.authorized
finance.payment.failed
finance.payment.cancelled
finance.payment.compensated
stock.reservation.committed
stock.reservation.released
stock.reservation.expired
marketplace.checkout.confirmed
marketplace.checkout.cancelled
marketplace.checkout.expired
```

Os eventos são gravados em `audit.domain_events` no mesmo limite transacional
da alteração de estado e carregam `correlation_id`, `causation_id` e versão de
schema.

## 12. Critérios de aceite

- migration 032 e rollback manual reproduzíveis;
- endpoint de confirmação com chave obrigatória;
- revalidação integral no servidor;
- snapshot imutável;
- total BRL calculado no backend;
- isolamento por usuário e empresa;
- nenhuma duplicidade de pedido, reserva ou ledger;
- concorrência sem estoque negativo;
- commit Stock somente após aprovação;
- release em falha, cancelamento e expiração;
- auditoria e outbox transacionais;
- OpenAPI 0.4.0 atualizado;
- feature flag desligada;
- Delivery, Rider e Vision ausentes;
- CI, Security, Database, OpenAPI e Compose verdes no mesmo SHA;
- integração somente por Squash and Merge com `expected_head_sha`.
