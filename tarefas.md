# Tarefas da IA Desenvolvedora

**Versão:** 2.8  
**Data e hora:** 29/07/2026 05:15, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/stock-reservations-foundation-2026-07-29`  
**Commit-base:** `002125a2b46d67f56a2651f797ec0392a06cb4c0`  
**Issues:** `#51`, `#78` e `#83`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Públicos:** Pessoa Física, Pessoa Jurídica, Equipe Técnica e gestão

## 1. Estado consolidado

- PR #65 integrou catálogo, busca, filtros, paginação, geolocalização, feed vertical, promoção, favoritos e carrinho;
- PR #74 integrou exclusões persistentes do VS Code;
- PR #75 foi encerrada sem merge por escopo divergente;
- PR #76 integrou o contrato Android v2.9;
- PR #77 foi encerrada sem merge por sobreposição;
- PR #80 integrou branding oficial e scanner corrigido;
- PR #81 foi encerrada sem merge após avanço da `main`;
- PR #82 integrou o contrato de checkout v0.1.0, relatório v3.8, plano v3.8 e tarefas v2.7;
- commit atual da `main`: `002125a2b46d67f56a2651f797ec0392a06cb4c0`;
- issue #83 e branch de fundação Stock abertas;
- Vision permanece excluído;
- nenhuma credencial ou segredo foi versionado.

## 2. Objetivo imediato

Criar a fonte única de saldo e reserva transacional no Stock, necessária ao checkout do Marketplace.

O trabalho deve ser dividido em quatro incrementos:

1. contrato e matriz tipada;
2. migration e store PostgreSQL;
3. reserva, confirmação, liberação e expiração;
4. testes de concorrência, idempotência, auditoria e outbox.

## 3. Primeira ação obrigatória

Antes de escrever SQL:

1. obter novamente o head da `main`;
2. listar migrations atuais em `database/postgres/migrations`;
3. identificar o próximo número livre sem inferência;
4. abrir e comparar a migration física que criou as tabelas atuais do Stock;
5. verificar constraints, UUIDs, timestamps, metadata, atores e FKs existentes;
6. confirmar padrões de reversibilidade e idempotência;
7. registrar o nome final da nova migration.

Nenhuma migration deve ser criada com número presumido.

## 4. Modelo autorizado

### `stock.inventory_items`

Campos mínimos:

- id;
- user_id;
- company_id;
- warehouse_id quando aplicável;
- product_id;
- sku;
- physical_quantity;
- reserved_quantity;
- available_quantity derivada ou validada;
- version;
- status;
- metadata;
- created_at e updated_at;
- created_by e updated_by;
- idempotency_key quando aplicável.

Regras:

- quantidades nunca negativas;
- reserved_quantity não supera physical_quantity;
- company_id e SKU formam escopo de unicidade quando aplicável;
- atualizações concorrentes usam bloqueio de linha ou versão otimista comprovada.

### `stock.stock_reservations`

Campos mínimos:

- id;
- user_id;
- company_id;
- order_id;
- inventory_item_id;
- quantity;
- status;
- idempotency_key;
- request_hash;
- correlation_id;
- expires_at;
- committed_at;
- released_at;
- metadata;
- created_at e updated_at;
- created_by e updated_by.

Estados permitidos:

```text
pending -> reserved -> committed
pending -> rejected
reserved -> released
reserved -> expired
```

Transições são monotônicas e auditadas.

## 5. Operações obrigatórias

### Reservar

1. validar ator, empresa, item e quantidade;
2. localizar idempotência anterior;
3. rejeitar chave reutilizada com corpo diferente;
4. bloquear o item de inventário;
5. calcular saldo disponível no servidor;
6. rejeitar saldo insuficiente;
7. aumentar reserved_quantity;
8. criar a reserva;
9. gravar auditoria e outbox na mesma transação.

### Confirmar

1. aceitar somente reserva ativa;
2. diminuir physical_quantity e reserved_quantity;
3. marcar `committed`;
4. registrar evento único;
5. repetir com segurança quando já confirmada.

### Liberar

1. aceitar reserva ativa;
2. diminuir reserved_quantity;
3. marcar `released`;
4. registrar motivo e evento;
5. repetir sem duplicar efeito.

### Expirar

1. selecionar reservas vencidas e ativas;
2. bloquear cada reserva;
3. liberar saldo;
4. marcar `expired`;
5. registrar evento e auditoria;
6. permitir execução repetida sem efeito duplicado.

## 6. Eventos

- `stock.reservation.created`;
- `stock.reservation.rejected`;
- `stock.reservation.committed`;
- `stock.reservation.released`;
- `stock.reservation.expired`.

Envelope obrigatório:

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

## 7. Testes obrigatórios

### Estrutura

- migration presente e corretamente ordenada;
- tabelas, constraints e índices presentes;
- store tipado resolve as duas entidades;
- contratos e OpenAPI consistentes.

### Comportamento

- reserva válida;
- saldo insuficiente;
- mesma chave e mesmo corpo retornam a mesma reserva;
- mesma chave e corpo diferente retornam conflito;
- duas reservas concorrentes não geram estoque negativo;
- confirmação reduz saldo físico e reservado;
- liberação devolve disponibilidade;
- expiração libera saldo;
- confirmação, liberação e expiração são idempotentes;
- evento não é duplicado;
- isolamento por empresa;
- auditoria imutável;
- rollback reproduzível.

### Gates

- Continuous Integration;
- Security;
- Database;
- OpenAPI;
- Docker Compose Health Gate;
- demais workflows acionados pelo diff.

Todos os gates devem estar verdes no mesmo SHA.

## 8. Condição para conectar o checkout

O endpoint de checkout permanece bloqueado até que:

- Stock seja a fonte única de saldo;
- reserva transacional esteja comprovada;
- concorrência e idempotência estejam verdes;
- migrations sejam executadas em banco limpo;
- auditoria e outbox funcionem na mesma transação;
- rollback esteja documentado.

A feature flag `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada.

## 9. Ordem funcional

1. Marketplace;
2. Stock;
3. Delivery.

A fundação Stock atual é uma dependência controlada do checkout do Marketplace. Delivery permanece bloqueado.

## 10. Proibições

- não fazer push direto na `main`;
- não adivinhar número de migration;
- não usar `products.payload.stock_quantity` como saldo autoritativo;
- não criar estoque paralelo no Marketplace;
- não criar pedido sem reserva válida;
- não lançar valor fora do ledger;
- não iniciar Delivery;
- não reativar Vision;
- não versionar segredos;
- não integrar com gate vermelho, ausente ou em processamento;
- não reutilizar evidência de head anterior.

## 11. Governança de merge

- abrir PR em rascunho;
- revisar o escopo completo;
- confirmar ausência de segredos;
- confirmar reviews e threads;
- integrar exclusivamente por Squash and Merge com `expected_head_sha`;
- auto-merge permanece bloqueado enquanto outros métodos de merge estiverem habilitados.

## 12. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web/Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 | PRs #74/#76 integrados; #75 rejeitado por escopo. |
| 2.5 | 29/07/2026 04:40 | Issue #79 reaplicada após fechamento do PR #77. |
| 2.6 | 29/07/2026 04:43 | PR #80 integrou branding oficial. |
| 2.7 | 29/07/2026 04:54 | PR #82 integrou contrato de checkout e bloqueio de estoque paralelo. |
| 2.8 | 29/07/2026 05:15 | Issue #83 e branch Stock abertas com contrato de implementação, concorrência e idempotência. |
