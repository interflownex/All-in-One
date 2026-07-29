# Plano de Ação Codex

**Versão:** 3.9  
**Data e hora:** 29/07/2026 05:15, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/stock-reservations-foundation-2026-07-29`  
**Commit-base:** `002125a2b46d67f56a2651f797ec0392a06cb4c0`  
**Issues:** `#51`, `#78` e `#83`  
**Ciclo principal:** 8 horas  
**Tolerância:** até 4 horas

## 1. Missão

Implementar a fonte única de saldo e reserva transacional no Stock, necessária ao checkout do Marketplace, sem iniciar Delivery.

## 2. Bloco 1, 0h a 1h: confirmação física

1. confirmar o head atual da `main`;
2. confirmar ausência de PR concorrente;
3. listar o diretório real de migrations;
4. identificar o próximo número livre;
5. abrir a migration que criou as tabelas atuais do Stock;
6. confirmar convenções de UUID, FK, timestamps, metadata, atores e idempotência.

## 3. Bloco 2, 1h a 2h30: migration

1. criar `stock.inventory_items`;
2. criar `stock.stock_reservations`;
3. criar constraints de quantidade;
4. criar unicidade por empresa, localização e SKU quando aplicável;
5. criar índices por produto, empresa, status e expiração;
6. documentar reversão;
7. aplicar em banco PostgreSQL limpo.

## 4. Bloco 3, 2h30 a 4h30: store transacional

1. atualizar a matriz tipada;
2. atualizar `StockPostgresStore`;
3. implementar `reserve_inventory`;
4. implementar `commit_reservation`;
5. implementar `release_reservation`;
6. implementar `expire_reservations`;
7. usar bloqueio de linha ou concorrência otimista comprovada;
8. gravar auditoria e outbox na mesma transação.

## 5. Bloco 4, 4h30 a 6h30: testes

Testar:

- reserva válida;
- saldo insuficiente;
- quantidade inválida;
- mesma chave e mesmo corpo;
- mesma chave com corpo diferente;
- duas reservas concorrentes;
- confirmação;
- liberação;
- expiração;
- estados terminais;
- evento único;
- isolamento por empresa;
- rollback.

## 6. Bloco 5, 6h30 a 7h30: API e contrato

1. atualizar OpenAPI do Stock;
2. criar rotas internas ou públicas conforme autorização;
3. aplicar RBAC/ABAC;
4. exigir X-Actor-User-Id, X-Idempotency-Key e X-Correlation-Id;
5. limitar payloads e logs;
6. manter o checkout desligado.

## 7. Bloco 6, 7h30 a 8h: fechamento

1. atualizar `tarefas.md`;
2. atualizar relatório e plano;
3. executar CI, Security, Database, OpenAPI e Compose;
4. revisar diff e segredos;
5. revisar reviews e threads;
6. marcar PR como pronta somente com gates verdes;
7. integrar por Squash and Merge com `expected_head_sha`.

## 8. Critérios de aceite

- migration corretamente numerada;
- banco limpo aprovado;
- Stock como fonte única de saldo;
- reserva atômica e idempotente;
- concorrência sem estoque negativo;
- expiração e compensação;
- auditoria e outbox;
- feature flag de checkout desligada;
- gates verdes no mesmo SHA;
- Delivery bloqueado;
- Vision excluído.

## 9. Proibições

- não adivinhar migration;
- não criar saldo paralelo no Marketplace;
- não criar pedido antes da reserva;
- não lançar valores financeiros;
- não iniciar Delivery;
- não armazenar dados de cartão;
- não versionar segredos;
- não fazer push direto na `main`;
- não integrar com gate pendente ou vermelho.

## 10. Regra de parada

Após 12 horas, não iniciar nova frente. Registrar o estado, evidências, bloqueios, rollback e primeiro passo do próximo ciclo.
