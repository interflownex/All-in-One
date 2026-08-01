# Pendências do Desenvolvedor

**Versão:** 5.2  
**Data e hora:** 01/08/2026 04:18, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Marcos integrados:** PR `#108` e PR `#109`  
**Issue de orquestração:** `#51`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Públicos impactados:** Pessoa Física, Pessoa Jurídica, Equipe Técnica, gestão e investidores

## 1. Situação consolidada

A governança, a fonte oficial única e os documentos pós-merge foram integrados com os gates obrigatórios verdes. Valley permanece dentro do monorepo oficial e Vision continua inativo.

Concluído:

- política `config/autonomy/repository_scope_policy.json`;
- gate `scripts/validate_repository_scope.py`;
- testes de regressão;
- reconciliação das issues #51, #55 e #95;
- inclusão da issue #107 no mapa de bloqueios;
- PRs #108 e #109 integradas por Squash and Merge;
- CI, Security, Docker Compose Health Gate e A1 Admin Template verdes.

## 2. Pendência imediata: worktree local

O caminho `/home/eretazan/all-in-one` não esteve montado nesta execução. Ainda é obrigatório verificar:

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

Ação necessária:

- habilitar billing legitimamente;
- confirmar IAM e APIs;
- repetir o workflow;
- exigir rollout verde sem enfraquecer o gate.

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

1. auditar o worktree local;
2. executar a issue #95;
3. resolver a issue #107 externamente;
4. executar a issue #89;
5. revisar branches antigas por extração seletiva;
6. avançar Delivery e Rider após o gate financeiro.

## 8. Histórico

- v5.0: correção mandatória de escopo, documentos, issues e gate de regressão;
- v5.1: registro pós-merge;
- v5.2: remoção da autorreferência e definição da fila operacional real.
