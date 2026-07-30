# Tarefas da IA Desenvolvedora

**Versão:** 3.0  
**Data e hora:** 30/07/2026 06:04, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de registro:** `feat/stock-reservations-foundation-20260730`  
**Commit-base:** `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`  
**Issue principal:** `#83`  
**Issues dependentes:** `#51` e `#78`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado consolidado

- PR #91 integrada por Squash and Merge no commit `c566d5dc9f45192b05f4bb8871dbee7ca0827a93`;
- PR #90 corrigida, validada e integrada por Squash and Merge no commit `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`;
- não havia PR aberta após a integração da PR #90;
- os commits recentes da `main` estavam vinculados às integrações comprovadas das PRs #90 e #91;
- a próxima tarefa executável confirmada foi a issue #83;
- Vision permanece inativo;
- nenhuma credencial ou segredo foi versionado;
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada;
- Delivery continua fora do escopo desta etapa.

## 2. Objetivo atual

Validar e integrar a fundação transacional mínima do Stock, criando a fonte única de saldo e o ciclo de reservas necessário ao checkout futuro do Marketplace.

A implementação desta branch não ativa checkout, pagamento, ledger, Delivery ou atribuição de Rider.

## 3. Implementação presente na branch

### PostgreSQL

- migration confirmada e numerada como `027_stock_inventory_reservations.sql`;
- tabela `stock.inventory_items`;
- tabela `stock.stock_reservations`;
- saldo disponível gerado por `physical_quantity - reserved_quantity`;
- constraints contra quantidade negativa e reserva superior ao saldo físico;
- unicidade de inventário por empresa, localização e SKU;
- unicidade idempotente por usuário, empresa e chave;
- índices por produto, empresa, pedido, status e expiração;
- rollback manual em `database/postgres/rollbacks/027_stock_inventory_reservations.sql`.

### Store transacional

Arquivo: `modules/shared/stock_postgres_store.py`.

Implementado:

- criação e ajuste versionado de inventário;
- hash SHA-256 estável para idempotência;
- reserva com `FOR UPDATE`;
- confirmação com baixa física e reservada;
- liberação de saldo;
- expiração com `FOR UPDATE SKIP LOCKED`;
- estados terminais idempotentes;
- auditoria e outbox no mesmo limite transacional;
- conflito quando a mesma chave recebe corpo diferente;
- isolamento por empresa.

### API

Arquivo: `modules/stock/main.py`, versão `0.3.0`.

Endpoints especializados:

```text
POST  /inventory/items
PATCH /inventory/items/{inventory_item_id}
POST  /reservations
POST  /reservations/{reservation_id}/commit
POST  /reservations/{reservation_id}/release
POST  /reservations/expire
```

Requisitos:

- ator autenticado;
- contexto Business para administração do inventário;
- `X-Correlation-Id` obrigatório;
- `X-Idempotency-Key` obrigatório na reserva;
- DSN `ALL_IN_ONE_STOCK_POSTGRES_DSN` somente fora do Git.

### Eventos

```text
stock.reservation.created
stock.reservation.rejected
stock.reservation.committed
stock.reservation.released
stock.reservation.expired
```

### Contratos

- `modules/stock/RESERVATION_CONTRACT.md` versão `0.2.0`;
- `modules/stock/OPENAPI.yaml` versão `0.3.0`;
- nenhuma rota de checkout ou Delivery incluída;
- Vision ausente.

### Testes

- `tests/test_stock_reservation_contract.py`;
- `tests/test_stock_reservations_integration.py`;
- aplicação da migration em PostgreSQL 16 limpo;
- prova de rollback no banco efêmero do workflow Database;
- reserva válida;
- saldo insuficiente;
- idempotência com mesmo corpo;
- conflito com corpo diferente;
- concorrência sem saldo negativo;
- confirmação;
- liberação;
- expiração;
- evento único;
- auditoria;
- isolamento por empresa.

## 4. Próxima sequência obrigatória

1. abrir pull request da branch `feat/stock-reservations-foundation-20260730` para `main`;
2. manter a PR em rascunho até os primeiros workflows terminarem;
3. acompanhar todos os workflows acionados pelo diff;
4. corrigir qualquer falha de CI, Security, Database, OpenAPI ou Docker;
5. executar novamente os workflows no novo head SHA após qualquer correção;
6. revisar o diff completo;
7. verificar ausência de segredos, tokens, chaves privadas e credenciais;
8. confirmar ausência de conflitos, reviews bloqueadoras e threads pendentes;
9. marcar a PR como pronta somente com todos os gates executáveis verdes no mesmo SHA;
10. integrar exclusivamente por Squash and Merge com `expected_head_sha`;
11. confirmar o commit consolidado na `main`;
12. fechar a issue #83 somente depois da integração comprovada.

## 5. Gates obrigatórios

- Continuous Integration;
- Security;
- Database;
- OpenAPI;
- Docker Compose Health Gate;
- demais workflows acionados pelo diff.

Todos devem estar verdes no mesmo SHA. Workflow ignorado por filtro ou por ausência de rótulo não deve ser confundido com falha, desde que não seja gate obrigatório da alteração.

## 6. Critérios de aceite da issue #83

- migration 027 corretamente ordenada;
- rollback reproduzível;
- `stock.inventory_items` como fonte autoritativa de saldo;
- `stock.stock_reservations` como fonte autoritativa de reservas;
- reserva com bloqueio de linha;
- concorrência comprovada em PostgreSQL real;
- idempotência e conflito de corpo comprovados;
- confirmação, liberação e expiração idempotentes;
- auditoria e outbox na mesma transação;
- isolamento por empresa;
- OpenAPI alinhado;
- diff sem segredos;
- todos os gates verdes no mesmo head;
- Squash and Merge protegido por SHA.

## 7. Proibições

- não fazer push direto na `main`;
- não usar `marketplace.products.stock_quantity` como saldo autoritativo;
- não criar estoque paralelo no Marketplace;
- não criar pedido automaticamente nesta etapa;
- não ativar `MARKETPLACE_CHECKOUT_V1_ENABLED`;
- não lançar valores financeiros;
- não iniciar Delivery;
- não atribuir Rider;
- não reativar Vision;
- não versionar segredos;
- não integrar com workflow vermelho, ausente ou em processamento;
- não reutilizar evidência de um head SHA anterior;
- não executar rollback da migration 027 automaticamente em produção.

## 8. Etapa posterior, ainda não autorizada por esta branch

Após a issue #83 ser integrada e comprovada, a issue #78 poderá implementar o checkout idempotente do Marketplace consumindo exclusivamente a reserva válida do Stock.

A ordem funcional permanece:

```text
Marketplace -> Stock -> Delivery
```

Delivery só poderá iniciar após checkout e pagamento comprovados em etapas próprias.

## 9. Evidências esperadas na entrega

- URL da pull request;
- head SHA validado;
- tabela de workflows e resultados;
- logs do teste PostgreSQL de concorrência;
- evidência da aplicação da migration;
- evidência do rollback;
- resumo da revisão do diff;
- resultado da varredura de segredos;
- commit consolidado na `main`, quando integrado.

## 10. Histórico resumido

| Versão | Data | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web/Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 | PRs #74/#76 integradas; escopos divergentes encerrados. |
| 2.5 | 29/07/2026 | Reaplicação controlada da issue #79. |
| 2.6 | 29/07/2026 | Branding oficial integrado pela PR #80. |
| 2.7 | 29/07/2026 | Contrato de checkout e bloqueio de estoque paralelo pela PR #82. |
| 2.8 | 29/07/2026 | Fundação Stock definida como prioridade. |
| 2.9 | 29/07/2026 | Entrega paralela AIO Admin Android registrada. |
| 3.0 | 30/07/2026 | PRs #90/#91 integradas e fundação Stock implementada para validação. |
