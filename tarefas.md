# Tarefas da IA Desenvolvedora

**Versão:** 3.7
**Data e hora:** 31/07/2026 18:48, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/corrigir-vscode-persistente-20260731`
**Commit-base:** `9ec1afab1e9f7f209d6844d82f8f23de96f15f84`
**Issue-mãe:** `#51`  
**Próxima dependência:** `#95`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 0. Próxima etapa reproduzível: validar a sincronização das skills de dados

### Objetivo e contexto

Confirmar em CI que a reorganização do catálogo de skills de dados mantém os
manifestos `.gemini/skills` e `.github/skills` coerentes, sem scripts ou
documentos com permissões executáveis indevidas. A migração remove skills
legadas de AlloyDB, Cloud SQL, Firestore e Spanner, separa BigQuery em skills
especializadas e preserva o módulo Vision inativo.

### Escopo e fontes de verdade

- `.gemini/skills/.datacloud_skills_manifest`: catálogo principal atualizado;
- `.github/skills/.datacloud_skills_manifest`: catálogo espelhado;
- `.gemini/skills/bigquery-*`: skills especializadas e referências canônicas;
- `.github/skills/bigquery-*`: cópias destinadas ao GitHub;
- `scripts/validate_innovation_wave.py`: gate local da onda de inovação;
- políticas Git, Google e multiagente em `config/autonomy/`.

### Pré-requisitos, sequência e prioridades

1. preservar o sub-repositório `testcontainers-cloud-java-example` e outras
   mudanças alheias fora do commit;
2. comparar os dois manifestos e confirmar os destinos de cada skill;
3. verificar que arquivos Markdown e `OWNERS` usam modo `0644`;
4. executar o validador de inovação pela `.venv`;
5. executar o validador geral e classificar separadamente falhas de baseline;
6. revisar o diff, exclusões e varredura de segredos;
7. validar os workflows no mesmo head SHA da pull request;
8. somente depois retomar a issue #95, prioridade de produto ainda aberta.

### Testes e critérios de aceite

- `.venv/bin/python scripts/validate_innovation_wave.py` retorna `status: ok`;
- `git diff --cached --check` não encontra erros;
- nenhum documento ou arquivo `OWNERS` novo fica executável;
- `scripts/validate_innovation_wave.py` preserva modo `0755`;
- a varredura do diff não encontra chaves privadas nem tokens conhecidos;
- as exclusões correspondem somente às skills legadas substituídas;
- `python3 scripts/validate_repository.py` tem suas falhas globais comparadas
  com o baseline e não pode ser declarado verde enquanto elas persistirem;
- CI e segurança ficam verdes no mesmo head SHA da pull request.

### Riscos, bloqueios e evidências esperadas

- O validador geral ainda acusa baseline de 24/25 módulos, branding e contratos
  locais de Google/Stitch; essas falhas não podem ser ocultadas nem declaradas
  resolvidas por esta sincronização.
- O volume de exclusões exige revisão do diff e dos manifestos antes do merge.
- O sub-repositório `testcontainers-cloud-java-example` permanece sujo e fora
  do stage desta entrega.
- Evidências: saídas dos validadores, resumo do diff, SHA, URL da PR e checks
  obrigatórios executados no mesmo SHA.

### Procedimento de entrega e pendências restantes

Publicar somente os catálogos, skills, referências e este registro na branch
indicada; abrir ou atualizar a PR para `main`, registrar testes e usar Squash
and Merge apenas com gates verdes. Se `validate_repository.py` continuar
falhando pelo baseline conhecido, registrar cada falha e tratá-la em atividade
própria, sem enfraquecer o gate. Após a integração, manter a issue #95 e as
demais pendências abaixo sem mudança de escopo.

## 1. Estado consolidado

- PR #90 integrada no commit `fb47ea5f2a064fd39538cc7f89b51156dfd3f1ce`;
- PR #91 integrada no commit `c566d5dc9f45192b05f4bb8871dbee7ca0827a93`;
- PR #92 integrada no commit `692ee05b1ca8e234d6875a1dfb153212a016ddb6`;
- PR #93 integrada no commit `87e3957002f3c9f5bde74e1f3ee56c3d4f79d1c8`;
- PR #94 integrada no commit `c6da2cb578a7edc7bdfd9c9b2182ff6aeec6c239`;
- issue #83 concluída: fundação transacional Stock;
- issue #78 concluída: checkout idempotente com Stock e Wallet;
- issue #95 aberta: homologação de PSP, webhooks, liquidação e reconciliação;
- issue-mãe #51 atualizada com o novo marco;
- Vision permanece inativo;
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada;
- nenhuma credencial ou DSN de produção foi versionada;
- Delivery e Rider permanecem não iniciados;
- nenhum valor foi liquidado ao lojista nesta etapa.

## 2. Etapas técnicas concluídas

### Reconciliação do trabalho local

- o checkout principal foi avançado por fast-forward de `7a41ee9` para
  `05564ff`, ficando idêntico a `origin/main`;
- o estado legado com remoções destrutivas foi preservado somente na branch
  local `recovery/local-main-20260730`, sem publicação;
- a migração incompleta de skills foi preservada somente na branch local
  `recovery/flutter-gemini-20260730`, sem publicação;
- as evoluções aproveitáveis foram reaplicadas sobre a `main` atual;
- foram adicionadas consultas de avaliações, série comercial, perfil CRM e
  resolução empresarial de disputas, com rotas correspondentes no API Hub;
- o acesso CRM foi limitado ao próprio usuário autenticado;
- o identificador empresarial foi alinhado a `Actor.business_id` e ao cabeçalho
  `X-Business-Id`;
- o worker de notificação simulado foi rejeitado e não integra esta entrega.

### Testes e critérios de aceite da reconciliação

- `ruff check` nos arquivos novos e testes: aprovado;
- testes recuperados e endurecidos: `7 passed`;
- gate de artefatos gerados: aprovado após isolar as rotas em
  `commercial_routes.py` e registrar sua inclusão no scaffold;
- contratos de API Hub, BI, Business, CRM e Marketplace: `10 passed, 1 skipped`;
- compilação Python dos cinco módulos alterados: aprovada;
- pendências preexistentes de branding e `validate_repository.py` permanecem
  bloqueios de baseline e devem ser tratadas em atividade exclusiva antes de
  qualquer declaração de conformidade integral;
- aceitar somente PR com CI, segurança e checks obrigatórios verdes no mesmo
  SHA; não promover os commits locais de recuperação.

```text
Marketplace catálogo/carrinho: concluído
Stock transacional: concluído
Checkout idempotente: concluído
Wallet interna + escrow hold: concluído tecnicamente
Ledger de retenção: concluído
Compensação de falha financeira: concluída
Liquidação produtiva/PSP: issue #95 aberta
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

## 5. Próxima dependência: issue #95

Título:

```text
[Finance Fase 1] Homologar PSP, webhooks, liquidação e reconciliação do checkout
```

Escopo obrigatório:

1. definir interface de PSP independente de fornecedor;
2. selecionar o primeiro PSP homologável;
3. validar assinatura, timestamp e replay de webhooks;
4. garantir idempotência de autorização, captura, cancelamento, estorno e chargeback;
5. preservar ledger e escrow como fontes internas de verdade;
6. implementar liquidação por partidas rastreáveis;
7. conciliar PSP, ledger, escrow e pedido;
8. bloquear liquidação diante de divergência;
9. manter credenciais em Secret Manager;
10. manter a feature flag desligada até homologação completa.

Delivery e Rider só poderão avançar após a issue #95 demonstrar pagamento produtivo, compensação e reconciliação confiáveis.

## 6. Issues abertas que continuam independentes

- #95: PSP, webhooks, liquidação e reconciliação;
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

1. executar a issue #95 em branch exclusiva;
2. manter a feature flag desligada;
3. preservar PSP sandbox e produção separados;
4. manter a issue #89 como próxima frente independente após o gate financeiro ou em branch isolada sem misturar escopos;
5. abrir cada PR em rascunho;
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
| 3.4 | 30/07/2026 | PR #94 e issue #78 concluídas; issue #95 aberta como próxima dependência financeira. |
| 3.5 | 30/07/2026 | Trabalho local reconciliado com `origin/main`; código válido reaplicado e regressões arquivadas apenas localmente. |
| 3.6 | 31/07/2026 | Contrato persistente do VS Code para interpretador, Pylance, observador de arquivos e abertura canônica do workspace. |
| 3.7 | 31/07/2026 | Migração do catálogo de skills de dados reconciliada, permissões normalizadas e validação reproduzível registrada. |
