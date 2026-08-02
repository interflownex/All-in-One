# Cloudflare WSL

**Versao:** 1.3
**Data:** 2026-08-02 02:31, America/Sao_Paulo
**Escopo:** workspace `all-in-one` no WSL

## Estado desejado

- `wrangler` instalado no WSL e autenticado por OAuth local ou
  `CLOUDFLARE_API_TOKEN`.
- `cloudflared` instalado no WSL.
- Cloudflare Pages publica `apps/all-in-one` no projeto `all-in-one-web`.
- A branch de producao do projeto Pages e `main`; `worktree-sync` nao deve
  voltar a ser branch produtiva.
- O workflow de Pages usa `wrangler` `4.118.0` e so tenta publicar quando
  `CLOUDFLARE_API_TOKEN` e `CLOUDFLARE_ACCOUNT_ID` existirem em GitHub Secrets.
- MCPs `cloudflare-docs` e `cloudflare-api` ficam cadastrados no Codex.
- Tunnel existente `all-in-one-stream` esta registrado no Cloudflare como
  `healthy` e publicado por `stream.brasildesconto.com.br`.
- O serviço Windows `Cloudflared` fica ativo e com inicializacao automatica.
- A replica systemd no WSL e opcional e usa `CLOUDFLARE_TUNNEL_TOKEN`, fora do
  Git, quando for necessario rodar um conector adicional dentro do WSL.
- SSH administrativo continua via Tailscale; Cloudflare Tunnel nao publica SSH.

## Perfil versionado

A fonte local fica em:

```text
config/cloudflare/workspace_profile.json
```

Esse arquivo pode conter `account_id`, nomes de projeto e hostnames, mas nunca
token, chave privada, `cert.pem`, refresh token ou tunnel token.

## Comandos

Validar o estado atual sem exigir tunnel ativo:

```bash
python3 scripts/validate_cloudflare_wsl.py
```

Aplicar MCPs e validar CLI local:

```bash
python3 scripts/configure_cloudflare_wsl.py --apply
```

Publicar manualmente a build atual pelo OAuth local do `wrangler`, sem depender
dos secrets do GitHub Actions:

```bash
cd apps/all-in-one
npm ci
npm run build
wrangler pages deploy dist --project-name all-in-one-web --branch main
```

Ativar uma replica persistente no WSL quando o token ja estiver disponivel no
ambiente:

```bash
CLOUDFLARE_TUNNEL_TOKEN="<token_do_dashboard>" \
sudo -E python3 scripts/configure_cloudflare_wsl.py --apply --install-service
```

Validar em modo estrito, exigindo o servico ativo:

```bash
python3 scripts/validate_cloudflare_wsl.py --strict
```

## Tunnel ativo

- Nome: `all-in-one-stream`
- ID: `7b9ce5bc-7f6e-4416-bff3-3a278ce4b96f`
- Hostname: `stream.brasildesconto.com.br`
- Origin: `http://127.0.0.1:8100`
- Caminho publicado pelo script legado: `/stream`
- Persistencia confirmada: servico Windows `Cloudflared` em estado `Running`
  com `StartType` automatico.

## Criacao do token de replica WSL

No painel Cloudflare Zero Trust, crie um tunnel gerenciado por `cloudflared`,
copie o token de instalacao e injete-o apenas como variavel de ambiente ou cofre
local. O reposititorio registra o tunnel real `all-in-one-stream`, mas nao
versiona o segredo nem arquivos `cert.pem` ou `*.json` de credenciais.

## DNS

- `brasildesconto.com.br` ja aparece no projeto Cloudflare Pages
  `all-in-one-web`.
- O diagnostico anterior em
  `docs/relatorios/dns/DIAGNOSTICO_DNS_BRASILDESCONTO_APPDEPLOY_2026-07-30.md`
  deve ser respeitado: nao reintroduzir AAAA no dominio raiz enquanto a
  validacao AppDeploy exigir somente IPv4.
- APIs devem usar subdominios dedicados, como `api.brasildesconto.com.br`.
- `stream.brasildesconto.com.br` deve continuar apontando para o API Hub em
  `http://127.0.0.1:8100`; nao redirecionar para ERP `8107` sem nova decisao
  tecnica registrada.

## GitHub Actions

- Variaveis nao sensiveis configuradas: `VITE_API_HUB_URL`,
  `CLOUDFLARE_PAGES_PROJECT_NAME`, `CLOUDFLARE_PAGES_DOMAIN`,
  `CLOUDFLARE_TUNNEL_NAME`, `CLOUDFLARE_TUNNEL_API_HOSTNAME`,
  `CLOUDFLARE_TUNNEL_API_ORIGIN`, `CLOUDFLARE_TUNNEL_STREAM_HOSTNAME` e
  `CLOUDFLARE_TUNNEL_STREAM_ORIGIN`.
- `CLOUDFLARE_ACCOUNT_ID` fica em GitHub Secrets.
- `CLOUDFLARE_API_TOKEN` deve ser um token Cloudflare persistente e escopado
  para Pages/Workers conforme a documentacao oficial; enquanto ausente, o
  workflow termina verde com aviso e sem publicar.
- `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` sao opcionais para a notificacao
  pos-deploy; quando ausentes, a publicacao Cloudflare nao deve falhar por isso.

## Producao

- `production_branch`: `main`.
- Deployment produtivo validado em 02/08/2026 02:30 America/Sao_Paulo:
  `https://6286ca59.all-in-one-web-7fa.pages.dev`.
- Dominio customizado validado: `https://brasildesconto.com.br`, HTTP 200,
  titulo `All-in-One - Ecossistema Digital` e headers de seguranca ativos.

## Fontes oficiais

- Cloudflare Tunnel: `https://developers.cloudflare.com/tunnel/`
- Setup de Tunnel: `https://developers.cloudflare.com/tunnel/setup/`
- Downloads do cloudflared:
  `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/`
- Servico Linux:
  `https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/`
- Wrangler:
  `https://developers.cloudflare.com/workers/wrangler/commands/general/`
- MCP Cloudflare: `https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/`
