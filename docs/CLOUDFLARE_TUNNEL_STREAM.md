# Cloudflare Tunnel para `/stream`

Este fluxo existe para uma excecao operacional explicitamente autorizada pelo
usuario: publicar `http://localhost:58578/stream` por um hostname HTTPS no
Cloudflare e manter a exposicao de forma persistente no Windows.

## O que este setup faz

- encerra processos `code-tunnel.exe` em execucao;
- instala ou reaproveita `cloudflared.exe` em `C:\Cloudflared\bin`;
- autentica a maquina no Cloudflare;
- cria ou reaproveita um `named tunnel`;
- registra um hostname publico no DNS da zona Cloudflare;
- grava o `config.yml` do servico em
  `C:\Windows\System32\config\systemprofile\.cloudflared\config.yml`;
- configura o servico Windows `Cloudflared` para iniciar automaticamente;
- restringe o trafego publicado ao caminho `/stream`.

## Pre-requisitos

- Windows com PowerShell em modo Administrador.
- Uma zona ja delegada ao Cloudflare.
- Permissao para autenticar o `cloudflared` na conta correta.
- O servico local respondendo em `http://localhost:58578/stream`.

## Configuracao

1. Copie o arquivo de exemplo:

```powershell
Copy-Item config\integrations\cloudflare_stream_tunnel.example.json `
  config\integrations\cloudflare_stream_tunnel.json
```

2. Ajuste o campo `hostname` para o subdominio publico desejado.

## Execucao

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts\setup_cloudflare_stream_tunnel.ps1 `
  -ConfigPath config\integrations\cloudflare_stream_tunnel.json
```

Tambem e possivel sobrescrever os valores diretamente:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts\setup_cloudflare_stream_tunnel.ps1 `
  -Hostname stream.seu-dominio.com `
  -TunnelName all-in-one-stream `
  -OriginUrl http://localhost:58578
```

## Resultado esperado

Ao final, o endpoint publico deve ficar assim:

```text
https://stream.seu-dominio.com/stream
```

O script escreve uma regra de ingress equivalente a:

```yml
ingress:
  - hostname: stream.seu-dominio.com
    path: ^/stream$
    service: http://localhost:58578
  - service: http_status:404
```

## Observacoes importantes

- O script nao versiona segredos.
- A autenticacao inicial do `cloudflared login` abre fluxo interativo no
  navegador da maquina Windows.
- Se a rota DNS ja existir, o script preserva a entrada existente quando ela ja
  apontar para o tunnel.
- Este setup substitui o acesso via VS Code Tunnel para esse caso de uso; o
  endpoint publico passa a ser o hostname do Cloudflare, nao `vscode.dev`.
