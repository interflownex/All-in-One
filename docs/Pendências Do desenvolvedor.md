# Pendências do Desenvolvedor

**Versão:** 5.4
**Data e hora:** 02/08/2026 02:09, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Marcos integrados:** PR `#108`, PR `#109`, PR `#114`, PR `#115`
**Issue de orquestração:** `#51`
**Classificação:** `Pendências > Técnico > Equipe Técnica`
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, Equipe Técnica, gestão e investidores

## 1. Situação consolidada

A governança, a fonte oficial única e os documentos pós-merge foram integrados com os gates obrigatórios verdes. Valley permanece dentro do monorepo oficial e Vision continua inativo.

Em 02/08/2026, o workspace foi consolidado em modo WSL local-first sem Google
Cloud pago por padrão. O workflow GKE deixou de disparar automaticamente em
`push` para `main`; ele permanece disponível somente por `workflow_dispatch`
manual com confirmação explícita de billing/IAM/APIs legítimos.

No mesmo ciclo, o Cloudflare foi validado no WSL: `wrangler`, Cloudflare Pages,
MCPs e Tunnel `all-in-one-stream` responderam corretamente. O workflow de Pages
passa a ser protegido por preflight de secrets: publica quando
`CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` existirem fora do Git, e
finaliza verde com aviso quando o token persistente ainda não estiver definido.

Concluído:

- política `config/autonomy/repository_scope_policy.json`;
- gate `scripts/validate_repository_scope.py`;
- testes de regressão;
- reconciliação das issues #51, #55 e #95;
- inclusão da issue #107 no mapa de bloqueios;
- PRs #108 e #109 integradas por Squash and Merge;
- CI, Security, Docker Compose Health Gate e A1 Admin Template verdes;
- PR #114 integrada por Squash and Merge com DNS WSL persistente, Cloudflare,
  Tailscale, Docker MCP, Antigravity, SSH e modo local-first;
- deploy GKE automático desativado no modo local-first, sem mascarar a pendência
  de billing;
- variáveis não sensíveis do GitHub configuradas para Cloudflare Pages/Tunnel e
  workflow de Pages alinhado ao `wrangler` `4.118.0`.

## 2. Estado do worktree local

O worktree WSL ativo é
`/home/eretazan/.codex/worktrees/1781507772-23398/all-in-one`. Em 02/08/2026,
após o PR #115, `main` estava alinhada a `origin/main` no commit
`5e7551111787ffa476cb420a5974c8ef30c4753b`.

Antes de qualquer nova alteração continua obrigatório verificar:

- branch e HEAD locais;
- staged, unstaged e untracked;
- exclusões preparadas;
- commits locais não publicados;
- merge, rebase ou cherry-pick em andamento;
- diferença para `origin/main`.

Nenhum pull, reset, clean, descarte, commit ou push deve ocorrer antes de preservar branch de backup e patches.

## 3. Pendências P0

### #95 — PSP, webhooks, liquidação e reconciliação

Pendente:

- interface de PSP independente;
- sandbox separado de produção;
- webhooks autenticados, temporizados, anti-replay e idempotentes;
- autorização, captura, cancelamento, estorno e chargeback;
- ledger de liquidação;
- liberação condicionada de escrow;
- reconciliação entre PSP, pedido, escrow e ledger;
- bloqueio diante de divergência;
- segredos em Secret Manager;
- testes completos e homologação.

Regra: `MARKETPLACE_CHECKOUT_V1_ENABLED=false`; Delivery produtivo e Rider bloqueados até pagamento comprovado e reconciliado.

### #107 — faturamento GCP

Bloqueio externo. O deploy GKE recebe HTTP 403 porque o faturamento do projeto `all-in-one-498012` está desativado.

Estado operacional v5.3: o workflow GKE não deve mais executar automaticamente em
`main` enquanto o workspace estiver em modo local-first. A reativação exige
execução manual com confirmação explícita de billing/IAM/APIs legítimos.

Ação necessária:

- habilitar billing legitimamente;
- confirmar IAM e APIs;
- executar manualmente o workflow GKE com `confirm_gcp_billing_enabled=true`;
- exigir rollout verde sem enfraquecer o gate.

### Cloudflare Pages — token de deploy automático

Estado operacional v5.4: Cloudflare está ativo e validado localmente, com Pages,
Tunnel e MCPs funcionais. `CLOUDFLARE_ACCOUNT_ID` foi configurado em GitHub
Secrets e as variáveis não sensíveis foram configuradas em GitHub Variables.

Pendente externo: criar ou fornecer `CLOUDFLARE_API_TOKEN` persistente,
escopado para publicação do projeto `all-in-one-web`, e salvar em GitHub Secrets.
Sem esse token, o workflow não deve falhar nem publicar; deve encerrar verde com
aviso auditável.

## 4. Pendências P1

### #89 — AIO Admin

A aplicação produtiva está publicada, mas a fonte operacional ainda precisa convergir com o repositório, preservando separação entre template visual, runtime produtivo e empacotamento Android.

### Branches divergentes

As branches antigas não são candidatas a merge direto. Trechos úteis devem ser reconstruídos sobre a `main` atual após revisão de migrations, lockfiles, segredos, branding e testes.

## 5. Pendências P2

- #47: Health Watch + SafeZone funcional em Android/Wear OS;
- #55: persistência, integrações e homologação da Rodada 004;
- #39: implementação individual das inovações dos 24 módulos;
- #69: bloqueada até a fonte funcional da Rodada 002 ser versionada;
- #24: comprovação integral da Promoção do Dia no Stitch, código e E2E;
- #51: continuidade Finance → Delivery → Rider conforme dependências.

## 6. Regras permanentes

1. único repositório oficial: `interflownex/All-in-One`;
2. Valley interno ao monorepo;
3. Vision inativo;
4. nenhuma escrita direta na `main`;
5. somente Squash and Merge;
6. gates verdes no mesmo head SHA;
7. nenhuma credencial no Git;
8. nenhuma exclusão em massa sem inventário;
9. nenhuma branch antiga mesclada diretamente;
10. migrations 031 e 032 não podem ser reutilizadas;
11. checkout produtivo desligado até homologação financeira;
12. nenhuma tarefa concluída sem teste, evidência, documentação e rollback.

## 7. Ordem operacional atual

1. manter `main` sem workflows pagos automáticos no modo local-first;
2. executar a issue #95;
3. resolver a issue #107 externamente antes de qualquer deploy GKE real;
4. executar a issue #89;
5. revisar branches antigas por extração seletiva;
6. avançar Delivery e Rider após o gate financeiro.

## 8. Histórico

- v5.0: correção mandatória de escopo, documentos, issues e gate de regressão;
- v5.1: registro pós-merge;
- v5.2: remoção da autorreferência e definição da fila operacional real.
- v5.3: registro do modo local-first pós-PR #114 e bloqueio de deploy GKE
  automático até billing/IAM/APIs legítimos.
