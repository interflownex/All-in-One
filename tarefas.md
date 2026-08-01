# Tarefas da IA Desenvolvedora

**Versão:** 5.0  
**Data e hora:** 01/08/2026 03:52, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Branch desta correção:** `codex/corrigir-inconsistencias-mandatorias-20260801`  
**Commit-base da `main`:** `63ceb867c6342a3706e82a650e6072522facfbd7`  
**Issue-mãe:** `#51`  
**Dependência funcional prioritária:** `#95`  
**Bloqueio externo de infraestrutura:** `#107`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Fonte de verdade e escopo

- O único repositório oficial é `interflownex/All-in-One`.
- Valley é produto e conjunto de aplicativos internos deste monorepo.
- A política mandatória está em `config/autonomy/repository_scope_policy.json`.
- O gate `scripts/validate_repository_scope.py` impede regressão de escopo.
- Vision permanece inativo e fora do catálogo vigente.
- Nenhuma alteração pode ser enviada diretamente para `main`.
- Integração somente por **Squash and Merge**, com gates verdes no mesmo head SHA.

## 2. Estado confirmado

- `main`: `63ceb867c6342a3706e82a650e6072522facfbd7`;
- zero Pull Request aberta antes desta atividade;
- nove issues abertas: `#24`, `#39`, `#47`, `#51`, `#55`, `#69`, `#89`, `#95` e `#107`;
- Merge Commit desativado;
- Rebase Merge desativado;
- Squash and Merge habilitado;
- auto-merge desativado;
- 28 branches remotas divergentes preservadas porque contêm commits exclusivos;
- nenhuma branch remota antiga pode ser mesclada diretamente na `main`;
- PR #106 integrada: persistência do VS Code/WSL;
- PR #105 integrada: coerência relacional, E2E e segurança npm;
- Stock transacional integrado;
- checkout idempotente integrado;
- Wallet interna, escrow hold, ledger e compensação técnica integrados;
- `MARKETPLACE_CHECKOUT_V1_ENABLED=false` permanece obrigatório;
- nenhum valor foi liquidado ao lojista;
- Delivery produtivo e atribuição de Rider permanecem bloqueados pela issue #95.

## 3. Inconsistências corrigidas nesta atividade

1. removida a referência autoritativa a branch encerrada;
2. removida a afirmação obsoleta de que a PR #50 permanecia em rascunho sem merge;
3. atualizado o total de issues abertas de oito para nove;
4. atualizada a `main` e o commit-base atuais;
5. consolidado o repositório oficial único em política versionada;
6. criado gate automatizado contra mistura de fontes de repositório;
7. atualizada a issue #51 para refletir Marketplace, Stock e checkout já integrados;
8. atualizada a issue #55 para referenciar a entrega integrada correta;
9. registrada separação entre bloqueios corrigíveis por código e bloqueios externos.

## 4. Próxima prioridade executável: issue #95

### Objetivo

Homologar a camada financeira produtiva do checkout sem acoplar o domínio a um único provedor e sem ativar produção prematuramente.

### Escopo obrigatório

1. definir interface de PSP independente de fornecedor;
2. implementar adaptador de sandbox isolado de produção;
3. validar assinatura, timestamp e replay de webhooks;
4. garantir idempotência de autorização, captura, cancelamento, estorno e chargeback;
5. preservar ledger e escrow como fontes internas de verdade;
6. implementar reconciliação entre PSP, pedido, ledger e escrow;
7. bloquear liquidação automática diante de divergência;
8. armazenar credenciais somente em Secret Manager;
9. manter dados brutos de cartão fora do sistema;
10. manter a feature flag desligada até homologação formal.

### Testes mínimos

- autorização repetida não duplica cobrança;
- webhook válido, inválido, expirado e repetido;
- captura repetida não duplica ledger;
- cancelamento antes da captura;
- estorno total e parcial;
- chargeback com compensação;
- reconciliação sem divergência;
- divergência bloqueia liquidação;
- falha de PSP mantém pedido e Stock consistentes;
- Delivery não inicia sem pagamento comprovado;
- nenhum segredo aparece em diff, logs ou artefatos.

## 5. Bloqueio externo: issue #107

O workflow de deploy GKE autentica no Google Cloud, mas recebe HTTP 403 porque o faturamento do projeto `all-in-one-498012` está desativado.

Regras:

- não enfraquecer o workflow;
- não usar `continue-on-error`;
- não simular sucesso;
- não contornar billing ou IAM;
- após habilitação legítima do faturamento, repetir o deploy no SHA atual e exigir rollout comprovado.

## 6. Auditoria obrigatória da máquina local

O ambiente desta atividade não possui acesso ao diretório WSL `/home/eretazan/all-in-one`; portanto, o índice local e eventual commit preparado não foram alterados nem presumidos.

Antes de qualquer sincronização local, executar somente inspeção não destrutiva:

```bash
cd /home/eretazan/all-in-one

git status --short --branch
git status --porcelain=v2 --branch
git diff --stat
git diff --name-status
git diff --cached --stat
git diff --cached --name-status
git diff --cached --diff-filter=D --name-only
git diff --check
git diff --cached --check
git fetch --prune origin
git rev-list --left-right --count HEAD...origin/main
git log --oneline origin/main..HEAD
git log --oneline HEAD..origin/main
```

Até essa auditoria terminar, é proibido:

- usar “Sincronizar Alterações”;
- executar `git pull`;
- executar `git reset --hard`;
- executar `git clean` destrutivo;
- descartar arquivos;
- commitar exclusões em massa;
- fazer push da cópia local.

Se houver conteúdo preparado, preservar antes de reorganizar:

```bash
timestamp="$(date +%Y%m%d-%H%M%S)"
git branch "backup/pre-audit-$timestamp" HEAD
git diff > "/tmp/all-in-one-worktree-$timestamp.patch"
git diff --cached > "/tmp/all-in-one-index-$timestamp.patch"
```

## 7. Tratamento das branches remotas antigas

Classificar cada branch como:

1. **integrada ou substituída**: preservar referência e remover somente após prova;
2. **histórica/backup**: manter sem merge;
3. **código exclusivo aproveitável**: extrair apenas trechos válidos para branch nova baseada na `main`;
4. **duplicada ou insegura**: registrar evidência e arquivar;
5. **conflitante com migrations atuais**: nunca fazer merge direto.

A branch `feature/primicias-selecionadas-v1` contém uma migration 031 antiga e não pode ser integrada sobre as migrations 031/032 vigentes. Qualquer capacidade útil deve ser reconstruída com nova numeração e contratos atuais.

## 8. Ordem mandatória de evolução

1. concluir esta correção de governança e documentação;
2. validar a PR e os gates no mesmo SHA;
3. integrar por Squash and Merge;
4. auditar o worktree local sem ações destrutivas;
5. executar a issue #95 em branch exclusiva;
6. resolver externamente a issue #107 e comprovar deploy;
7. consolidar a fonte produtiva do AIO Admin na issue #89;
8. revisar branches antigas por reaproveitamento seletivo;
9. somente depois avançar Delivery e Rider;
10. manter Vision inativo e todas as flags de risco desligadas até homologação.

## 9. Critérios de aceite desta correção

- política do repositório oficial versionada;
- teste de regressão criado;
- documentos autoritativos sem estado obsoleto;
- issue #51 reconciliada com o código integrado;
- issue #55 reconciliada com a PR integrada;
- nenhuma credencial incluída;
- nenhuma alteração de produto ou banco;
- diff limitado a governança, documentação e testes;
- PR aberta para `main`;
- nenhum merge antes dos gates verdes.

## 10. Histórico resumido

- v4.4: reconciliação da PR #105 e orientação pós-PR #106;
- v5.0: correção mandatória do escopo oficial, documentos obsoletos, issues e gate contra regressão.
