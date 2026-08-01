# Plano de Ação Codex v5.2

**Data e hora:** 01/08/2026 04:18, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## Sequência real de trabalho

### 1. Auditar o worktree local

- verificar branch, HEAD, staged, unstaged, untracked e exclusões;
- verificar commits locais e operações Git em andamento;
- executar apenas `git fetch --prune`, sem pull;
- preservar branch de backup e patches;
- classificar cada alteração antes de qualquer commit.

### 2. Executar a issue #95

- contrato PSP independente;
- sandbox separado de produção;
- webhooks autenticados e idempotentes;
- autorização, captura, cancelamento, estorno e chargeback;
- liquidação e reconciliação;
- checkout produtivo desligado até homologação;
- Delivery e Rider bloqueados até pagamento comprovado.

### 3. Resolver a issue #107

- habilitar billing GCP legitimamente;
- confirmar IAM e APIs;
- repetir o deploy;
- exigir rollout verde;
- não mascarar HTTP 403.

### 4. Executar a issue #89

- convergir a fonte produtiva do AIO Admin;
- preservar template e Android;
- documentar publicação e rollback;
- repetir E2E e gates.

### 5. Revisar branches antigas

- comparar com a `main`;
- preservar backups;
- extrair apenas código exclusivo válido;
- bloquear migrations 031/032 e lockfiles obsoletos;
- nunca fazer merge direto.

## Critérios permanentes

- repositório oficial único;
- Vision inativo;
- sem segredos;
- sem escrita direta na `main`;
- Squash and Merge;
- gates verdes no mesmo head SHA;
- rollback e evidência obrigatórios.
