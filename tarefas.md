# Tarefas da IA Desenvolvedora

**Versão:** 3.3  
**Data e hora:** 30/07/2026 07:19, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de trabalho:** `feat/marketplace-checkout-idempotent-20260730`  
**Pull request:** `#94`  
**Issue em execução:** `#78`  
**Issue-mãe:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado consolidado

- PR #90 integrada no commit `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`;
- PR #91 integrada no commit `c566d5dc9f45192b05f4bb8871dbee7ca0827a93`;
- PR #92 integrada no commit `692ee05b1ca8e234d6875a1dfb153212a016ddb6`;
- PR #93 integrada no commit `87e3957002f3c9f5bde74e1f3ee56c3d4f79d1c8`;
- issue #83 concluída;
- PR #94 aberta em rascunho para executar exclusivamente a issue #78;
- Vision permanece inativo;
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada;
- nenhuma credencial ou DSN de produção foi versionada;
- Delivery, Rider, PSP externo e liquidação ao lojista continuam fora do escopo.

## 2. Objetivo atual

Implementar checkout idempotente do Marketplace consumindo exclusivamente a fonte autoritativa de saldo e reservas do Stock.

```text
Marketplace -> Stock -> Wallet/Escrow -> etapa futura de Delivery
```

A presente branch termina em pedido pago por Wallet interna, saldo retido em escrow e reservas Stock confirmadas. Não realiza entrega ou liquidação ao lojista.

## 3. Implementação presente na PR #94

### PostgreSQL

- migration `database/postgres/migrations/032_marketplace_checkout_attempts.sql`;
- rollback `database/postgres/rollbacks/032_marketplace_checkout_attempts.sql`;
- tabela `marketplace.checkout_attempts`;
- snapshot imutável;
- chave e hash idempotentes;
- referências para carrinho, loja, empresa, pedido e escrow;
- lista das reservas Stock;
- correlation_id e causation_id;
- trigger de imutabilidade e estados monotônicos;
- índices para usuário, empresa, expiração e confirmação idempotente.

### Orquestração transacional

Arquivo:

```text
modules/shared/marketplace_checkout_postgres_store.py
```

Implementado:

- bloqueio do carrinho;
- revalidação de produto, loja, preço e moeda;
- checkout de uma única loja e empresa nesta versão;
- bloqueio do inventário Stock com `FOR UPDATE`;
- criação de pedido pendente;
- criação de reservas Stock;
- confirmação por Wallet pessoal ativa;
- retenção de saldo em escrow;
- lançamento `escrow_hold` no ledger;
- confirmação do Stock somente após autorização financeira;
- liberação das reservas em falha de Wallet;
- cancelamento idempotente;
- limpeza do carrinho apenas após sucesso;
- auditoria e outbox na mesma transação.

### Rotas

```text
POST /valley/checkout
GET  /valley/checkout/{checkout_id}
POST /valley/checkout/{checkout_id}/confirm
POST /valley/checkout/{checkout_id}/cancel
```

Regras:

- criação exige `MARKETPLACE_CHECKOUT_V1_ENABLED=true`;
- a flag desligada não bloqueia consulta, confirmação ou compensação de operações já iniciadas;
- `X-Idempotency-Key` obrigatório em criação e confirmação;
- `X-Correlation-Id` obrigatório em todas as rotas;
- consumidor opera somente o próprio checkout;
- apenas `BRL` e `wallet` são aceitos nesta versão.

### Contratos

- `modules/marketplace/CHECKOUT_CONTRACT.md` versão `0.2.0`;
- `modules/marketplace/checkout/OPENAPI.yaml` versão `0.1.0`;
- nenhum endpoint Delivery ou Rider;
- nenhuma ativação produtiva automática;
- Vision ausente do fluxo funcional.

### Testes

- `tests/test_marketplace_checkout_contract.py`;
- `tests/test_marketplace_checkout_routes.py`;
- `tests/test_marketplace_checkout_integration.py`;
- migration em PostgreSQL 16 limpo;
- rollback 032 antes do rollback Stock 031;
- criação idempotente;
- conflito de corpo;
- preço divergente;
- Wallet insuficiente com compensação;
- escrow e ledger únicos;
- confirmação repetida sem duplicação;
- snapshot imutável;
- concorrência pelo último item sem estoque negativo;
- cancelamento idempotente;
- eventos correlacionados.

## 4. Estados permitidos

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

Reserva:

```text
reserved
committed
released
expired
```

## 5. Eventos previstos

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

## 6. Próxima sequência obrigatória

1. acompanhar todos os workflows acionados pela PR #94;
2. abrir o log de cada falha comprovada;
3. corrigir somente a causa real;
4. reiniciar a validação no novo head após qualquer alteração;
5. confirmar migration 032 em PostgreSQL 16;
6. confirmar idempotência, concorrência, escrow, ledger e compensação;
7. revisar o diff integral;
8. verificar ausência de segredos, tokens e DSNs de produção;
9. confirmar ausência de conflitos, reviews bloqueadoras e threads pendentes;
10. marcar a PR pronta apenas com todos os gates verdes no mesmo SHA;
11. integrar por Squash and Merge com `expected_head_sha`;
12. confirmar o commit consolidado na `main`;
13. confirmar o encerramento automático da issue #78;
14. atualizar a issue-mãe #51 e este documento.

## 7. Gates obrigatórios

- Continuous Integration;
- Security;
- Database;
- OpenAPI;
- Docker Compose Health Gate;
- demais workflows acionados pelo diff.

Resultado de um SHA anterior não pode ser reutilizado após qualquer commit novo.

## 8. Proibições persistentes

- não fazer push direto na `main`;
- não usar `marketplace.products.stock_quantity` como saldo autoritativo;
- não criar pedido sem reserva Stock válida;
- não editar ledger destrutivamente;
- não duplicar cobrança, escrow ou pedido;
- não armazenar dados brutos de cartão;
- não ligar a feature flag antes da homologação;
- não liquidar o valor ao lojista nesta branch;
- não iniciar Delivery;
- não atribuir Rider;
- não reativar Vision;
- não versionar segredos;
- não integrar com workflow vermelho, ausente ou em processamento;
- não executar rollback 032 automaticamente em produção.

## 9. Critério de conclusão da issue #78

A issue somente pode ser fechada com:

- migration 032 ordenada e reversível;
- snapshot imutável;
- checkout, pedido e reservas idempotentes;
- preço e saldo revalidados no servidor;
- saldo Stock nunca negativo;
- Wallet, escrow e ledger sem duplicação;
- falha financeira compensada;
- auditoria e eventos correlacionados;
- testes reproduzíveis;
- feature flag desligada por padrão;
- Delivery, Rider e Vision fora do escopo;
- todos os gates verdes no mesmo head;
- diff sem segredos;
- Squash and Merge protegido por SHA.

## 10. Histórico resumido

| Versão | Data | Alteração |
|---|---|---|
| 2.0 a 2.9 | 28–29/07/2026 | Evoluções anteriores, contratos, branding e aplicações. |
| 3.0 | 30/07/2026 | PRs #90/#91 integradas e fundação Stock implementada. |
| 3.1 | 30/07/2026 | Migration Stock corrigida para 031. |
| 3.2 | 30/07/2026 | PR #92 e issue #83 concluídas; issue #78 priorizada. |
| 3.3 | 30/07/2026 | PR #94 aberta e checkout idempotente implementado para validação. |
