# Plano de Ação Codex

**Versão:** 3.8  
**Data e hora:** 29/07/2026 04:54, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/marketplace-checkout-contract-v1-2026-07-29`  
**Commit-base:** `438d64f46ef341f6a3559dbcb6642cd950ba7291`  
**Issues:** `#51` e `#78`  
**Ciclo principal:** 8 horas  
**Tolerância operacional:** até 4 horas

## 1. Missão

Construir a fundação transacional do Stock necessária ao checkout, sem criar saldo paralelo no Marketplace e sem iniciar Delivery.

## 2. Bloco 1, 0h a 1h30: inventário e contrato

1. confirmar o head atual da `main`;
2. confirmar que não existem PRs abertas conflitantes;
3. inventariar migrations e store PostgreSQL do Stock;
4. confirmar o contrato do Marketplace já integrado;
5. confirmar as regras de ledger e outbox;
6. atualizar a matriz `documentado | implementado | testado | homologado | bloqueado`.

## 3. Bloco 2, 1h30 a 3h: modelo do Stock

Adicionar à fonte tipada:

- `inventory_items`;
- `stock_reservations`.

Definir:

- saldo físico;
- saldo reservado;
- saldo disponível derivado;
- SKU e product_id;
- company_id e warehouse_id quando aplicável;
- versão para concorrência;
- expiração;
- status monotônico;
- idempotency_key;
- correlation_id.

## 4. Bloco 3, 3h a 5h: migration e store

1. criar migration reversível;
2. criar índices e constraints;
3. impedir saldo negativo;
4. bloquear linha durante a reserva;
5. implementar reserva atômica;
6. implementar confirmação;
7. implementar liberação;
8. implementar expiração;
9. criar auditoria e outbox no mesmo limite transacional.

## 5. Bloco 4, 5h a 6h30: testes

Testar em banco PostgreSQL limpo:

- reserva válida;
- saldo insuficiente;
- duas reservas concorrentes;
- repetição da mesma chave;
- mesma chave com corpo diferente;
- expiração;
- liberação;
- confirmação;
- prevenção de estoque negativo;
- evento único por operação;
- isolamento por empresa.

## 6. Bloco 5, 6h30 a 7h30: integração de contrato

Somente após o Stock estar comprovado:

1. adicionar o endpoint de checkout protegido pela feature flag;
2. revalidar carrinho, preço e publicação;
3. criar snapshot imutável;
4. solicitar reserva ao Stock;
5. criar pedido idempotente;
6. iniciar pagamento como pendente;
7. não retornar estado pago sem ledger e provedor homologado.

## 7. Bloco 6, 7h30 a 8h: fechamento

1. atualizar OpenAPI;
2. atualizar eventos e documentação;
3. atualizar `tarefas.md`;
4. atualizar relatório e plano;
5. executar gates no mesmo SHA;
6. revisar segredos, threads e mergeabilidade;
7. manter PR em rascunho enquanto houver gate pendente.

## 8. Critérios de aceite

- fonte única de saldo no Stock;
- migrations reversíveis;
- reserva atômica e idempotente;
- concorrência comprovada;
- nenhuma reserva dentro do Marketplace;
- ledger como única fonte financeira;
- outbox no mesmo limite transacional;
- feature flag desligada;
- CI, Security, Database, OpenAPI e Compose verdes no mesmo SHA;
- integração exclusivamente por Squash and Merge.

## 9. Proibições

- não usar `products.payload.stock_quantity` como saldo autoritativo;
- não criar pedido sem reserva válida;
- não criar saldo paralelo;
- não lançar valor fora do ledger;
- não armazenar dados brutos de cartão;
- não simular liquidação como real;
- não iniciar Delivery;
- não reativar Vision;
- não excluir ativos de marca;
- não fazer push direto na `main`.

## 10. Regra de parada

Após 12 horas, não iniciar nova frente. Registrar:

- concluído;
- parcial;
- falhou;
- causa;
- evidência;
- bloqueio externo;
- rollback;
- primeira tarefa do próximo ciclo.
