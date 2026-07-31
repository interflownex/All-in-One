# Tarefas da IA Desenvolvedora

**Versão:** 3.6
**Data e hora:** 31/07/2026 18:30, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`  
**Branch:** `codex/corrigir-vscode-persistente-20260731`
**Commit-base:** `8832ea85a17099bdc33cf666248e91c2ad0d7cd6`
**Issue-mãe:** `#51`  
**Próxima dependência:** `#95`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 0. Próxima etapa reproduzível: confirmar o VS Code após a correção persistente

### Objetivo e contexto

Confirmar numa janela `WSL: Ubuntu` aberta pelo arquivo
`all-in-one.code-workspace` que o interpretador Python, o Pylance e o inspetor
de alterações iniciam sem os quatro avisos relatados em 31/07/2026. A correção
versionada cobre tanto a abertura da pasta quanto a abertura do workspace.

### Escopo e fontes de verdade

- `.vscode/settings.json`: contrato para abertura como pasta;
- `all-in-one.code-workspace`: contrato canônico para abertura como workspace;
- `.venv/bin/python` e `.python-version`: ambiente Python do repositório;
- `tests/test_vscode_workspace_contract.py`: prevenção automatizada de regressão;
- documentação oficial do VS Code sobre workspaces e configurações multi-root;
- política Git e multiagente em `config/autonomy/`.

### Pré-requisitos, sequência e prioridades

1. preservar todas as mudanças alheias já existentes no checkout;
2. abrir `all-in-one.code-workspace` diretamente em uma janela `WSL: Ubuntu`;
3. executar `Developer: Reload Window` uma única vez para descartar o estado
   antigo da janela;
4. confirmar em `Python: Select Interpreter` que `.venv/bin/python` está ativo;
5. executar `Python: Run Python File in Terminal` ou a tarefa `pytest`;
6. observar por pelo menos dois ciclos de edição/salvamento que o inspetor de
   arquivos permanece ativo;
7. reiniciar o VS Code e reabrir o mesmo workspace para provar persistência;
8. somente depois retomar a issue #95, que permanece a prioridade de produto.

### Testes e critérios de aceite

- `.venv/bin/python --version` retorna o Python esperado;
- `pytest -q tests/test_vscode_workspace_contract.py` fica verde;
- `pytest -q tests/test_gradle_vscode_contract.py` fica verde;
- `python3 scripts/validate_repository.py` não acusa regressão desta atividade;
- não aparece aviso de interpretador não resolvido;
- não aparece alerta de excesso de fontes do Pylance;
- o inspetor de alterações não é interrompido;
- não aparece convite para abrir o `.code-workspace`, pois ele já é a entrada
  canônica da sessão;
- CI e segurança ficam verdes no mesmo head SHA da pull request.

### Riscos, bloqueios e evidências esperadas

- Estado antigo do VS Code pode exigir um único recarregamento após receber a
  configuração; isso não é recorrência se sessões posteriores permanecerem
  limpas.
- O CLI standalone instalado em WSL não oferece `--remote`; não usá-lo para
  fabricar uma validação de GUI. A prova final deve vir da janela real.
- Mudanças massivas preexistentes em `.gemini/` e `.github/skills/` pertencem a
  outra atividade e não podem entrar no commit desta correção.
- Evidências: saída dos testes, SHA, URL da PR, checks do mesmo SHA e captura ou
  registro da janela `WSL: Ubuntu` sem notificações.

### Procedimento de entrega e pendências restantes

Publicar somente os arquivos desta atividade na branch indicada, abrir PR para
`main`, registrar os testes e usar Squash and Merge apenas com gates verdes.
Se a GUI não puder ser inspecionada pela sessão automatizada, registrar essa
limitação sem declarar a validação visual concluída. Após a integração, manter
a issue #95 e as demais pendências já listadas abaixo sem mudança de escopo.

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
