param(
    [string]$Hostname = "",
    [switch]$SkipOriginCheck,
    [switch]$PublishAllPaths
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Hostname)) {
    $Hostname = Read-Host "Digite o hostname publico no Cloudflare (ex.: stream.seu-dominio.com)"
}

if ([string]::IsNullOrWhiteSpace($Hostname)) {
    throw "Hostname obrigatorio."
}

$scriptPath = Join-Path $PSScriptRoot "setup_cloudflare_stream_tunnel.ps1"

& $scriptPath `
    -Hostname $Hostname `
    -TunnelName "all-in-one-stream" `
    -OriginUrl "http://127.0.0.1:8100" `
    -SkipOriginCheck:$SkipOriginCheck `
    -PublishAllPaths:$PublishAllPaths

if ($LASTEXITCODE -ne 0) {
    throw "Falha na configuracao automatica do Cloudflare Tunnel."
}
