# Tarefas da IA Desenvolvedora

**Versão:** 3.1  
**Data e hora:** 30/07/2026 06:20, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de registro:** `feat/stock-reservations-foundation-20260730`  
**Commit-base:** `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`  
**Issue principal:** `#83`  
**Issues dependentes:** `#51` e `#78`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado consolidado

- PR #91 integrada no commit `c566d5dc9f45192b05f4bb8871dbee7ca0827a93`;
- PR #90 integrada no commit `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`;
- PR #92 aberta em rascunho para a issue #83;
- Vision permanece inativo;
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada;
- Delivery, pagamento, ledger e Rider estão fora desta etapa;
- nenhuma credencial ou segredo foi versionado;
- a CI comprovou que a `main` já possui migrations até 030 e que o prefixo 027 pertence ao adaptador legado;
- a fundação Stock foi renumerada corretamente para 031.

## 2. Objetivo atual

Validar e integrar a fundação transacional mínima do Stock, criando a fonte única de saldo e o ciclo de reservas necessário ao checkout futuro do Marketplace.

## 3. Implementação presente na branch

### PostgreSQL

- migration `031_stock_inventory_reservations.sql`;
- rollback `database/postgres/rollbacks/031_stock_inventory_reservations.sql`;
- tabela `stock.inventory_items`;
- tabela `stock.stock_reservations`;
- saldo disponível gerado por `physical_quantity - reserved_quantity`;
- trigger que deriva `active/depleted` pela disponibilidade real;
- constraints contra quantidade negativa e reserva superior ao saldo físico;
- unicidade de inventário por empresa, localização e SKU;
- unicidade idempotente por usuário, empresa e chave;
- índices por produto, empresa, pedido, status e expiração.

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
- auditoria e outbox na mesma transação;
- conflito quando a mesma chave recebe corpo diferente;
- isolamento por empresa.

### API

Arquivo: `modules/stock/main.py`, versão `0.3.0`.

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
- contexto Business para inventário;
- operador restrito à empresa autenticada;
- `X-Correlation-Id` obrigatório;
- `X-Idempotency-Key` obrigatório na reserva;
- expiração global exige `stock:reservations:expire`;
- DSN `ALL_IN_ONE_STOCK_POSTGRES_DSN` fora do Git.

### Eventos

```text
stock.reservation.created
stock.reservation.rejected
stock.reservation.committed
stock.reservation.released
stock.reservation.expired
```

### Contratos

- `modules/stock/RESERVATION_CONTRACT.md` versão `0.2.2`;
- `modules/stock/OPENAPI.yaml` versão `0.3.0`;
- OpenAPI Stock registrado como artefato especializado no scaffold efetivo;
- nenhuma rota de checkout ou Delivery;
- Vision ausente.

### Testes

- `tests/test_stock_reservation_contract.py`;
- `tests/test_stock_reservations_integration.py`;
- aplicação da migration em PostgreSQL 16 limpo;
- prova de rollback no banco efêmero;
- reserva válida e saldo insuficiente;
- idempotência e conflito de corpo;
- concorrência sem saldo negativo;
- confirmação, liberação e expiração;
- evento único e auditoria;
- isolamento por empresa;
- stores tipados validados diretamente contra as migrations atuais.

## 4. Falhas encontradas e corrigidas durante a revisão

1. OpenAPI Stock era sobrescrito pelo scaffold genérico.
2. Validador PostgreSQL havia perdido verificações imutáveis e `--repeat-migrations`.
3. Operadores podiam atravessar empresas em reservas.
4. Expiração global aceitava perfil sem escopo específico.
5. Status do inventário podia divergir da disponibilidade após confirmação.
6. Migration Stock havia sido numerada como 027 apesar da existência das migrations 027 a 030.
7. Catálogo tipado usava somente snapshot antigo, em vez das migrations atuais.
8. Um DSN de teste BPM recebeu hífen no usuário durante edição e foi corrigido antes da validação final.

## 5. Próxima sequência obrigatória

1. acompanhar todos os workflows da PR #92 no head final;
2. corrigir qualquer nova falha comprovada;
3. reexecutar todos os gates no novo SHA após cada correção;
4. revisar o diff completo;
5. verificar segredos, tokens, chaves privadas e credenciais;
6. confirmar ausência de conflitos, reviews bloqueadoras e threads pendentes;
7. marcar a PR como pronta somente com todos os gates executáveis verdes no mesmo SHA;
8. integrar por Squash and Merge com `expected_head_sha`;
9. confirmar o commit consolidado na `main`;
10. confirmar o encerramento da issue #83;
11. revisar a issue #78 como próxima dependência possível, sem ativar checkout automaticamente.

## 6. Gates obrigatórios

- Continuous Integration;
- Security;
- Database;
- OpenAPI;
- Docker Compose Health Gate;
- Valley DAST;
- A1 Admin Template;
- demais workflows acionados pelo diff.

Todos devem ficar verdes no mesmo SHA. Workflow de automerge ignorado por ausência de rótulo não representa falha quando a integração é manual e protegida por SHA.

## 7. Critérios de aceite da issue #83

- migration 031 corretamente ordenada;
- rollback reproduzível;
- `stock.inventory_items` como saldo autoritativo;
- `stock.stock_reservations` como reservas autoritativas;
- reserva com bloqueio de linha;
- concorrência comprovada em PostgreSQL real;
- idempotência e conflito de corpo;
- confirmação, liberação e expiração idempotentes;
- auditoria e outbox na mesma transação;
- isolamento por empresa;
- OpenAPI alinhado;
- diff sem segredos;
- todos os gates verdes no mesmo head;
- Squash and Merge protegido por SHA.

## 8. Proibições

- não fazer push direto na `main`;
- não usar `marketplace.products.stock_quantity` como saldo autoritativo;
- não criar estoque paralelo no Marketplace;
- não criar pedido automaticamente;
- não ativar `MARKETPLACE_CHECKOUT_V1_ENABLED`;
- não lançar valores financeiros;
- não iniciar Delivery;
- não atribuir Rider;
- não reativar Vision;
- não versionar segredos;
- não integrar com workflow vermelho ou em processamento;
- não reutilizar evidência de head SHA anterior;
- não executar rollback da migration 031 automaticamente em produção.

## 9. Etapa posterior

Após a issue #83 ser integrada, a issue #78 poderá implementar o checkout idempotente consumindo exclusivamente uma reserva válida do Stock.

```text
Marketplace -> Stock -> Delivery
```

Delivery só pode iniciar após checkout e pagamento comprovados em etapas próprias.

## 10. Evidências esperadas

- URL da PR #92;
- head SHA validado;
- tabela de workflows;
- evidência dos testes PostgreSQL;
- evidência da migration 031 e rollback;
- revisão do diff;
- varredura de segredos;
- commit consolidado na `main`;
- estado final da issue #83.

## 11. Histórico resumido

| Versão | Data | Alteração |
|---|---|---|
| 2.0 a 2.9 | 28–29/07/2026 | Evoluções anteriores, contratos, branding e aplicações. |
| 3.0 | 30/07/2026 | PRs #90/#91 integradas e fundação Stock implementada. |
| 3.1 | 30/07/2026 | Migration Stock corrigida para 031 e falhas de revisão consolidadas. |
