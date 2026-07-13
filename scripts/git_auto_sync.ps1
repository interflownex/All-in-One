git config --global --add safe.directory '/wsl.localhost/Ubuntu/home/eretazan/.codex/worktrees/1781507772-23398/all-in-one'param(
    [string]$Activity = "atividade Codex",
    [string]$Remote = "",
    [string]$Branch = "",
    [switch]$NoFetch,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PathSpec = @()
)

$ErrorActionPreference = "Stop"

$GitExecutable = "git"
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if ($gitCommand) {
    $GitExecutable = $gitCommand.Source
} else {
    $gitCandidates = @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files\Git\bin\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
    )
    foreach ($candidate in $gitCandidates) {
        if (Test-Path $candidate) {
            $GitExecutable = $candidate
            break
        }
    }
}

function Invoke-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
    & $GitExecutable @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git $($GitArgs -join ' ') falhou com codigo $LASTEXITCODE"
    }
}

function Test-GitPath {
    param([string]$Path)
    $value = & $GitExecutable rev-parse --git-path $Path
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel resolver o caminho Git: $Path"
    }
    return (Test-Path $value)
}

function Get-GitConfigValue {
    param([string]$Key)
    $value = & $GitExecutable config --get $Key
    if ($LASTEXITCODE -ne 0 -or $null -eq $value) {
        return ""
    }
    return ([string]$value).Trim()
}

$repoRoot = & $GitExecutable rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) {
    throw "Este comando precisa ser executado dentro de um repositorio Git."
}

Set-Location $repoRoot

if ((Test-GitPath "MERGE_HEAD") -or (Test-GitPath "rebase-merge") -or (Test-GitPath "rebase-apply")) {
    throw "Sincronizacao automatica bloqueada: ha merge ou rebase em andamento."
}

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (& $GitExecutable branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($Branch)) {
        throw "Nao foi possivel identificar a branch atual."
    }
}

if ([string]::IsNullOrWhiteSpace($Remote)) {
    $Remote = Get-GitConfigValue "branch.$Branch.pushRemote"
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        $Remote = Get-GitConfigValue "remote.pushDefault"
    }
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        $Remote = Get-GitConfigValue "branch.$Branch.remote"
    }
    if ([string]::IsNullOrWhiteSpace($Remote)) {
        $Remote = "origin"
    }
}

if (-not $NoFetch) {
    & $GitExecutable fetch $Remote $Branch | Out-Host
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

& $GitExecutable diff --cached --quiet
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
