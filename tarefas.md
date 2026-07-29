# Tarefas da IA Desenvolvedora

**Versão:** 2.5  
**Data e hora:** 29/07/2026 04:40, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch:** `feat/marketplace-checkout-idempotente-2026-07-29`  
**Commit-base:** `6f76c6359eca268aaafc301a51c0f754be8998c8`  
**Issues:** `#51`, `#78` e `#79`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`

## 1. Regra mandatória de prioridade

Antes de qualquer nova evolução, tratar nesta ordem:

1. workflows falhos ou bloqueados;
2. merges pendentes ou conflitantes;
3. pull requests abertas;
4. commits e branches não integrados;
5. issues executáveis;
6. somente depois, nova evolução autorizada.

## 2. Fechamentos confirmados

- PR #74 integrada por Squash and Merge no commit `f1681dd2cbff145a661254cb1ce49f059121d7f2`;
- PR #75 encerrada sem merge por escopo divergente;
- PR #76 integrada por Squash and Merge no commit `6f76c6359eca268aaafc301a51c0f754be8998c8`;
- PR #77 encerrada sem merge por estar baseada antes do PR #76 e misturar branding, CI e documentação divergente;
- issue #79 preserva os nove ajustes de branding para reaplicação controlada;
- Continuous Integration, Security, Docker Compose Health Gate e A1 Admin Template passaram no head final do PR #76;
- Vision permanece excluído;
- nenhuma credencial foi versionada.

## 3. Estado real do Marketplace

O PR #65 já integrou:

- catálogo público;
- busca, filtros e paginação;
- geolocalização e ordenação por distância;
- feed vertical;
- promoção do dia;
- favoritos;
- carrinho isolado por usuário.

O carrinho atual calcula preço e disponibilidade a partir de `products.payload`, incluindo `price_brl` e `stock_quantity`.

## 4. Bloqueio estrutural comprovado

O módulo Stock atual ainda não possui entidade de inventário ou reserva transacional. As entidades tipadas registradas são:

- suppliers;
- catalog_products;
- price_rules;
- supplier_orders;
- discount_quotes.

O `modules/stock/main.py` expõe apenas cálculo de conversão de unidades além das rotas genéricas compartilhadas.

Portanto, não é permitido declarar checkout concluído nem criar uma reserva fictícia dentro do Marketplace. A fonte única de saldo precisa ser criada no Stock antes da confirmação financeira.

## 5. Objetivo imediato da issue #78

Implementar o checkout por incrementos seguros:

### Incremento A, contrato e fundação

1. versionar o contrato de checkout;
2. definir a máquina de estados;
3. definir a chave de idempotência;
4. definir snapshot imutável dos itens;
5. definir eventos e compensações;
6. manter feature flag desligada;
7. mapear migrations e stores necessários.

### Incremento B, Stock transacional

1. adicionar inventory_items;
2. adicionar stock_reservations;
3. criar reserva com expiração;
4. impedir estoque negativo;
5. tratar concorrência;
6. liberar ou confirmar reserva;
7. publicar eventos por outbox.

### Incremento C, pedido e pagamento

1. criar pedido idempotente;
2. validar preço e disponibilidade novamente;
3. lançar valores somente no ledger;
4. tratar pagamento pendente, aprovado, rejeitado e compensado;
5. impedir dupla cobrança;
6. confirmar a baixa somente após autorização válida.

## 6. Estado desta execução

- issue #78 criada;
- branch `feat/marketplace-checkout-idempotente-2026-07-29` criada sobre a main atual;
- contrato de checkout será versionado nesta branch;
- nenhuma reserva, pedido ou pagamento fictício será criado;
- Delivery permanece bloqueado.

## 7. Validação obrigatória

Antes de qualquer implementação transacional:

```bash
python scripts/validate_repository.py
python -m pytest -q tests/test_marketplace_discovery.py
python -m pytest -q modules/marketplace/tests
python -m pytest -q modules/stock/tests
python -m pytest -q modules/finance/tests
```

Quando houver migration ou store:

- banco PostgreSQL limpo;
- migrations ordenadas;
- testes de concorrência;
- testes de idempotência;
- testes de expiração e compensação;
- Database, CI, Security, OpenAPI e Compose verdes no mesmo SHA.

## 8. Critérios de aceite do checkout completo

- fonte única de saldo no Stock;
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
- integração por Squash and Merge.

## 9. Proibições

- não executar push direto na `main`;
- não criar saldo de estoque dentro do Marketplace;
- não armazenar dados brutos de cartão;
- não simular pagamento como liquidado;
- não iniciar Delivery;
- não reativar Vision;
- não excluir ativos de marca sem confirmar substituição;
- não integrar PR com gate vermelho ou escopo divergente.

## 10. Histórico

| Versão | Data | Alteração |
|---|---|---|
| 2.0 | 28/07/2026 | PR #62, QA Rider e testes Git determinísticos. |
| 2.1 | 28/07/2026 | Rodada 005 com contratos e feature flags. |
| 2.2 | 28/07/2026 | Marketplace Fase 1 e governança de pendências. |
| 2.3 | 28/07/2026 | A1 Admin Web + Mobile, Android seguro e pacote Figma. |
| 2.4 | 29/07/2026 | PR #74 integrada, PR #75 rejeitada e correção Android v2.9 isolada. |
| 2.5 | 29/07/2026 | PR #76 integrada, PR #77 preservada sem merge e checkout bloqueado até existir reserva transacional no Stock. |
