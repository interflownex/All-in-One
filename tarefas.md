# Tarefas da IA Desenvolvedora

**Versão:** 3.4  
**Data e hora:** 30/07/2026 08:16, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Commit-base:** `c6da2cb578a7edc7bdfd9c9b2182ff6aeec6c239`  
**Issue-mãe:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado consolidado

- PR #90 integrada no commit `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`;
- PR #91 integrada no commit `c566d5dc9f45192b05f4bb8871dbee7ca0827a93`;
- PR #92 integrada no commit `692ee05b1ca8e234d6875a1dfb153212a016ddb6`;
- PR #93 integrada no commit `87e3957002f3c9f5bde74e1f3ee56c3d4f79d1c8`;
- PR #94 integrada no commit `c6da2cb578a7edc7bdfd9c9b2182ff6aeec6c239`;
- issue #83 concluída: fundação transacional Stock;
- issue #78 concluída: checkout idempotente com Stock e Wallet;
- issue-mãe #51 atualizada com o novo marco;
- Vision permanece inativo;
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada;
- nenhuma credencial ou DSN de produção foi versionada;
- Delivery e Rider permanecem não iniciados;
- nenhum valor foi liquidado ao lojista nesta etapa.

## 2. Etapas técnicas concluídas

```text
Marketplace catálogo/carrinho: concluído
Stock transacional: concluído
Checkout idempotente: concluído
Wallet interna + escrow hold: concluído tecnicamente
Ledger de retenção: concluído
Compensação de falha financeira: concluída
Liquidação produtiva/PSP: pendente
Delivery/Rider: não iniciado
```

## 3. Checkout integrado

### Persistência

- migration `database/postgres/migrations/032_marketplace_checkout_attempts.sql`;
- rollback `database/postgres/rollbacks/032_marketplace_checkout_attempts.sql`;
- tabela `marketplace.checkout_attempts`;
- snapshot imutável;
- estados monotônicos;
- idempotência de criação e confirmação;
- correlation_id e causation_id;
- referências para carrinho, pedido, reservas e escrow.

### Rotas

```text
POST /valley/checkout
GET  /valley/checkout/{checkout_id}
POST /valley/checkout/{checkout_id}/confirm
POST /valley/checkout/{checkout_id}/cancel
```

### Garantias comprovadas

- revalidação de preço, loja, produto, moeda e Stock no servidor;
- saldo autoritativo somente em `stock.inventory_items`;
- pedido e reservas criados na mesma transação;
- Wallet, escrow e ledger sem duplicação;
- falha financeira libera reservas;
- concorrência não produz estoque negativo;
- corrida simultânea da mesma chave retorna o mesmo checkout ou conflito 409;
- snapshot não pode ser alterado;
- cancelamento é idempotente;
- auditoria e outbox preservados;
- rollback 032 executado antes do rollback 031 no banco efêmero.

## 4. Evidências da PR #94

Head validado:

```text
932c3738c49e479c1cc5ca4c149a7c6eaf219a1e
```

Commit consolidado:

```text
c6da2cb578a7edc7bdfd9c9b2182ff6aeec6c239
```

Checks verdes no mesmo SHA:

- Continuous Integration #1834;
- Security #925;
- Database #442;
- OpenAPI #304;
- Docker Compose Health Gate #810;
- Valley DAST #283;
- A1 Admin Template #56.

A revisão final confirmou:

- 14 arquivos alterados;
- 18 commits preparados para squash;
- 18 commits à frente e 0 atrás da `main` antes do merge;
- nenhum review ou thread pendente;
- ausência de chaves privadas, tokens GitHub, chaves Google e chaves OpenAI;
- Squash and Merge protegido por `expected_head_sha`.

## 5. Próxima dependência da orquestração #51

Antes de ativar o checkout ou iniciar Delivery, deve existir uma atividade própria para homologação financeira produtiva.

Escopo necessário:

1. selecionar e homologar PSP compatível com o projeto;
2. definir adaptador independente de fornecedor;
3. validar assinatura de webhook;
4. garantir idempotência de autorização, captura, cancelamento, estorno e chargeback;
5. preservar ledger como fonte financeira;
6. definir liquidação e split sem alterar histórico;
7. implementar reconciliação;
8. adicionar observabilidade e alertas;
9. manter credenciais em Secret Manager;
10. manter a feature flag desligada até homologação completa.

Delivery e Rider só poderão avançar após pagamento produtivo comprovado e regras de compensação aprovadas.

## 6. Issues abertas que continuam independentes

- #51: orquestração Marketplace → Stock → Delivery;
- #89: convergir a fonte produtiva do AIO Admin AppDeploy com o repositório;
- #47: Health Watch + SafeZone com controles de consentimento e antiabuso;
- #55: implantação progressiva da Rodada 004;
- #39: onda de inovação nos 24 módulos ativos;
- #69: bloqueada por ausência da fonte funcional;
- #24: Promoção do Dia, sujeita a revalidação contra o estado atual.

## 7. Proibições persistentes

- não fazer push direto na `main`;
- não ativar `MARKETPLACE_CHECKOUT_V1_ENABLED` antes da homologação;
- não usar `marketplace.products.stock_quantity` como saldo autoritativo;
- não criar pedido sem reserva Stock válida;
- não alterar ou apagar ledger histórico;
- não duplicar cobrança, escrow ou pedido;
- não armazenar dados brutos de cartão;
- não versionar credenciais, tokens ou DSNs de produção;
- não liquidar valores sem contrato financeiro homologado;
- não iniciar Delivery;
- não atribuir Rider;
- não reativar Vision;
- não integrar PR com workflow vermelho, ausente ou em processamento;
- não reutilizar evidência de um SHA anterior;
- não executar rollbacks 031 ou 032 automaticamente em produção.

## 8. Próxima sequência obrigatória

1. formalizar a pendência de homologação PSP/liquidação como issue técnica própria ou subtarefa explícita da #51;
2. manter a feature flag desligada;
3. revisar a issue #89 como próxima frente independente e executável;
4. executar cada issue em branch exclusiva;
5. abrir PR em rascunho;
6. corrigir falhas comprovadas pelos workflows;
7. revisar diff e segredos;
8. validar todos os gates no mesmo SHA;
9. integrar somente por Squash and Merge protegido por SHA;
10. atualizar este documento após cada issue concluída.

## 9. Histórico resumido

| Versão | Data | Alteração |
|---|---|---|
| 2.0 a 2.9 | 28–29/07/2026 | Evoluções anteriores, contratos, branding e aplicações. |
| 3.0 | 30/07/2026 | PRs #90/#91 integradas e fundação Stock implementada. |
| 3.1 | 30/07/2026 | Migration Stock corrigida para 031. |
| 3.2 | 30/07/2026 | PR #92 e issue #83 concluídas. |
| 3.3 | 30/07/2026 | PR #94 aberta para executar a issue #78. |
| 3.4 | 30/07/2026 | PR #94 e issue #78 concluídas; homologação PSP definida como próxima dependência da #51. |
