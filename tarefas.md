# Tarefas da IA Desenvolvedora

## Versão 6.0 — Flutter Linux persistente no VS Code WSL e gate do checkout

**Data e hora:** 03/08/2026 07:58, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/integrar-checkout-pagamentos-20260802`
**Referência de base:** `1b152dac1ec7de06a561233a40316af79d624fc1`
**Objetivo:** impedir que o VS Code em `WSL: Ubuntu` execute o SDK Flutter do
Windows e restaurar o gate de segurança do checkout Mercado Pago.

### Contexto, escopo e fontes de verdade

- O log Dart Code selecionava `/mnt/c/Users/ereta/flutter/flutter/flutter` e
  falhava ao localizar `packages/flutter_tools/bin/flutter_tools.dart`.
- O SDK Linux oficial Flutter `3.44.8`, alinhado ao workflow
  `.github/workflows/valley-android-release.yml`, fica em
  `/home/eretazan/develop/flutter`.
- `.vscode/settings.json` e `all-in-one.code-workspace` são os contratos dos
  dois modos de abertura do repositório.
- `modules/shared/mercado_pago_checkout.py` deve aceitar no sink de rede apenas
  uma base HTTPS sem credenciais, conforme o gate Bandit B310.

### Pré-requisitos, sequência e prioridades

1. Abrir `all-in-one.code-workspace` em uma janela `WSL: Ubuntu`.
2. Confirmar que `/home/eretazan/develop/flutter/bin/flutter --version` retorna
   Flutter `3.44.8` e Dart `3.12.2`.
3. Executar `Developer: Reload Window` para a extensão Dart reler
   `dart.flutterSdkPath`.
4. Executar `flutter pub get` e os testes em `apps/valley-flutter`, registrando
   separadamente qualquer asset declarado ainda ausente.
5. Executar os testes de contrato do VS Code e Mercado Pago e o mesmo comando
   Bandit do workflow Security.
6. Publicar o commit na PR #120 e exigir gates verdes no mesmo SHA antes de
   qualquer **Squash and Merge**.

### Testes e critérios de aceite

- `flutter --version` usa exclusivamente o SDK Linux `3.44.8`.
- `flutter pub get` resolve as dependências e `flutter test` passa em
  `apps/valley-flutter`.
- `tests/test_vscode_workspace_contract.py` protege SDK e PATH nos dois modos.
- `tests/test_mercado_pago_checkout.py` rejeita `http:`, `file:` e credenciais
  embutidas, preservando HTTPS legítimo.
- Bandit completo termina com código zero e a PR #120 fica verde no SHA final.

### Riscos, bloqueios, evidências e pendências

- A janela já aberta precisa ser recarregada; o estado visual pós-reload deve
  ser confirmado pelo usuário e não é provado apenas por teste estático.
- `flutter pub get` apontou que `assets/brand/` e `assets/valley/` ainda não
  existem. A criação desses diretórios depende dos ativos canônicos e não pode
  usar substitutos por causa da governança de marca.
- Dispositivo/emulador Android não é necessário para os testes Dart unitários,
  mas continua necessário para evidência final de execução móvel.
- Evidências esperadas: versões do SDK, testes reproduzíveis, diff conhecido,
  commit publicado, PR #120 e checks verdes.
- Se a extensão voltar a escolher `/mnt/c/...`, conferir primeiro se a janela
  exibe `WSL: Ubuntu` e se o arquivo de workspace correto foi reaberto.

### Procedimento de entrega

- Versionar somente os arquivos deste escopo na branch atual, publicar na PR
  #120, aguardar todos os gates obrigatórios e integrar somente por **Squash and
  Merge**. Não versionar SDK, cache, credenciais nem artefatos temporários.

### Histórico resumido

- v6.0: SDK Flutter Linux fixado nos dois modos do VS Code WSL e validação HTTPS
  adicionada ao cliente Mercado Pago para restaurar o gate `python-security`.
- v5.9: checkout Mercado Pago integrado de forma seletiva sobre a `main`.

## Versão 5.9 — Integração limpa do Checkout Mercado Pago

**Data e hora:** 02/08/2026 15:55, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/integrar-checkout-pagamentos-20260802`
**Referência de base:** `origin/main` em `de69008282ed8c30b63c18c798730383866bd6bd`
**Objetivo:** integrar sobre a `main` atual somente o checkout Mercado Pago e a
configuração MCP correspondente, sem carregar o histórico divergente da branch
antiga `codex/corrigir-vscode-persistente-20260731`.

### Contexto e escopo

- `payment_method` aceita `wallet` ou `mercado_pago`.
- O backend cria preferências server-side em
  `POST /valley/checkout/{checkout_id}/mercadopago/preference`.
- A migration `033` e seu rollback ampliam a constraint de pagamento.
- O MCP Mercado Pago é referenciado sem versionar credenciais.
- `MARKETPLACE_CHECKOUT_V1_ENABLED` permanece desligada por padrão.

### Fontes de verdade e pré-requisitos

- `modules/marketplace/CHECKOUT_CONTRACT.md`
- `modules/marketplace/checkout/OPENAPI.yaml`
- `modules/shared/mercado_pago_checkout.py`
- `database/postgres/migrations/033_marketplace_checkout_mercado_pago.sql`
- Credenciais `MERCADO_PAGO_ACCESS_TOKEN`, `MERCADO_PAGO_WEBHOOK_SECRET` e
  `MERCADO_PAGO_NOTIFICATION_URL` permanecem exclusivamente fora do Git.

### Sequência, prioridades e testes

1. Validar compilação dos módulos Python alterados.
2. Executar os testes de Mercado Pago, contrato e rotas do checkout.
3. Executar `git diff --check` e o validador geral do repositório.
4. Publicar a branch, abrir PR para `main` e aguardar gates verdes no mesmo SHA.
5. Integrar exclusivamente por **Squash and Merge**.

### Critérios de aceite, riscos e bloqueios

- Nenhum token é enviado ao cliente ou versionado.
- A assinatura HMAC `id;request-id;ts` expira em 300 segundos.
- Sem credenciais, nenhuma chamada real ao PSP é declarada como validada.
- Produção permanece bloqueada até consumidor idempotente de webhook, consulta
  autoritativa, escrow/ledger transacional, reconciliação, refund e chargeback
  previstos na issue #95.
- Evidências esperadas: testes locais reproduzíveis, diff conhecido, PR e checks
  verdes no SHA final.

### Histórico resumido

- v5.9: checkout Mercado Pago extraído seletivamente da branch divergente e
  reaplicado sobre a `main` atual para integração segura.

## Versão 5.8 — Cloudflare Pages produção em `main`

**Data e hora:** 02/08/2026 02:31, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/cloudflare-production-main-20260802`
**Referência local antes do commit da entrega:** `41c0e33`
**Objetivo:** fixar a branch de produção do Cloudflare Pages em `main`,
remover a dependência de `worktree-sync` e validar o domínio customizado
`brasildesconto.com.br` servindo o All-in-One correto.

### Contexto

Depois do deploy manual por `wrangler`, a lista do Cloudflare Pages mostrou que
`main` ainda gerava Preview porque a branch produtiva remota estava em
`worktree-sync`. Isso fazia o domínio customizado servir uma build antiga com
título `tmp-valley`.

### Escopo

- Alterar remotamente o projeto Cloudflare Pages `all-in-one-web` para
  `production_branch=main`.
- Publicar novamente a build atual pelo `wrangler` OAuth local.
- Versionar `production_branch=main` em `config/cloudflare/workspace_profile.json`
  e `config/autonomy/cloudflare_web_policy.json`.
- Atualizar os validadores para bloquear regressão.
- Atualizar documentação e relatórios v5.5.

### Evidências

- API Cloudflare respondeu `success=true` e `production_branch=main`.
- `wrangler pages deployment list --project-name all-in-one-web` mostrou
  deployment Production na branch `main`, source `41c0e33`, deployment
  `https://6286ca59.all-in-one-web-7fa.pages.dev`.
- `https://brasildesconto.com.br` respondeu HTTP 200 com o título
  `All-in-One - Ecossistema Digital` e headers de segurança.

### Critérios de aceite

- Produção Cloudflare Pages vem de `main`.
- `worktree-sync` não é fonte produtiva.
- Validador local falha se `production_branch` divergir de `main`.
- Nenhum segredo é versionado.

### Histórico resumido

- v5.8: Cloudflare Pages production branch corrigida para `main`; domínio
  customizado validado com o All-in-One correto.

## Versão 5.7 — Cloudflare completo e coerente no modo local-first

**Data e hora:** 02/08/2026 02:09, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/cloudflare-completo-coerente-20260802`
**Referência local antes do commit da entrega:** `5e75511`
**Objetivo:** deixar Cloudflare Pages, Tunnel, MCP, GitHub Actions e variáveis
externas coerentes com o workspace WSL local-first, sem versionar segredos e sem
falhas automáticas quando o token persistente de deploy não existir.

### Contexto

Cloudflare está ativo no ambiente local: `wrangler` autenticado, Pages
`all-in-one-web` confirmado, MCPs Cloudflare cadastrados e Tunnel
`all-in-one-stream` remoto em estado `healthy`. As falhas históricas do workflow
Cloudflare Pages vinham de credenciais ausentes no GitHub Actions; a entrega
passa a tratar essa ausência como preflight auditável, não como erro vermelho.

### Escopo

- Atualizar `.github/workflows/cloudflare-pages.yml` para `wrangler` `4.118.0`.
- Adicionar preflight de `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID`.
- Manter deploy automático apenas quando os secrets existirem fora do Git.
- Ignorar notificação Telegram quando `TELEGRAM_BOT_TOKEN` ou
  `TELEGRAM_CHAT_ID` estiverem ausentes, sem falhar a publicação Cloudflare.
- Atualizar `apps/all-in-one/package.json` para usar o mesmo pin de Wrangler.
- Adicionar teste `tests/test_cloudflare_pages_workflow.py`.
- Atualizar `scripts/validate_repository.py`, `docs/CLOUDFLARE_WSL.md`,
  `docs/Pendências Do desenvolvedor.md` e relatórios v5.4.

### Fontes de verdade

- `config/cloudflare/workspace_profile.json`
- `config/autonomy/cloudflare_web_policy.json`
- `.github/workflows/cloudflare-pages.yml`
- `scripts/validate_cloudflare_wsl.py`
- `scripts/configure_cloudflare_wsl.py`

### Pré-requisitos

- `CLOUDFLARE_API_TOKEN` deve permanecer somente em GitHub Secrets, variável de
  ambiente local ou cofre externo.
- `CLOUDFLARE_ACCOUNT_ID` já pode ficar em GitHub Secrets.
- Variáveis não sensíveis esperadas no GitHub: `VITE_API_HUB_URL`,
  `CLOUDFLARE_PAGES_PROJECT_NAME`, `CLOUDFLARE_PAGES_DOMAIN`,
  `CLOUDFLARE_TUNNEL_NAME`, `CLOUDFLARE_TUNNEL_API_HOSTNAME`,
  `CLOUDFLARE_TUNNEL_API_ORIGIN`, `CLOUDFLARE_TUNNEL_STREAM_HOSTNAME` e
  `CLOUDFLARE_TUNNEL_STREAM_ORIGIN`.

### Sequência de execução

1. Validar Cloudflare local: `python3 scripts/configure_cloudflare_wsl.py --apply`.
2. Validar estado remoto: `python3 scripts/validate_cloudflare_wsl.py`.
3. Testar app web: `cd apps/all-in-one && npm ci && npm run build`.
4. Validar workflow: `.venv/bin/python -m pytest --capture=no -q tests/test_cloudflare_pages_workflow.py tests/test_cloudflare_wsl_configuration.py`.
5. Validar repositório: `python3 scripts/validate_repository.py`.
6. Abrir PR, aguardar checks verdes e integrar por Squash and Merge.

### Critérios de aceite

- Cloudflare Pages/Tunnel/MCP validam sem erro no WSL.
- Workflow de Pages não usa Wrangler obsoleto.
- Ausência de `CLOUDFLARE_API_TOKEN` não causa falha automática em push.
- Nenhum token, chave privada ou PDF sensível é versionado.
- Deploy real no CI só ocorre com secrets persistentes configurados fora do Git.

### Histórico resumido

- v5.7: Cloudflare Pages/Tunnel/MCP validados; CI protegido por preflight de
  secrets e Wrangler alinhado ao ambiente local.

## Versão 5.6 — GKE manual no modo local-first

**Data e hora:** 02/08/2026 01:46, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/desativar-gke-local-first-20260802`
**Referência local antes do commit da entrega:** `00d027e`
**Objetivo:** remover a falha automática de GKE em `main` enquanto o workspace
opera sem Google Cloud pago, preservando deploy manual futuro com confirmação
explícita de billing/IAM/APIs legítimos.

### Contexto

O run de `main` `30732776160` falhou em `Get GKE credentials` com HTTP 403:
billing desativado no projeto `all-in-one-498012`. Isso é um bloqueio externo
já registrado em #107, mas o workflow automático em `push` contrariava o modo
local-first definido para o workspace.

### Escopo

- Converter `.github/workflows/deploy.yml` para `workflow_dispatch`.
- Exigir `confirm_gcp_billing_enabled=true` para executar o job real de deploy.
- Manter `GOOGLE_CLOUD_ENABLED=false` no nível padrão do workflow.
- Adicionar teste `tests/test_gke_workflow_local_first.py`.
- Atualizar `scripts/validate_repository.py` para bloquear regressão.
- Atualizar `docs/Pendências Do desenvolvedor.md` e relatórios v5.3.

### Sequência de validação

1. `.venv/bin/python -m pytest --capture=no -q tests/test_gke_workflow_local_first.py`
2. `python3 scripts/validate_repository.py`
3. Abrir PR, aguardar checks verdes e integrar por Squash and Merge.

### Critérios de aceite

- Nenhum deploy GKE automático em `push` para `main`.
- GKE só executa manualmente com confirmação explícita.
- #107 continua aberto como bloqueio externo de billing, sem simulação de
  sucesso.

### Histórico resumido

- v5.6: GKE automático removido do modo local-first; workflow fica manual e
  auditável.

## Versão 5.5 — WSL local-first, DNS persistente, Antigravity/Docker/MCP e acesso SSH

**Data e hora:** 02/08/2026 01:25:09, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/wsl-dns-antigravity-local-first-20260802`
**Referência local antes do commit da entrega:** `3533bca`
**Objetivo:** consolidar o workspace no WSL em modo local-first sem Google Cloud
pago, mantendo Cloudflare, Docker, MCP, Antigravity, Tailscale, DNS persistente e
acesso SSH por chave de forma coerente e auditável.

### Contexto

O Cloudflare já está ativo e validado para Pages, MCP e tunnel
`all-in-one-stream`. A execução remota Google Cloud/Data Agent Kit fica suspensa
por padrão. Stitch permanece configurado, mas a sincronização remota automática
fica desligada; fallback remoto somente por `workflow_dispatch` explícito com
segredo fora do Git.

### Escopo entregue

- Criar política e script persistente para DNS do WSL com `systemd-resolved`,
  `/etc/wsl.conf` sem `generateResolvConf` e preservação do MagicDNS Tailscale.
- Aplicar o DNS real no WSL e limpar alerta Tailscale de `setLinkDomains`.
- Normalizar MCPs do Codex: Docker usa `docker mcp gateway run --profile
  all_in_one_local`; filesystem aponta para o workspace WSL; Cloudflare e Stitch
  usam variáveis de ambiente sem token literal.
- Criar política e script de confiança do Antigravity, mantendo apenas MCPs
  essenciais: Cloudflare, Context7, Docker, filesystem do workspace e Stitch.
- Remover recomendações automáticas de `googlecloudtools.cloudcode` e
  `GoogleCloudTools.datacloud` do VS Code e colocar variáveis Google/Data Agent
  em `false`.
- Suspender Data Agent Kit por política, mantendo metadados só para reativação
  futura controlada.
- Remover `schedule` do workflow Stitch e deixar execução remota apenas como
  fallback manual.
- Ajustar scripts Cloudflare para rodarem `wrangler` em modo CI/sem métricas e
  aceitarem validação `--check`.
- Criar política SSH remota sem segredo, gerar chave OpenSSH fora do Git,
  registrar a chave pública em `~/.ssh/authorized_keys` e validar SSH por
  loopback e Tailscale.
- Gerar manual PDF sensível fora do Git em
  `/home/eretazan/.local/share/all-in-one/secure/manual-termius-termux-all-in-one-wsl-20260802.pdf`.

### Fontes de verdade

- `config/autonomy/wsl_dns_policy.json`
- `config/autonomy/antigravity_trust_policy.json`
- `config/autonomy/ssh_remote_access_policy.json`
- `config/autonomy/google_integrations_policy.json`
- `config/autonomy/data_agent_kit_policy.json`
- `config/cloudflare/workspace_profile.json`
- `.agents/antigravity.json`
- `.vscode/settings.json`
- `.vscode/extensions.json`
- `.github/workflows/stitch-sync.yml`

### Pré-requisitos

- Segredos permanecem fora do Git: `CLOUDFLARE_API_TOKEN`,
  `CLOUDFLARE_TUNNEL_TOKEN`, `STITCH_API_KEY`, `TELEGRAM_BOT_TOKEN` e
  `TELEGRAM_CHAT_ID`.
- A chave privada OpenSSH fica somente em
  `/home/eretazan/.ssh/all_in_one_wsl_ed25519`.
- O manual PDF sensível e o utilitário local de envio Telegram ficam somente em
  `/home/eretazan/.local/share/all-in-one/secure/`.
- O app Tailscale do cliente Termius/Termux deve estar na mesma tailnet.

### Sequência de execução

1. Validar DNS WSL: `python3 scripts/configure_wsl_dns.py --check`.
2. Validar Antigravity: `python3 scripts/configure_antigravity_trust.py --check`.
3. Validar Cloudflare: `python3 scripts/validate_cloudflare_wsl.py`.
4. Validar Docker: `python3 scripts/configure_docker_dx.py --check --print-status`
   e `docker compose -f infra/docker/docker-compose.yml config --quiet`.
5. Validar SSH: `ssh -i /home/eretazan/.ssh/all_in_one_wsl_ed25519 -o
   BatchMode=yes eretazan@100.99.245.76 true`.
6. Validar repositório: `python3 scripts/validate_repository.py`.

### Prioridades

1. Não versionar chave privada, PDF sensível, tokens ou backups externos.
2. Manter Google Cloud, Data Agent Kit, AlloyDB e Code CLI desligados por
   padrão no workspace.
3. Manter Gemini Code Assist e Stitch MCP disponíveis sem execução remota
   automática.
4. Manter SSH administrativo exclusivamente por Tailscale/loopback; Cloudflare
   Tunnel não publica SSH nem bancos.
5. Preservar Docker MCP no perfil `all_in_one_local`.

### Testes e evidências

- `python3 -m py_compile scripts/configure_data_agent_kit.py scripts/configure_wsl_dns.py scripts/configure_antigravity_trust.py scripts/configure_cloudflare_wsl.py scripts/validate_cloudflare_wsl.py scripts/validate_repository.py`
- `.venv/bin/python -m pytest --capture=no -q tests/test_ssh_remote_access_policy.py tests/test_data_agent_kit_runtime.py tests/test_stitch_orchestrator.py tests/test_wsl_dns_policy.py tests/test_antigravity_trust_policy.py tests/test_windows_script_contracts.py tests/test_cloudflare_wsl_configuration.py`
- `python3 scripts/configure_wsl_dns.py --check`
- `python3 scripts/configure_antigravity_trust.py --check`
- `python3 scripts/configure_data_agent_kit.py`
- `python3 scripts/validate_cloudflare_wsl.py`
- `python3 scripts/validate_repository.py`
- `tailscale status --json | jq '{BackendState, TUN, Online: .Self.Online, DNSName: .Self.DNSName, TailscaleIPs, Health}'`
- `resolvectl query github.com api.cloudflare.com login.tailscale.com registry-1.docker.io brasildesconto.com.br stream.brasildesconto.com.br`
- `ssh -i /home/eretazan/.ssh/all_in_one_wsl_ed25519 -o BatchMode=yes eretazan@127.0.0.1 true`
- `ssh -i /home/eretazan/.ssh/all_in_one_wsl_ed25519 -o BatchMode=yes eretazan@100.99.245.76 true`

### Critérios de aceite

- DNS do WSL continua apontando para `systemd-resolved` após reinício e resolve
  hosts GitHub, Cloudflare, Tailscale, Docker Registry e domínios do projeto.
- `tailscale status --json` retorna `Health: []` e MagicDNS resolve
  `valley-wsl2-1.tailb44596.ts.net`.
- Antigravity e Codex compartilham MCPs essenciais sem duplicidade, sem
  `MCP_DOCKER` legado e sem segredo literal.
- Cloudflare WSL valida Pages, MCPs, API, porta 7844 e tunnel
  `all-in-one-stream` healthy.
- SSH aceita somente chave pública; senha e root permanecem bloqueados.
- PDF e chave SSH não aparecem em `git status`.

### Riscos, bloqueios e pendências restantes

- O envio real por Telegram não foi executado porque `TELEGRAM_BOT_TOKEN` e
  `TELEGRAM_CHAT_ID` não estavam definidos no ambiente; o utilitário local
  sensível ficou pronto fora do Git.
- O PDF não imprime o conteúdo da chave privada; a importação no Termius deve
  usar a chave OpenSSH local indicada no manual.
- A sincronização remota Stitch segue disponível apenas como fallback manual e
  exige segredo legítimo fora do Git.

### Procedimento de entrega

Versionar somente os arquivos controlados desta atividade, executar push da
branch, abrir ou atualizar PR para `main`, aguardar gates verdes e integrar
exclusivamente por Squash and Merge. Após o merge, sincronizar `main` local e
liberar o lock multiagente.

### Histórico resumido

- v5.5: modo local-first no WSL, DNS persistente, Antigravity/Docker/MCP
  normalizados, Cloudflare robusto, Data Agent Kit suspenso, Stitch manual,
  Tailscale saudável e SSH/Termius documentado fora do Git.

## Versão 5.4 — Cloudflare WSL coerente e MCP sem segredo literal

**Data e hora:** 02/08/2026 00:07, `America/Sao_Paulo`
**Repositório:** `interflownex/All-in-One`
**Branch:** `codex/cloudflare-wsl-coerente-clean-20260802`
**Referência local antes do commit da entrega:** `953b570cd574`
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

**Versão:** 5.2
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
