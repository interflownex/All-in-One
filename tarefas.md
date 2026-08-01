# Tarefas da IA Desenvolvedora

**Versão:** 5.1  
**Data e hora:** 01/08/2026 04:10, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Marco integrado:** PR `#108`, commit `1d05e56ca3bc1a66eb1e280743db24308d6da1b1`  
**Branch desta atualização:** `codex/finalizar-status-pos-merge-20260801`  
**Issue-mãe:** `#51`  
**Prioridade funcional:** `#95`  
**Bloqueio externo:** `#107`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado autoritativo

- A PR #108 foi integrada por Squash and Merge após Continuous Integration, Security, Docker Compose Health Gate e A1 Admin Template ficarem verdes no mesmo head SHA.
- O único repositório oficial é `interflownex/All-in-One`.
- Valley é produto e conjunto de aplicativos internos do monorepo oficial.
- A política mandatória está em `config/autonomy/repository_scope_policy.json`.
- O gate `scripts/validate_repository_scope.py` e seus testes impedem regressão de escopo.
- Vision permanece inativo e fora do catálogo vigente.
- Merge Commit e Rebase Merge permanecem desativados; Squash and Merge é o único método habilitado.
- As issues #51, #55 e #95 foram reconciliadas com o estado real integrado.
- Nenhuma migration, lockfile, feature flag, ativo de marca ou código funcional foi alterado pela PR #108.

## 2. Próxima prioridade executável: issue #95

Implementar a camada financeira produtiva do checkout em branch exclusiva, mantendo `MARKETPLACE_CHECKOUT_V1_ENABLED=false`.

Escopo obrigatório:

1. interface de PSP independente de fornecedor;
2. sandbox separado de produção;
3. webhooks com assinatura, timestamp, proteção contra replay e idempotência;
4. autorização, captura, cancelamento, estorno e chargeback;
5. ledger de liquidação e liberação condicionada de escrow;
6. reconciliação PSP × pedido × escrow × ledger;
7. bloqueio automático diante de divergência;
8. credenciais somente em Secret Manager;
9. dados brutos de cartão fora do sistema;
10. testes unitários, integração, contrato, banco limpo e sandbox.

Delivery produtivo e atribuição de Rider permanecem bloqueados até pagamento comprovado e reconciliado.

## 3. Bloqueio externo: issue #107

O deploy GKE autentica no Google Cloud, mas recebe HTTP 403 porque o faturamento do projeto `all-in-one-498012` está desativado.

Regras:

- não enfraquecer o workflow;
- não usar `continue-on-error`;
- não simular sucesso;
- não contornar billing ou IAM;
- após habilitação legítima do faturamento, repetir o deploy e exigir rollout verde no mesmo SHA.

## 4. Auditoria obrigatória da máquina local

O diretório WSL `/home/eretazan/all-in-one` não esteve montado nesta execução. Logo, staged, unstaged, untracked, exclusões e commits locais não foram presumidos nem alterados.

Executar no host WSL, antes de pull, sincronização, commit ou descarte:

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

Se houver mudanças, preservar antes de reorganizar:

```bash
timestamp="$(date +%Y%m%d-%H%M%S)"
git branch "backup/pre-audit-$timestamp" HEAD
git diff > "/tmp/all-in-one-worktree-$timestamp.patch"
git diff --cached > "/tmp/all-in-one-index-$timestamp.patch"
```

Até concluir a auditoria local, é proibido executar `git pull`, `git reset --hard`, `git clean` destrutivo, descartar arquivos, commitar exclusões em massa, fazer push ou usar “Sincronizar Alterações”.

## 5. Branches remotas antigas

As branches divergentes devem ser classificadas como integrada/substituída, histórica/backup, aproveitável por extração seletiva, duplicada/insegura ou conflitante.

- Nunca fazer merge direto de branch obsoleta.
- Nunca trazer lockfiles antigos sem reinstalação e auditoria.
- Nunca reutilizar migrations 031 ou 032.
- A branch `feature/primicias-selecionadas-v1` contém migration 031 incompatível e só pode servir como fonte de requisitos ou trechos reconstruídos sobre a `main` atual.

## 6. Ordem mandatória de evolução

1. integrar esta atualização pós-merge com gates verdes;
2. auditar o worktree local sem ações destrutivas;
3. executar a issue #95;
4. resolver externamente a issue #107;
5. consolidar a fonte produtiva do AIO Admin na issue #89;
6. revisar branches antigas por extração seletiva;
7. avançar Delivery e Rider somente após o gate financeiro;
8. manter Vision inativo e flags de risco desligadas até homologação.

## 7. Critérios permanentes

- nenhuma alteração direta na `main`;
- integração somente por Squash and Merge;
- gates verdes no mesmo head SHA;
- nenhuma credencial ou segredo no Git;
- nenhuma exclusão em massa sem inventário e justificativa;
- nenhuma tarefa concluída apenas pela existência de código ou documento;
- documentação, testes, segurança, rollback e evidência no ambiente correto obrigatórios.

## 8. Histórico resumido

- v5.0: política de fonte única, gate de regressão e reconciliação das issues;
- v5.1: confirmação da integração da PR #108 e definição da próxima etapa autoritativa.
