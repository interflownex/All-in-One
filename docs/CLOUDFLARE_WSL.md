# Cloudflare WSL

**Versao:** 1.1
**Data:** 2026-08-01 23:58, America/Sao_Paulo
**Escopo:** workspace `all-in-one` no WSL

## Estado desejado

- `wrangler` instalado no WSL e autenticado por OAuth local ou
  `CLOUDFLARE_API_TOKEN`.
- `cloudflared` instalado no WSL.
- Cloudflare Pages publica `apps/all-in-one` no projeto `all-in-one-web`.
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
