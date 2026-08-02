# Tarefas da IA Desenvolvedora

## Versão 5.4 — Cloudflare WSL coerente e MCP sem segredo literal

**Data e hora:** 02/08/2026 00:07, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/cloudflare-wsl-coerente-20260802`
**Referência local antes do commit da entrega:** `ffb542c32850`
**Objetivo:** consolidar Cloudflare no workspace WSL com Pages, Tunnel, MCP,
DNS e documentação persistentes, sem segredos versionados ou bearer literal em
cadastros MCP.

### Contexto

O Cloudflare está ativo na conta `474fc26bf9c6bcf5e1a84b7f63a516d8`. O projeto
Pages confirmado é `all-in-one-web`, com domínios
`all-in-one-web-7fa.pages.dev` e `brasildesconto.com.br`. O tunnel real
confirmado por API é `all-in-one-stream`
(`7b9ce5bc-7f6e-4416-bff3-3a278ce4b96f`), em estado `healthy`, expondo
`stream.brasildesconto.com.br` para `http://127.0.0.1:8100`.

### Escopo entregue

- Criar `config/cloudflare/workspace_profile.json` como fonte local versionada.
- Atualizar `config/autonomy/cloudflare_web_policy.json` para Cloudflare Pages,
  MCP e tunnel real.
- Instalar e validar `cloudflared` `2026.7.3` no WSL.
- Instalar e validar `wrangler` `4.118.0`, autenticado na conta Cloudflare.
- Cadastrar MCPs `cloudflare-docs` e `cloudflare-api` com API por
  `CLOUDFLARE_API_TOKEN`.
- Migrar o MCP `stitch` de bearer literal para `STITCH_ACCESS_TOKEN` persistente
  no ambiente de usuário do Windows.
- Alinhar `stream.brasildesconto.com.br` e scripts Windows para API Hub `8100`,
  removendo a divergência com ERP `8107`.
- Documentar operação em `docs/CLOUDFLARE_WSL.md` e atualizar
  `docs/CLOUDFLARE_TUNNEL_STREAM.md`.

### Fontes de verdade

- `config/cloudflare/workspace_profile.json`
- `config/autonomy/cloudflare_web_policy.json`
- `config/integrations/cloudflare_stream_tunnel.json`
- `scripts/validate_cloudflare_wsl.py`
- `scripts/configure_cloudflare_wsl.py`
- Documentação oficial Cloudflare Tunnel, Wrangler e MCP Cloudflare.

### Pré-requisitos

- `CLOUDFLARE_API_TOKEN` somente fora do Git quando for usar MCP/API token.
- `STITCH_ACCESS_TOKEN` persistido como variável de usuário do Windows.
- `CLOUDFLARE_TUNNEL_TOKEN` somente fora do Git se for ativar réplica systemd no
  WSL.
- Serviço local do API Hub respondendo em `http://127.0.0.1:8100` para tráfego
  de aplicação.

### Sequência de execução

1. Validar estado Cloudflare: `python3 scripts/validate_cloudflare_wsl.py`.
2. Aplicar MCPs locais: `python3 scripts/configure_cloudflare_wsl.py --apply`.
3. Validar contrato: `.venv/bin/python -m pytest --capture=no -q tests/test_cloudflare_wsl_configuration.py tests/test_windows_script_contracts.py`.
4. Validar repo: `python3 scripts/validate_repository.py`.
5. Publicar alterações em branch de trabalho e abrir ou atualizar PR para
   `main`.

### Prioridades

1. Não versionar tokens, chaves, `cert.pem` ou credenciais `*.json`.
2. Manter `stream.brasildesconto.com.br` em `http://127.0.0.1:8100`.
3. Não publicar SSH, PostgreSQL, MongoDB, RabbitMQ ou Redis via Cloudflare
   Tunnel.
4. Usar `api.brasildesconto.com.br` apenas após definir DNS e política de acesso.

### Testes e evidências

- `python3 -m py_compile scripts/configure_cloudflare_wsl.py scripts/validate_cloudflare_wsl.py scripts/validate_repository.py`
- `.venv/bin/python -m pytest --capture=no -q tests/test_cloudflare_wsl_configuration.py tests/test_windows_script_contracts.py`
- `python3 scripts/validate_repository.py`
- `python3 scripts/validate_cloudflare_wsl.py`
- `docker compose -f infra/docker/docker-compose.yml config --quiet`
- `docker info --format '{{json .ServerVersion}}'`
- `codex mcp list` sem bearer literal para `stitch`.

### Critérios de aceite

- Validador Cloudflare confirma `cloudflared`, `wrangler`, Pages, MCPs,
  conectividade `region1.v2.argotunnel.com:7844`, API Cloudflare e tunnel
  `all-in-one-stream` `healthy`.
- Testes específicos e validador geral passam.
- `stream.brasildesconto.com.br` resolve por DNS público.
- `api.brasildesconto.com.br` permanece reservado, sem declarar publicação
  inexistente.
- Nenhum segredo Cloudflare ou Stitch é versionado.

### Riscos, bloqueios e pendências restantes

- A leitura de registros DNS pela API retornou `Authentication error` com o
  OAuth atual do `wrangler`; portanto a validação DNS autoritativa fica limitada
  à resolução pública e ao estado do Tunnel até existir token com `DNS Read`.
- `api.brasildesconto.com.br` não resolve hoje e não deve ser tratado como ativo.
- A réplica systemd no WSL permanece opcional e só pode ser instalada com
  `CLOUDFLARE_TUNNEL_TOKEN` fora do Git.
- Se o token Windows `STITCH_ACCESS_TOKEN` for rotacionado, recriar a variável de
  usuário antes de reiniciar o Codex.

### Procedimento de entrega

Versionar somente os arquivos desta atividade, preservar mudanças preexistentes
fora do escopo, executar push da branch de trabalho, abrir ou atualizar PR para
`main` e registrar que o merge deve ser feito exclusivamente por Squash and
Merge após gates verdes.

### Histórico resumido

- v5.4: Cloudflare WSL, MCPs Cloudflare, tunnel real `all-in-one-stream`, correção
  de origem `stream -> 8100` e migração do MCP Stitch para variável de ambiente.

## Versão 5.3 — Checkout Mercado Pago

**Data e hora:** 01/08/2026 08:58, `America/Sao_Paulo`
**Branch:** `codex/corrigir-vscode-persistente-20260731`
**Referência local:** merge sobre `origin/main` em `4b4f83f3b3cefe9850f796e4dd393b741b1c89cb`
**Objetivo:** preparar a criação server-side de preferências Checkout Pro do Mercado Pago para o checkout Marketplace.

Escopo entregue: `payment_method` aceita `wallet` ou `mercado_pago`; o backend
cria a preferência em `POST /valley/checkout/{checkout_id}/mercadopago/preference`;
o access token nunca é enviado ao cliente; a migration `033` e seu rollback
ampliam a constraint de pagamento. A feature flag
`MARKETPLACE_CHECKOUT_V1_ENABLED` continua desligada por padrão.

Pré-requisitos: `MERCADO_PAGO_ACCESS_TOKEN`, `MERCADO_PAGO_WEBHOOK_SECRET` e
`MERCADO_PAGO_NOTIFICATION_URL` com HTTPS, sempre fora do Git. A assinatura
HMAC `id;request-id;ts` é validada e expira em 300 segundos.

Validação reproduzível: `python3 -m py_compile` nos módulos alterados e
`.venv/bin/python -m pytest --capture=no -q tests/test_mercado_pago_checkout.py tests/test_marketplace_checkout_contract.py tests/test_marketplace_checkout_routes.py`.
O ambiente local exigiu `--capture=no` por falha do diretório temporário do
pytest. Sem credenciais não foi feita chamada real ao PSP.

Pendência: implementar consumidor idempotente do webhook, consulta autoritativa
do pagamento, atualização transacional de escrow/ledger e refund/chargeback na
issue #95 antes de habilitar produção.

**Versão:** 5.3
**Data e hora:** 01/08/2026 04:18, `America/Sao_Paulo`  
**Repositório:** `interflownex/All-in-One`  
**Marcos integrados:** PR `#108` (`1d05e56ca3bc1a66eb1e280743db24308d6da1b1`) e PR `#109` (`90d518cf65b90ec54c8dc6995f47c061cbba2e23`)  
**Issue-mãe:** `#51`  
**Prioridade funcional:** `#95`  
**Bloqueio externo:** `#107`  
**Classificação:** `Pendências > Técnico > Equipe Técnica`  
**Público-alvo:** Equipe Técnica

## 1. Estado autoritativo

- O único repositório oficial é `interflownex/All-in-One`.
- Valley é produto e conjunto de aplicativos internos deste monorepo.
- A política mandatória está em `config/autonomy/repository_scope_policy.json`.
- O gate `scripts/validate_repository_scope.py` e seus testes impedem regressão de escopo.
- Vision permanece inativo e fora do catálogo vigente.
- Merge Commit e Rebase Merge permanecem desativados; Squash and Merge é o único método habilitado.
- As issues #51, #55 e #95 estão reconciliadas com o estado real integrado.
- A governança e a documentação pós-merge já foram integradas com CI, Security, Docker Compose Health Gate e A1 Admin Template verdes no mesmo SHA.

## 2. Primeira ação: auditoria do worktree local

O diretório WSL `/home/eretazan/all-in-one` não esteve montado nesta execução. Staged, unstaged, untracked, exclusões e commits locais não foram presumidos nem alterados.

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

## 3. Segunda ação: issue #95

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

## 4. Bloqueio externo: issue #107

O deploy GKE autentica no Google Cloud, mas recebe HTTP 403 porque o faturamento do projeto `all-in-one-498012` está desativado.

- não enfraquecer o workflow;
- não usar `continue-on-error`;
- não simular sucesso;
- não contornar billing ou IAM;
- após habilitação legítima do faturamento, repetir o deploy e exigir rollout verde no mesmo SHA.

## 5. Demais prioridades

1. consolidar a fonte produtiva do AIO Admin na issue #89;
2. revisar branches antigas por extração seletiva;
3. executar Health Watch + SafeZone da issue #47;
4. avançar as issues #55, #39, #69 e #24 conforme seus critérios;
5. avançar Delivery e Rider somente após o gate financeiro.

## 6. Branches remotas antigas

- Nunca fazer merge direto de branch obsoleta.
- Nunca trazer lockfiles antigos sem reinstalação e auditoria.
- Nunca reutilizar migrations 031 ou 032.
- A branch `feature/primicias-selecionadas-v1` contém migration 031 incompatível e só pode servir como fonte de requisitos ou trechos reconstruídos sobre a `main` atual.

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
- v5.1: registro da integração e estado pós-merge;
- v5.2: remoção de passos autorreferentes; fila inicia na auditoria local e na issue #95.
