param(
    [string]$ConfigPath = "config/integrations/cloudflare_stream_tunnel.json",
    [string]$Hostname = "",
    [string]$TunnelName = "",
    [string]$OriginUrl = "",
    [string]$PublicPathRegex = "",
    [switch]$SkipOriginCheck
)

$ErrorActionPreference = "Stop"

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Resolve-RepoRoot {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) {
        $repoRoot = & $git.Source rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($repoRoot)) {
            return $repoRoot.Trim()
        }
    }

    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Merge-ConfigValue {
    param(
        [string]$ExplicitValue,
        [pscustomobject]$ConfigObject,
        [string]$PropertyName,
        [string]$DefaultValue
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitValue)) {
        return $ExplicitValue
    }

    if ($ConfigObject -and $ConfigObject.PSObject.Properties.Name -contains $PropertyName) {
        $value = [string]$ConfigObject.$PropertyName
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value.Trim()
        }
    }

    return $DefaultValue
}

function Invoke-Cloudflared {
    param(
        [string]$Executable,
        [string[]]$Arguments
    )

    $output = & $Executable @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "cloudflared $($Arguments -join ' ') falhou.`n$output"
    }
    return $output
}

function Get-CloudflaredService {
    $service = Get-Service -Name "Cloudflared" -ErrorAction SilentlyContinue
    if ($service) {
        return $service
    }

    return Get-Service -Name "cloudflared" -ErrorAction SilentlyContinue
}

if (-not (Test-IsAdministrator)) {
    throw "Execute este script em um PowerShell com privilegios de administrador."
}

$repoRoot = Resolve-RepoRoot
Set-Location $repoRoot

$config = $null
$resolvedConfigPath = Join-Path $repoRoot $ConfigPath
if (Test-Path $resolvedConfigPath) {
    $config = Get-Content -Raw -Path $resolvedConfigPath | ConvertFrom-Json
}

$Hostname = Merge-ConfigValue $Hostname $config "hostname" ""
$TunnelName = Merge-ConfigValue $TunnelName $config "tunnelName" "all-in-one-stream"
$OriginUrl = Merge-ConfigValue $OriginUrl $config "originUrl" "http://localhost:58578"
$PublicPathRegex = Merge-ConfigValue $PublicPathRegex $config "publicPathRegex" "^/stream$"

if ([string]::IsNullOrWhiteSpace($Hostname)) {
    throw "Informe -Hostname ou preencha o campo 'hostname' em $ConfigPath."
}

if (-not $SkipOriginCheck) {
    try {
        $originProbe = Invoke-WebRequest -Uri "$OriginUrl/stream" -Method Get -UseBasicParsing -TimeoutSec 10
        Write-Host "Origin local respondeu com status $($originProbe.StatusCode): $OriginUrl/stream"
    } catch {
        throw "A origin local nao respondeu em $OriginUrl/stream. Suba o servico antes de publicar no Cloudflare ou use -SkipOriginCheck."
    }
}

$codeTunnel = Get-Command code-tunnel.exe -ErrorAction SilentlyContinue
if (-not $codeTunnel) {
    $codeTunnel = Get-Command code-tunnel -ErrorAction SilentlyContinue
}

$existingCodeTunnel = Get-Process -Name "code-tunnel" -ErrorAction SilentlyContinue
if ($existingCodeTunnel) {
    Write-Host "Encerrando processo VS Code Tunnel existente."
    $existingCodeTunnel | Stop-Process -Force
}

$cloudflaredDir = "C:\Cloudflared\bin"
$cloudflaredExe = Join-Path $cloudflaredDir "cloudflared.exe"
$systemCloudflaredDir = "C:\Windows\System32\config\systemprofile\.cloudflared"
$systemConfigPath = Join-Path $systemCloudflaredDir "config.yml"
$cloudflaredLog = "C:\Cloudflared\cloudflared.log"
$downloadUrl = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

New-Item -ItemType Directory -Path $cloudflaredDir -Force | Out-Null
New-Item -ItemType Directory -Path $systemCloudflaredDir -Force | Out-Null
New-Item -ItemType Directory -Path "C:\Cloudflared" -Force | Out-Null

if (-not (Test-Path $cloudflaredExe)) {
    Write-Host "Baixando cloudflared para $cloudflaredExe"
    Invoke-WebRequest -Uri $downloadUrl -OutFile $cloudflaredExe
}

$service = Get-CloudflaredService
if (-not $service) {
    Write-Host "Instalando servico Cloudflared."
    Invoke-Cloudflared $cloudflaredExe @("service", "install")
    $service = Get-CloudflaredService
    if (-not $service) {
        throw "O servico Cloudflared nao ficou disponivel apos a instalacao."
    }
}

$userCloudflaredDir = Join-Path $env:USERPROFILE ".cloudflared"
$userCertPath = Join-Path $userCloudflaredDir "cert.pem"
$systemCertPath = Join-Path $systemCloudflaredDir "cert.pem"

if (-not (Test-Path $userCertPath)) {
    Write-Host "Autenticando cloudflared na conta Cloudflare."
    & $cloudflaredExe login
    if ($LASTEXITCODE -ne 0) {
        throw "Falha na autenticacao interativa do cloudflared."
    }
    if (-not (Test-Path $userCertPath)) {
        throw "O cloudflared login foi concluido sem gerar o arquivo $userCertPath."
    }
}

Copy-Item -Path $userCertPath -Destination $systemCertPath -Force

$tunnelListRaw = Invoke-Cloudflared $cloudflaredExe @("tunnel", "list", "--output", "json")
$tunnelList = $tunnelListRaw | ConvertFrom-Json
$tunnel = $tunnelList | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1

if (-not $tunnel) {
    Write-Host "Criando tunnel nomeado '$TunnelName'."
    Invoke-Cloudflared $cloudflaredExe @("tunnel", "create", $TunnelName) | Out-Host
    $tunnelListRaw = Invoke-Cloudflared $cloudflaredExe @("tunnel", "list", "--output", "json")
    $tunnelList = $tunnelListRaw | ConvertFrom-Json
    $tunnel = $tunnelList | Where-Object { $_.name -eq $TunnelName } | Select-Object -First 1
}

if (-not $tunnel -or [string]::IsNullOrWhiteSpace($tunnel.id)) {
    throw "Nao foi possivel localizar o tunnel '$TunnelName' apos a criacao."
}

$tunnelId = [string]$tunnel.id
$userCredentialsPath = Join-Path $userCloudflaredDir "$tunnelId.json"
$systemCredentialsPath = Join-Path $systemCloudflaredDir "$tunnelId.json"

if (-not (Test-Path $userCredentialsPath)) {
    throw "Arquivo de credenciais do tunnel nao encontrado em $userCredentialsPath."
}

Copy-Item -Path $userCredentialsPath -Destination $systemCredentialsPath -Force

$configContent = @"
tunnel: $tunnelId
credentials-file: $systemCredentialsPath
logfile: $cloudflaredLog

ingress:
  - hostname: $Hostname
    path: $PublicPathRegex
    service: $OriginUrl
  - service: http_status:404
"@

Set-Content -Path $systemConfigPath -Value $configContent -Encoding ASCII

Write-Host "Criando/atualizando DNS publico para $Hostname."
$routeOutput = & $cloudflaredExe tunnel route dns $TunnelName $Hostname 2>&1
if ($LASTEXITCODE -ne 0) {
    $routeText = ($routeOutput | Out-String)
    if ($routeText -notmatch "already exists") {
        throw "Falha ao criar rota DNS para $Hostname.`n$routeText"
    }
    Write-Warning "A rota DNS ja existia para $Hostname; mantendo configuracao."
}

Invoke-Cloudflared $cloudflaredExe @("--config", $systemConfigPath, "tunnel", "ingress", "validate") | Out-Host

$serviceCommand = "`"$cloudflaredExe`" --config=`"$systemConfigPath`" tunnel run"
$serviceRegPath = "HKLM:\SYSTEM\CurrentControlSet\Services\Cloudflared"
if (-not (Test-Path $serviceRegPath)) {
    $serviceRegPath = "HKLM:\SYSTEM\CurrentControlSet\Services\cloudflared"
}

if (-not (Test-Path $serviceRegPath)) {
    throw "Servico Cloudflared instalado, mas a chave de registro do servico nao foi encontrada."
}

Set-ItemProperty -Path $serviceRegPath -Name ImagePath -Value $serviceCommand

$service = Get-CloudflaredService
if (-not $service) {
    throw "Nao foi possivel localizar o servico Cloudflared para reinicio final."
}
if ($service -and $service.Status -ne "Stopped") {
    Stop-Service -Name $service.Name -Force
}

Set-Service -Name $service.Name -StartupType Automatic
Start-Service -Name $service.Name
$service.Refresh()

Write-Host ""
Write-Host "Tunnel Cloudflare configurado com persistencia no servico do Windows."
Write-Host "Hostname publico: https://$Hostname/stream"
Write-Host "Origin local: $OriginUrl/stream"
Write-Host "Tunnel name: $TunnelName"
Write-Host "Tunnel id: $tunnelId"
