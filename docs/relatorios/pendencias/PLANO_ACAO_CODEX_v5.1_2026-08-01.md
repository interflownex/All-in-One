# Plano de Ação Codex v5.1

**Data e hora:** 01/08/2026 04:10, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Marco integrado:** PR #108, commit `1d05e56ca3bc1a66eb1e280743db24308d6da1b1`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## Objetivo

Manter o estado autoritativo coerente após a integração da PR #108 e avançar somente pelas dependências reais do projeto.

## Sequência obrigatória

### 1. Finalizar a documentação pós-merge

- atualizar `tarefas.md` e pendências para v5.1;
- registrar PR #108 e gates verdes;
- abrir PR exclusivamente documental;
- integrar por Squash and Merge após checks verdes.

### 2. Auditar o worktree local

No host WSL, executar inspeção sem `pull`, reset, clean, descarte ou push:

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

Se houver mudanças, criar branch de backup e patches antes de qualquer reorganização.

### 3. Executar a issue #95

- criar branch sobre a `main` limpa;
- definir contrato PSP independente;
- separar sandbox e produção;
- implementar webhooks autenticados e idempotentes;
- implementar autorização, captura, cancelamento, estorno e chargeback;
- implementar liquidação e reconciliação;
- manter checkout produtivo desligado;
- impedir Delivery/Rider antes do pagamento confirmado;
- validar Database, OpenAPI, CI, Security e Docker no mesmo SHA.

### 4. Resolver a issue #107

Ação externa legítima:

- habilitar billing no projeto GCP;
- confirmar IAM e APIs;
- repetir o deploy;
- comprovar rollout;
- não enfraquecer o workflow.

### 5. Convergir o AIO Admin

- obter fonte produtiva por canal autorizado;
- separar template, runtime e Android;
- documentar publicação e rollback;
- repetir E2E e gates.

### 6. Revisar branches antigas

- comparar cada branch com a `main`;
- preservar backups;
- extrair somente código exclusivo válido;
- reconstruir em branch nova;
- bloquear migrations 031/032 antigas e lockfiles obsoletos;
- nunca fazer merge direto.

## Critérios permanentes

- único repositório oficial;
- Vision inativo;
- sem segredos;
- sem escrita direta na `main`;
- Squash and Merge;
- todos os gates verdes no mesmo head SHA;
- rollback e evidência obrigatórios.
