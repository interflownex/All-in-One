# Execução de Pendências v6.4

**Data e hora:** 03/08/2026 17:48, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Classificação:** `Pendências > Técnico`  
**Público-alvo:** Equipe Técnica  
**Base inicial:** `c2a3d97d8c1d65e0493dbe118ee261950ff8eb30`

## 1. Visão geral

A publicação gratuita do APK Valley Rider Flutter está concluída e validada. A operação comercial completa continua bloqueada pela homologação financeira da issue #95. Esta rodada executou as correções de governança que já estavam maduras e iniciou a primeira correção isolada de segurança do webhook Mercado Pago.

## 2. Ações executadas

### PR #119 e issue #69

- PR #119 retirada do estado draft;
- revisão do escopo de quatro arquivos, sem exclusões e sem segredos;
- confirmação dos gates `Continuous Integration`, `Security` e `Docker Compose Health Gate` no mesmo head SHA;
- integração por `Squash and Merge` com `expected_head_sha`;
- commit integrado: `e351f3c67969b3f884692c8f3a75f86e014675ad`;
- issue #69 atualizada de `bloqueada_por_fonte_ausente` para `desbloqueada_fonte_versionada`;
- a issue permanece aberta porque PostgreSQL, autenticação, RBAC/ABAC, auditoria, sincronização e homologação ainda não foram implementados.

### Mercado Pago

- criada branch `codex/corrigir-webhook-mercado-pago-timestamp-20260803`;
- normalização da janela temporal para aceitar os formatos documentados em segundos e milissegundos;
- preservação do timestamp original no manifesto HMAC;
- rejeição explícita de timestamp negativo ou inválido;
- testes de regressão para assinatura recente e expirada nos dois formatos;
- checkout permanece desligado por feature flag;
- nenhum endpoint de webhook, liquidação ou reconciliação foi declarado como concluído.

## 3. Estado das pendências por prioridade

### P0 — Finance produtivo, issue #95

Concluído parcialmente:

- adaptador inicial Mercado Pago;
- criação de preferência Checkout Pro;
- host da API restrito ao domínio oficial;
- idempotency key na criação de preferência;
- verificador HMAC isolado;
- migration 033 habilitando `payment_method=mercado_pago`;
- feature flag desligada.

Ainda obrigatório:

1. endpoint autenticado de webhook;
2. migration 034 para eventos externos e prevenção de replay;
3. processamento assíncrono por outbox/worker;
4. consulta autoritativa do pagamento no provedor;
5. validação de valor, moeda, pedido, checkout, tenant e referência externa;
6. estados de pagamento e transições idempotentes;
7. reconciliação PSP × pedido × Stock × escrow × ledger;
8. cancelamento, estorno total/parcial e chargeback;
9. split/marketplace e OAuth de vendedores, quando adotados;
10. sandbox separado de produção;
11. segredos em cofre externo;
12. testes de banco limpo, compensação, falha e replay;
13. homologação formal antes de ativar `MARKETPLACE_CHECKOUT_V1_ENABLED`.

### P0 externo — GKE, issue #107

Bloqueio administrativo confirmado:

- billing do projeto `all-in-one-498012` desativado;
- autenticação GCP funciona;
- falha ocorre em `Get GKE credentials` com HTTP 403;
- deploy permanece manual e protegido.

Ação externa necessária:

1. habilitar billing legitimamente;
2. confirmar IAM, APIs, cluster e região;
3. conferir secrets exigidos;
4. executar workflow manual com confirmação explícita;
5. validar rollout no SHA vigente.

### P1 — AIO Admin, issue #89

- separar fonte visual, runtime produtivo AppDeploy e wrapper Android;
- documentar versão, URL, publicação e rollback;
- preservar autenticação, auditoria, notificações e tempo real;
- repetir cinco jornadas E2E e validação Android.

### P1 — Promoção do Dia, issue #24

- comprovar uso do projeto e screen ID corretos no Stitch;
- validar modal real, frequência, acessibilidade, CTA e métricas idempotentes;
- anexar evidências visuais e E2E após login.

### P2 — Rodadas e módulos

- issue #69: persistência autenticada da Rodada 002;
- issue #55: implantação progressiva da Rodada 004;
- issue #47: Health Watch + SafeZone;
- issue #39: inovações dos 24 módulos;
- issue #51: sequência Finance → Delivery → Rider.

## 4. Ordem operacional aprovada

1. integrar a correção de timestamp somente com gates verdes;
2. implementar webhook e armazenamento idempotente em PR própria;
3. implementar confirmação autoritativa e transições de pagamento;
4. implementar ledger, escrow, reconciliação, estorno e chargeback;
5. homologar sandbox e manter produção desligada;
6. liberar Delivery somente após pagamento confirmado e reconciliado;
7. liberar atribuição operacional de Rider somente após Delivery produtivo;
8. resolver GKE apenas quando billing/IAM/APIs estiverem legítimos;
9. consolidar AIO Admin e demais pendências sem quebrar a sequência financeira.

## 5. Regras de segurança e governança

- nenhuma escrita direta na `main`;
- somente `Squash and Merge`;
- usar `expected_head_sha` no merge;
- gates verdes no mesmo head SHA;
- nenhuma credencial no Git;
- nenhuma exclusão em massa sem inventário;
- migrations 031, 032 e 033 não podem ser reutilizadas;
- checkout produtivo permanece desligado;
- código integrado não equivale a homologação produtiva;
- Vision permanece excluído;
- toda entrega precisa de teste, evidência, documentação e rollback.

## 6. Critério desta rodada

Esta rodada é concluída quando:

- a PR #119 estiver integrada e a issue #69 reconciliada;
- a correção de timestamp estiver em PR com testes e gates;
- as pendências financeiras e externas estiverem documentadas sem mascaramento;
- nenhuma feature financeira for ativada antes da homologação completa.
