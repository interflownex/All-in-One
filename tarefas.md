# Tarefas da IA Desenvolvedora

**Versão:** 4.0
**Data e hora:** 30/07/2026 14:38, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/corrigir-referencias-marca-20260730`
**Commit-base:** `b04af1dd235fee24e504e0dc79a296ed4832d7e0`
**Issue-mãe:** `#51`  
**Próxima dependência:** `#95`  
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

## 9. Auditoria de PRs, commits, merges e coerência relacional

### Objetivo, contexto e escopo

- reconciliar a `main`, branches, PRs, merges, workflows e trabalhos locais;
- preservar qualquer alteração não versionada antes de classificá-la;
- corrigir o gerador relacional para refletir o código atual e regenerar sua
  documentação derivada;
- não incorporar branches antigas, arquivos gerados ou código de segurança
  superado sem comparação semântica e teste reproduzível.

### Fontes de verdade e pré-requisitos

- Git local, `origin/main`, API do GitHub e histórico de checks;
- `scripts/generate_data_audit_inventory.py`;
- `scripts/validate_data_audit_delivery.py`;
- `docs/data-audit/` e seus artefatos derivados;
- lock de sincronização multiagente obrigatório antes de editar;
- credenciais GCP válidas fora do Git para liberar o deploy GKE.

### Resultado e evidências

- nenhuma PR aberta foi localizada no início da atividade;
- `main` local e `origin/main` estavam iguais em `8832ea8`;
- CI, Security, Compose e Git Sync estavam verdes nesse SHA;
- Deploy to GKE permanecia vermelho porque `GCP_WIP` e `GCP_SA_EMAIL` não
  estavam disponíveis no ambiente GitHub, sem correção segura no código;
- trabalhos locais Android/Telegram e logging foram preservados em branches
  `recovery/*`, sem promoção de implementações antigas;
- a auditoria de dados passou a carregar `domain_rules.py` sem acionar o
  `shared.__init__` nem exigir FastAPI para geração estática;
- rotas vazias de `APIRouter` passaram a herdar o prefixo real;
- o inventário de browser storage foi alinhado às chaves produtivas atuais;
- o alias relacional `jobs:jobpostings -> job_postings` foi mantido;
- gerador reproduzido: 32 migrations, 167 tabelas, 2.367 campos, 586 relações,
  166 endpoints, 263 superfícies e 946 ações;
- validador nativo aprovado, compilação Python aprovada, `git diff --check`
  aprovado e 22 testes do contrato executados diretamente e aprovados;
- a tentativa de instalar `pytest` via `uv` foi interrompida após repetidas
  falhas de rede; não foi usada como evidência de aprovação.
- a correção 3.7 criou um pool e provider OIDC exclusivos para GitHub Actions,
  vinculou a conta de serviço de deploy, configurou `GCP_WIP` e
  `GCP_SA_EMAIL` nos GitHub Secrets e atualizou o workflow para GKE regional;
- React Router foi elevado a 7.18.2 nas três SPAs, Vite Admin a 8.0.16,
  PostCSS a no mínimo 8.5.18 e `brace-expansion` a no mínimo 5.0.7;
- o classpath Gradle passou a impor pisos corrigidos para Netty, Bouncy Castle,
  jose4j, JDOM, Commons Lang, HttpClient, Protobuf e Guava;
- tokens, refresh tokens, identificadores e email da sessão Valley deixaram de
  ser persistidos em `localStorage`; a sessão agora permanece somente em
  memória e chaves legadas são removidas;
- 29 testes focados foram executados diretamente e aprovados; os validadores de
  release Android e de auditoria de dados também foram aprovados.
- o primeiro gate remoto `web-template` da PR #100 identificou inconsistência
  entre `package.json` e `package-lock.json` no Admin; o lockfile foi
  regenerado pelo resolvedor oficial do npm e a instalação bloqueada deverá ser
  revalidada no novo head SHA;
- a PR #100 foi integrada por Squash and Merge no commit `0199103`, com todos
  os gates verdes no mesmo head;
- o login federado do deploy GKE passou; a API bloqueou `get-credentials`
  exclusivamente porque o faturamento do projeto `all-in-one-498012` está
  desabilitado;
- o plugin Foojay foi removido de `settings.gradle.kts`: os workflows já
  provisionam Temurin 17 explicitamente, e o plugin era a única raiz do grafo
  transitivo associado aos 48 alertas Maven restantes;
- a varredura pós-merge confirmou zero alertas Dependabot abertos;
- duas referências não canônicas de marca detectadas pelo workflow pós-merge
  foram restauradas para os ativos oficiais autorizados, sem alterar os
  binários nem a composição das marcas;

### Sequência, prioridades e critérios de aceite

1. publicar esta branch e abrir PR para `main`;
2. verificar diff, segredos e head SHA;
3. exigir todos os gates verdes no mesmo SHA;
4. executar Squash and Merge somente sem conflito ou revisão pendente;
5. confirmar `origin/main` no commit de merge;
6. comprovar o deploy GKE no commit integrado;
7. remover `origin/worktree-sync` somente após preservar a referência local e
   registrar que seus 11 commits foram substituídos por implementações atuais;
8. confirmar o fechamento automático dos alertas Dependabot e encerrar apenas
   os três alertas RSC como não utilizados, com evidência das SPAs Vite.

Aceite: artefatos regeneráveis, rotas e relações com evidência real, nenhuma
mudança local perdida, PR sem conflito, ausência de segredo e checks verdes no
mesmo SHA.

### Riscos, bloqueios e pendências restantes

- a identidade federada GKE foi provisionada; o aceite final depende do
  workflow executar contra o cluster e o RBAC reais após o merge;
- `origin/worktree-sync` continua preservada até a verificação final da PR;
- branches `recovery/*` são salvaguardas locais, não entregas candidatas a merge;
- a resolução Gradle local das novas versões foi bloqueada temporariamente por
  falha DNS/Maven; o gate Android remoto é obrigatório para aceite;
- três alertas React Router sobre RSC exigem encerramento como `not_used`
  porque as aplicações afetadas são SPAs Vite sem servidor/RSC.

### Procedimento de entrega

- commit em português baseado no diff real;
- push apenas da branch de trabalho;
- PR para `main` com testes, riscos e bloqueios;
- Squash and Merge com proteção por head SHA;
- atualização final deste documento após o commit integrado.

## 10. Histórico resumido

| Versão | Data | Alteração |
|---|---|---|
| 2.0 a 2.9 | 28–29/07/2026 | Evoluções anteriores, contratos, branding e aplicações. |
| 3.0 | 30/07/2026 | PRs #90/#91 integradas e fundação Stock implementada. |
| 3.1 | 30/07/2026 | Migration Stock corrigida para 031. |
| 3.2 | 30/07/2026 | PR #92 e issue #83 concluídas. |
| 3.3 | 30/07/2026 | PR #94 aberta para executar a issue #78. |
| 3.4 | 30/07/2026 | PR #94 e issue #78 concluídas; issue #95 aberta como próxima dependência financeira. |
| 3.5 | 30/07/2026 | Trabalho local reconciliado com `origin/main`; código válido reaplicado e regressões arquivadas apenas localmente. |
| 3.6 | 30/07/2026 | PRs, commits, merges, workflows e trabalhos locais auditados; gerador e artefatos relacionais sincronizados ao código atual. |
| 3.7 | 30/07/2026 | Identidade GKE provisionada, dependências vulneráveis elevadas, sessão Valley retirada do browser storage e branch legada preparada para encerramento. |
| 3.8 | 30/07/2026 | Lockfile do Admin regenerado após o gate remoto detectar dependências inconsistentes. |
| 3.9 | 30/07/2026 | PR #100 integrada; bloqueio externo de billing GKE isolado e resolvedor Foojay vulnerável removido. |
| 4.0 | 30/07/2026 | Dependabot zerado e referências de marca restauradas para os caminhos canônicos autorizados. |
