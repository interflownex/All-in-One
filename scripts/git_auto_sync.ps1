param(
    [string]$Activity = "atividade Codex",
    [string]$Remote = "",
    [string]$Branch = "",
    [switch]$NoFetch,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PathSpec = @()
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') falhou com codigo $LASTEXITCODE"
    }
}

function Test-GitPath {
    param([string]$Path)
    $value = & git rev-parse --git-path $Path
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel resolver o caminho Git: $Path"
    }
    return (Test-Path $value)
}

$repoRoot = & git rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) {
    throw "Este comando precisa ser executado dentro de um repositorio Git."
}

Set-Location $repoRoot

if ((Test-GitPath "MERGE_HEAD") -or (Test-GitPath "rebase-merge") -or (Test-GitPath "rebase-apply")) {
    throw "Sincronizacao automatica bloqueada: ha merge ou rebase em andamento."
}

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (& git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($Branch)) {
        throw "Nao foi possivel identificar a branch atual."
    }
}

if ([string]::IsNullOrWhiteSpace($Remote)) {
    $Remote = (& git config --get "branch.$Branch.pushRemote").Trim()
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        $Remote = (& git config --get remote.pushDefault).Trim()
    }
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        $Remote = (& git config --get "branch.$Branch.remote").Trim()
    }
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        $Remote = "origin"
    }
}

if (-not $NoFetch) {
    & git fetch $Remote $Branch | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Fetch de $Remote/$Branch falhou; prosseguindo com commit local antes do push."
    }
}

$normalizedPathSpec = @()
foreach ($item in $PathSpec) {
    if ([string]::IsNullOrWhiteSpace($item)) {
        continue
    }

    $normalizedPathSpec += ($item -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

if ($normalizedPathSpec.Count -gt 0) {
    Invoke-Git add -- @normalizedPathSpec
} else {
    Invoke-Git add -A
}

& git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "Sem mudancas staged para commit. Nada para sincronizar."
    exit 0
}

$safeActivity = ($Activity -replace "\s+", " ").Trim()
if ([string]::IsNullOrWhiteSpace($safeActivity)) {
    $safeActivity = "atividade Codex"
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$message = "chore(auto-sync): $safeActivity"
$body = "Sincronizacao automatica Codex em $timestamp."

Invoke-Git commit -m $message -m $body
Invoke-Git push $Remote "HEAD:$Branch"

Write-Host "Sincronizacao concluida: $Remote/$Branch"
