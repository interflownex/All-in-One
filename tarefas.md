# Tarefas da IA Desenvolvedora

**Versão:** 2.7  
**Data e hora:** 29/07/2026 04:54, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `docs/marketplace-checkout-contract-v1-2026-07-29`  
**Commit-base:** `438d64f46ef341f6a3559dbcb6642cd950ba7291`  
**Issues:** `#51` e `#78`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Públicos:** Pessoa Física, Pessoa Jurídica, Equipe Técnica e gestão

## 1. Regra mandatória de prioridade

Antes de qualquer nova evolução, tratar nesta ordem:

1. workflows falhos ou bloqueados;
2. merges pendentes ou conflitantes;
3. pull requests abertas;
4. commits e branches não integrados;
5. issues executáveis;
6. somente depois, nova evolução autorizada.

A política autoritativa permanece em `config/autonomy/pending_work_priority_policy.json` e `AGENTS.md`.

## 2. Estado consolidado

- PR #65 integrou catálogo, busca, filtros, paginação, geolocalização, feed vertical, promoção, favoritos e carrinho;
- PR #74 integrou exclusões persistentes do VS Code;
- PR #75 foi encerrada sem merge por escopo divergente;
- PR #76 integrou o contrato Android v2.9 no release;
- PR #77 foi encerrada sem merge por sobreposição e base ultrapassada;
- PR #80 integrou ativos oficiais, scanner de branding, lint Valley e preparo do logo no PDV;
- PR #81 teve gates verdes, mas foi encerrada sem merge porque a `main` avançou com o PR #80;
- o contrato de checkout foi reconstruído sobre `438d64f46ef341f6a3559dbcb6642cd950ba7291`;
- Vision permanece excluído;
- nenhuma credencial ou segredo foi versionado.

## 3. Estado real do Marketplace

O Marketplace já possui:

- catálogo público;
- busca e filtros;
- paginação;
- geolocalização e distância;
- feed vertical;
- promoção do dia;
- favoritos;
- carrinho isolado por usuário.

O carrinho calcula o total usando `price_brl` e considera disponibilidade usando `stock_quantity` dentro do produto.

Esse campo não é uma fonte transacional de estoque.

## 4. Bloqueio estrutural comprovado

O Stock atual ainda não possui entidades tipadas de inventário ou reserva.

Entidades existentes:

- suppliers;
- catalog_products;
- price_rules;
- supplier_orders;
- discount_quotes.

Antes do checkout funcional, devem existir:

- `inventory_items`;
- `stock_reservations`;
- migrations reversíveis;
- store PostgreSQL transacional;
- bloqueio de concorrência;
- expiração;
- confirmação;
- liberação;
- auditoria;
- outbox.

Não criar reserva dentro do Marketplace.

## 5. Entregas deste ciclo

1. versionar `modules/marketplace/CHECKOUT_CONTRACT.md` em 0.1.0;
2. registrar feature flag desligada;
3. definir request, response e máquina de estados;
4. definir snapshot imutável;
5. definir idempotência;
6. definir contrato obrigatório do Stock;
7. definir ledger, compensações e eventos;
8. definir telemetria, alertas e rollback;
9. atualizar relatório v3.8;
10. atualizar plano v3.8;
11. abrir PR em rascunho sobre a `main` atual;
12. reexecutar todos os gates no novo head.

## 6. Próxima implementação autorizada

### Incremento A, Stock transacional

1. adicionar `inventory_items` à matriz tipada;
2. adicionar `stock_reservations` à matriz tipada;
3. criar migration reversível;
4. criar constraints e índices;
5. reservar saldo de forma atômica;
6. impedir estoque negativo;
7. tratar repetição da mesma chave;
8. rejeitar mesma chave com corpo diferente;
9. criar expiração;
10. confirmar e liberar reserva;
11. publicar eventos por outbox;
12. registrar auditoria imutável.

### Incremento B, checkout idempotente

Somente depois do Incremento A:

1. proteger endpoint por `MARKETPLACE_CHECKOUT_V1_ENABLED`;
2. revalidar carrinho e preços;
3. criar snapshot imutável;
4. solicitar reserva ao Stock;
5. criar pedido idempotente;
6. iniciar pagamento como pendente;
7. usar ledger como única fonte financeira;
8. compensar reserva em falha;
9. impedir dupla cobrança;
10. não retornar `paid` sem evidência homologada.

## 7. Ordem funcional

1. Marketplace;
2. Stock;
3. Delivery.

O Stock participa agora somente como fundação necessária ao checkout do Marketplace. A Fase Stock completa continua posterior. Delivery permanece bloqueado.

## 8. Testes obrigatórios

### Contrato atual

```bash
python scripts/validate_repository.py
python -m pytest -q tests/test_marketplace_discovery.py
python -m pytest -q modules/marketplace/tests
python -m pytest -q modules/stock/tests
python -m pytest -q modules/finance/tests
```

### Futuro Stock transacional

- banco PostgreSQL limpo;
- migrations ordenadas e reversíveis;
- saldo suficiente e insuficiente;
- duas reservas concorrentes;
- idempotência;
- conflito de chave;
- expiração;
- liberação;
- confirmação;
- prevenção de saldo negativo;
- evento único;
- isolamento por empresa;
- rollback.

### Gates remotos

- Continuous Integration;
- Security;
- Database;
- OpenAPI;
- Docker Compose Health Gate;
- demais workflows acionados pelo diff.

Todos devem estar verdes no mesmo SHA.

## 9. Critérios de aceite do checkout completo

- Stock é a fonte única de saldo;
- reserva transacional com expiração;
- preço revalidado no servidor;
- snapshot imutável;
- pedido idempotente;
- ledger como única fonte financeira;
- nenhuma dupla cobrança;
- outbox e consumidores idempotentes;
- auditoria imutável;
- feature flag desligada até homologação;
- rollback comprovado;
- integração por Squash and Merge com `expected_head_sha`.

## 10. Proibições

- não fazer push direto na `main`;
- não usar `stock_quantity` do produto como saldo autoritativo;
- não criar estoque paralelo dentro do Marketplace;
- não criar pedido sem reserva válida;
- não lançar valor fora do ledger;
- não armazenar dados brutos de cartão;
- não simular pagamento como liquidado;
- não iniciar Delivery;
- não reativar Vision;
- não modificar ativos oficiais sem autorização;
- não excluir ativos de marca às cegas;
- não integrar PR com gate vermelho, ausente ou em processamento;
- não reutilizar gates de head anterior.

## 11. Governança de merge pendente

O repositório ainda deve ser configurado administrativamente para:

- `allow_squash_merge = true`;
- `allow_merge_commit = false`;
- `allow_rebase_merge = false`.

Enquanto isso não for confirmado, auto-merge permanece bloqueado.

## 12. Evidências obrigatórias

- SHA da branch e do PR;
- lista de arquivos alterados;
- testes executados;
- gates do mesmo head;
- ausência de reviews ou threads pendentes;
- diff sem segredos;
- merge por squash;
- commit final na `main`;
- atualização das issues #51 e #78.

## 13. Histórico

| Versão | Data e hora | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web/Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 | PRs #74/#76 integrados; #75 rejeitado por escopo. |
| 2.5 | 29/07/2026 04:40 | Issue #79 reaplicada após fechamento seguro do PR #77. |
| 2.6 | 29/07/2026 04:43 | PR #80 integrou branding oficial e scanner corrigido. |
| 2.7 | 29/07/2026 04:54 | Contrato de checkout reconstruído sobre a main atual e Stock transacional definido como próximo incremento. |
