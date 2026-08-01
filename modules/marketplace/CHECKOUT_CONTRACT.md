# Contrato de Checkout Marketplace

**Versão:** 0.2.0  
**Data e hora:** 30/07/2026 07:19, `America/Sao_Paulo`  
**Status:** implementação presente na branch e aguardando validação integral  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/marketplace-checkout-idempotent-20260730`  
**Issue:** `#78`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Públicos:** Pessoa Física, Pessoa Jurídica e Equipe Técnica

## 1. Objetivo

Implementar o checkout idempotente do Marketplace sobre a fundação transacional Stock integrada pela PR #92, sem criar fontes paralelas de saldo, pedido ou cobrança.

A ordem funcional continua:

```text
Marketplace -> Stock -> Finance/Wallet -> Delivery
```

A presente etapa termina em pedido pago por Wallet interna e valor retido em escrow. Não inicia Delivery, não atribui Rider e não liquida o valor ao lojista.

## 2. Feature flag

```text
MARKETPLACE_CHECKOUT_V1_ENABLED
```

Regras:

- desligada por padrão;
- bloqueia somente a criação de novos checkouts;
- consulta, confirmação e compensação de operações já iniciadas continuam disponíveis;
- não pode ser ativada em produção por endpoint;
- exige DSN `ALL_IN_ONE_MARKETPLACE_POSTGRES_DSN` fora do Git;
- desligamento não apaga pedidos, reservas, auditoria, ledger ou outbox.

## 3. Persistência

Migration:

```text
database/postgres/migrations/032_marketplace_checkout_attempts.sql
database/postgres/migrations/033_marketplace_checkout_mercado_pago.sql
```

Rollback manual:

```text
database/postgres/rollbacks/032_marketplace_checkout_attempts.sql
```

Tabela especializada:

```text
marketplace.checkout_attempts
```

Responsabilidades:

- preservar chave e hash idempotentes;
- vincular carrinho, loja, empresa, pedido e escrow;
- armazenar snapshot imutável do checkout;
- registrar referências das reservas Stock;
- manter correlation_id e causation_id;
- controlar estados monotônicos;
- preservar operação terminal;
- permitir compensação sem apagar histórico.

## 4. APIs

### Criar checkout e reservar Stock

```http
POST /valley/checkout
```

Cabeçalhos obrigatórios:

```http
X-Actor-User-Id: <uuid>
X-Idempotency-Key: <16..160 caracteres>
X-Correlation-Id: <uuid>
X-Causation-Id: <uuid opcional>
```

Corpo:

```json
{
  "cart_id": "uuid",
  "currency": "BRL",
  "expected_total_brl": "199.90",
  "payment_method": "mercado_pago"
}
```

Para Wallet, mantenha `payment_method: "wallet"`. Para Mercado Pago, crie a
preferência server-side em:

```http
POST /valley/checkout/{checkout_id}/mercadopago/preference
```

O endpoint devolve `init_point`/`sandbox_init_point` sem expor o access token.
O ambiente exige `MERCADO_PAGO_ACCESS_TOKEN`,
`MERCADO_PAGO_WEBHOOK_SECRET` e `MERCADO_PAGO_NOTIFICATION_URL` HTTPS.

A criação:

1. exige a feature flag ligada;
2. bloqueia o carrinho do consumidor;
3. rejeita carrinho vazio ou de outro usuário;
4. revalida produto, loja, preço e moeda;
5. aceita uma única loja e empresa por checkout nesta versão;
6. usa `stock.inventory_items` como saldo autoritativo;
7. bloqueia cada inventário com `FOR UPDATE`;
8. cria snapshot imutável;
9. cria pedido pendente;
10. cria reservas Stock com expiração;
11. grava auditoria e outbox na mesma transação.

### Consultar

```http
GET /valley/checkout/{checkout_id}
```

Somente o consumidor titular pode consultar.

### Confirmar com Wallet

```http
POST /valley/checkout/{checkout_id}/confirm
```

A confirmação:

1. bloqueia checkout, pedido, reservas e Wallet;
2. exige Wallet pessoal ativa;
3. impede autorização acima do saldo disponível;
4. transfere saldo disponível para saldo retido;
5. cria escrow sem liberação automática;
6. grava lançamento `escrow_hold` no ledger;
7. confirma as reservas Stock;
8. marca o pedido como `paid`;
9. marca o pagamento como `authorized`;
10. limpa o carrinho somente após sucesso;
11. não liquida o valor ao lojista;
12. não inicia Delivery.

Falha de Wallet:

- marca o checkout `payment_failed`;
- marca o pedido `cancelled`;
- libera todas as reservas na mesma transação;
- publica eventos de falha e compensação;
- não cria escrow nem ledger.

### Cancelar

```http
POST /valley/checkout/{checkout_id}/cancel
```

O cancelamento é idempotente enquanto o checkout não estiver confirmado e libera as reservas pendentes.

## 5. Estados

Checkout:

```text
requested
pending_stock_reservation
pending_payment
confirmed
rejected
payment_failed
cancelled
expired
```

Pagamento:

```text
not_started
pending
authorized
failed
cancelled
```

Reserva Stock:

```text
reserved
committed
released
expired
```

Estados terminais do checkout não podem retroceder.

## 6. Snapshot imutável

O snapshot contém:

- cart_id;
- store_id;
- company_id;
- moeda;
- total em BRL;
- product_id;
- inventory_item_id;
- SKU;
- nome;
- quantidade;
- preço unitário;
- subtotal;
- promoção vigente;
- timestamp do catálogo.

O banco impede alteração posterior do snapshot, total, referências, idempotência, correlação e expiração.

## 7. Idempotência

### Criação

Escopo:

```text
(user_id, X-Idempotency-Key)
```

Mesmo corpo:

- retorna o mesmo checkout;
- não cria novo pedido;
- não cria novas reservas;
- não publica eventos duplicados.

Corpo diferente:

- retorna conflito;
- registra auditoria;
- não altera a operação original.

### Confirmação

Escopo:

```text
(user_id, confirmation_idempotency_key)
```

A repetição de checkout confirmado retorna o resultado existente sem duplicar escrow, ledger ou baixa Stock.

## 8. Eventos

Implementados:

- `marketplace.checkout.started`;
- `marketplace.order.created`;
- `stock.reservation.created`;
- `finance.payment.authorized`;
- `finance.payment.failed`;
- `stock.reservation.committed`;
- `stock.reservation.released`;
- `stock.reservation.expired`;
- `marketplace.checkout.confirmed`;
- `marketplace.checkout.cancelled`.

Todos usam envelope com:

- event_id;
- occurred_at;
- actor_user_id;
- user_id;
- entity_id;
- aggregate_type;
- aggregate_id;
- correlation_id;
- causation_id;
- schema_version;
- payload minimizado.

## 9. Segurança e isolamento

- consumidor opera somente o próprio carrinho e checkout;
- preço e saldo enviados pelo cliente nunca são autoritativos;
- consultas SQL são parametrizadas;
- dados brutos de cartão não são aceitos;
- apenas BRL e Wallet interna são permitidos nesta versão;
- credenciais e DSNs ficam fora do repositório;
- saldo autoritativo permanece no Stock;
- valores financeiros permanecem no ledger;
- Vision permanece inativo.

## 10. Testes obrigatórios

- migration 032 em banco limpo;
- rollback 032 reproduzível;
- feature flag desligada por padrão;
- criação bloqueada com flag desligada;
- carrinho vazio bloqueado;
- carrinho de outro usuário bloqueado;
- item ou loja indisponível bloqueados;
- preço divergente bloqueado;
- checkout com múltiplas lojas bloqueado;
- saldo Stock insuficiente bloqueado;
- mesma chave e mesmo corpo retornam o mesmo checkout;
- mesma chave e corpo diferente retornam conflito;
- concorrência não torna estoque negativo;
- Wallet insuficiente libera reservas;
- confirmação cria apenas um escrow e um ledger;
- confirmação repetida não duplica efeitos;
- snapshot permanece imutável;
- pedido, reservas, ledger e eventos compartilham correlation_id;
- cancelamento é idempotente;
- auditoria e outbox são preservados;
- nenhum fluxo Delivery, Rider ou Vision é iniciado.

## 11. Fora do escopo

- PSP externo;
- dados de cartão;
- liquidação ao lojista;
- split produtivo;
- parcelamento;
- múltiplas moedas;
- cálculo de frete;
- Delivery;
- atribuição de Rider;
- ativação automática em produção;
- reativação do Vision.

## 12. Critério de conclusão

A issue #78 somente poderá ser encerrada após:

1. todos os testes passarem;
2. CI, Security, Database, OpenAPI e Docker ficarem verdes no mesmo SHA;
3. diff integral revisado;
4. ausência de segredos comprovada;
5. ausência de reviews ou threads bloqueadoras;
6. Squash and Merge com `expected_head_sha`;
7. commit consolidado confirmado na `main`.
