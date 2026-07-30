# Tarefas da IA Desenvolvedora

**Versão:** 3.2  
**Data e hora:** 30/07/2026 07:06, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch de registro:** `docs/post-stock-orchestration-20260730`  
**Commit-base:** `692ee05b1ca8e234d6875a1dfb153212a016ddb6`  
**Issue concluída nesta rodada:** `#83`  
**Próxima issue executável:** `#78`  
**Issue-mãe:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado consolidado

- PR #91 integrada no commit `c566d5dc9f45192b05f4bb8871dbee7ca0827a93`;
- PR #90 integrada no commit `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`;
- PR #92 integrada por Squash and Merge no commit `692ee05b1ca8e234d6875a1dfb153212a016ddb6`;
- issue #83 encerrada automaticamente como concluída;
- nenhuma pull request permaneceu aberta após a integração da PR #92;
- o commit Stock é o commit mais recente da `main`;
- os commits recentes identificados correspondem a integrações de pull requests, sem commit recente isolado detectado;
- Vision permanece inativo;
- nenhuma credencial ou segredo foi versionado;
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada;
- Delivery, pagamento, ledger e atribuição de Rider continuam fora do estágio concluído.

## 2. Entrega Stock integrada

### PostgreSQL

- migration `database/postgres/migrations/031_stock_inventory_reservations.sql`;
- rollback `database/postgres/rollbacks/031_stock_inventory_reservations.sql`;
- `stock.inventory_items` como fonte autoritativa de saldo;
- `stock.stock_reservations` como fonte autoritativa de reservas;
- saldo disponível gerado no banco;
- trigger que deriva `active/depleted` pela disponibilidade;
- constraints contra saldo negativo;
- índices para produto, empresa, pedido, status e expiração.

### Transações e segurança

- reserva com `FOR UPDATE`;
- expiração com `FOR UPDATE SKIP LOCKED`;
- idempotência por usuário, empresa e chave;
- conflito quando a mesma chave recebe corpo diferente;
- confirmação, liberação e expiração idempotentes;
- isolamento por empresa;
- expiração global protegida pelo escopo `stock:reservations:expire`;
- auditoria e outbox no mesmo limite transacional.

### Contratos e testes

- API Stock versão `0.3.0`;
- OpenAPI especializado preservado pelo scaffold;
- contrato `modules/stock/RESERVATION_CONTRACT.md` versão `0.2.2`;
- testes de concorrência em PostgreSQL 16 real;
- migration aplicada em banco limpo;
- rollback comprovado no banco efêmero;
- CI, Security, Database, OpenAPI, Docker Compose, Valley DAST e A1 Admin verdes no head `cb36a00d8ba0b08a62fd7fcd7a36702ba4c6f8af`;
- diff revisado sem segredo literal.

## 3. Pendências abertas confirmadas

| Prioridade | Issue | Situação | Próxima decisão |
|---|---:|---|---|
| P0 executável | #78 | Checkout idempotente agora desbloqueado pela fundação Stock | Implementar em branch própria, mantendo a flag desligada até homologação |
| Coordenação | #51 | Orquestra Marketplace → Stock → Delivery | Registrar Stock concluído e avançar somente para checkout |
| Alta | #89 | Fonte produtiva AIO Admin AppDeploy ainda precisa convergir com o repositório | Auditar e versionar a fonte operacional sem apagar o pacote de design |
| P0 sensível | #47 | Health Watch + SafeZone | Exige consentimento, antiabuso, auditoria e validação legal/técnica antes de piloto |
| Produto | #55 | Implantação progressiva da Rodada 004 | Executar por ideias aprovadas e feature flags |
| Programa | #39 | Onda de inovação nos 24 módulos | Continuar por ondas autorizadas; Vision excluído |
| Bloqueada | #69 | Fonte funcional da Rodada 002 ausente | Não reconstruir silenciosamente; localizar ou obter a fonte oficial |
| Alta | #24 | Pop-up Promoção do Dia | Revalidar escopo atual antes de nova implementação para evitar duplicidade |

## 4. Próxima tarefa autorizável

A próxima evolução técnica coerente é a issue #78:

```text
Marketplace -> Stock -> Checkout idempotente -> Pagamento validado -> Delivery
```

A implementação deve consumir exclusivamente uma reserva válida do Stock.

Escopo mínimo da próxima branch:

1. revalidar carrinho, loja, publicação, preço e disponibilidade no servidor;
2. exigir chave idempotente;
3. criar snapshot imutável de itens e valores;
4. calcular total BRL no backend;
5. criar pedido idempotente somente após reserva válida;
6. impedir cobrança duplicada;
7. manter estados de pagamento explícitos;
8. liberar reserva em falha ou cancelamento;
9. confirmar baixa somente após pagamento validado;
10. registrar auditoria, correlação e outbox.

## 5. Proibições persistentes

- não fazer push direto na `main`;
- não usar `marketplace.products.stock_quantity` como saldo autoritativo;
- não criar estoque paralelo no Marketplace;
- não criar pedido sem reserva válida;
- não ativar `MARKETPLACE_CHECKOUT_V1_ENABLED` antes de implementação, testes e homologação;
- não lançar valores fora do ledger;
- não iniciar Delivery antes de checkout e pagamento comprovados;
- não atribuir Rider nesta etapa;
- não reativar Vision;
- não versionar tokens, chaves, senhas ou DSNs de produção;
- não integrar com workflow vermelho, ausente ou em processamento;
- não reutilizar evidência de um head SHA anterior;
- não executar rollback destrutivo automaticamente em produção.

## 6. Procedimento obrigatório para a próxima evolução

1. verificar novamente PRs, issues, commits, branches e workflows;
2. confirmar que não surgiu gate vermelho ou merge pendente;
3. criar branch a partir da `main` atual;
4. atualizar o contrato antes de ligar qualquer feature flag;
5. implementar o menor incremento transacional completo;
6. executar testes unitários, integração real e segurança;
7. revisar o diff completo;
8. verificar ausência de segredos;
9. abrir PR em rascunho;
10. corrigir todas as falhas no mesmo ciclo;
11. validar todos os gates no mesmo head SHA;
12. marcar pronta para revisão;
13. executar Squash and Merge com `expected_head_sha`;
14. confirmar o commit consolidado e atualizar esta tarefa.

## 7. Critério de verdade

Código, plano, comentário ou documento isolado não equivalem a entrega funcional. Uma tarefa somente pode ser considerada concluída com:

- implementação no ambiente correto;
- teste reproduzível;
- evidência dos workflows;
- diff revisado;
- ausência de segredos;
- commit e pull request identificados;
- integração por Squash and Merge quando aplicável.

## 8. Histórico resumido

| Versão | Data | Alteração |
|---|---|---|
| 2.0 a 2.9 | 28–29/07/2026 | Evoluções anteriores, contratos, branding e aplicações. |
| 3.0 | 30/07/2026 | PRs #90/#91 integradas e fundação Stock implementada. |
| 3.1 | 30/07/2026 | Migration Stock corrigida para 031 e falhas de revisão consolidadas. |
| 3.2 | 30/07/2026 | PR #92 e issue #83 concluídas; pendências reclassificadas e issue #78 definida como próxima etapa. |
