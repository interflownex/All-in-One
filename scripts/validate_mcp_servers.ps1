param([switch]$Verbose)
$ErrorActionPreference = "Continue"

$GREEN  = "`e[32m"
$RED    = "`e[31m"
$YELLOW = "`e[33m"
$BLUE   = "`e[34m"
$RESET  = "`e[0m"
$BOLD   = "`e[1m"

function Write-OK   { param([string]$L, [string]$M) Write-Host "${GREEN}${BOLD}[OK]${RESET}   [$L] $M" }
function Write-FAIL { param([string]$L, [string]$M) Write-Host "${RED}${BOLD}[FAIL]${RESET} [$L] $M" }
function Write-WARN { param([string]$L, [string]$M) Write-Host "${YELLOW}${BOLD}[WARN]${RESET} [$L] $M" }
function Write-INFO { param([string]$L, [string]$M) Write-Host "${BLUE}${BOLD}[INFO]${RESET} [$L] $M" }

$ok   = 0
$warn = 0
$fail = 0

Write-Host ""
Write-Host "${BOLD}${BLUE}============================================${RESET}"
Write-Host "${BOLD}${BLUE}  All-in-One - Validacao de Servidores MCP  ${RESET}"
Write-Host "${BOLD}${BLUE}============================================${RESET}"
Write-Host "  Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# 1. Ferramentas base
Write-Host "${BOLD}1. Ferramentas Base${RESET}"
Write-Host "--------------------------------------------"

foreach ($tool in @("node --version", "npx --version", "go version", "docker --version")) {
    $parts = $tool.Split(" ")
    $cmd   = $parts[0]
    $args  = $parts[1..($parts.Length-1)]
    try {
        $out = & $cmd $args 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-OK $cmd "$out"
            $ok++
        } else {
            Write-WARN $cmd "saiu com codigo $LASTEXITCODE"
            $warn++
        }
    } catch {
        Write-FAIL $cmd "nao encontrado"
        $fail++
    }
}

Write-Host ""

# 2. Pacotes NPX globais
Write-Host "${BOLD}2. Pacotes NPX MCP (instalados globalmente)${RESET}"
Write-Host "--------------------------------------------"

$pkgs = @(
    "@modelcontextprotocol/server-memory",
    "@modelcontextprotocol/server-filesystem",
    "@modelcontextprotocol/server-sequential-thinking",
    "@modelcontextprotocol/server-postgres",
    "mcp-remote",
    "chrome-devtools-mcp",
    "@playwright/mcp"
)

foreach ($pkg in $pkgs) {
    $chk = npm list -g --depth=0 $pkg 2>&1 | Select-String $pkg
    if ($chk) {
        Write-OK "NPX" "$pkg - instalado"
        $ok++
    } else {
        Write-WARN "NPX" "$pkg - nao instalado globalmente (npx -y fara download)"
        $warn++
    }
}

Write-Host ""

# 3. Endpoints remotos
Write-Host "${BOLD}3. Endpoints Remotos MCP${RESET}"
Write-Host "--------------------------------------------"

$endpoints = @(
    @{ n="Context7";      u="https://mcp.context7.com" },
    @{ n="Figma MCP";     u="https://mcp.figma.com" },
    @{ n="Linear MCP";    u="https://mcp.linear.app" },
    @{ n="Cloudflare";    u="https://mcp.cloudflare.com" },
    @{ n="Stitch GCP";    u="https://stitch.googleapis.com" },
    @{ n="BigQuery MCP";  u="https://bigquery.googleapis.com" },
    @{ n="GitLab Orbit";  u="https://gitlab.com" }
)

foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri $ep.u -Method HEAD -TimeoutSec 6 -ErrorAction Stop
        Write-OK $ep.n "HTTP $($r.StatusCode) - acessivel"
        $ok++
    } catch {
        $msg = $_.Exception.Message
        if ($msg -match "401|403|400|405|404") {
            Write-OK $ep.n "Acessivel (requer auth - $($msg.Substring(0,[Math]::Min(60,$msg.Length))))"
            $ok++
        } elseif ($msg -match "Unable to connect|timeout|No connection") {
            Write-WARN $ep.n "Sem conectividade: $($msg.Substring(0,[Math]::Min(80,$msg.Length)))"
            $warn++
        } else {
            Write-WARN $ep.n "$($msg.Substring(0,[Math]::Min(80,$msg.Length)))"
            $warn++
        }
    }
}

Write-Host ""

# 4. Bancos locais
Write-Host "${BOLD}4. Servicos Locais (Docker)${RESET}"
Write-Host "--------------------------------------------"

$ports = @(
    @{ n="PostgreSQL"; h="localhost"; p=5432 },
    @{ n="Redis";      h="localhost"; p=6379 },
    @{ n="RabbitMQ";   h="localhost"; p=5672 },
    @{ n="MongoDB";    h="localhost"; p=27017 }
)

foreach ($svc in $ports) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar  = $tcp.BeginConnect($svc.h, $svc.p, $null, $null)
        $ok2 = $ar.AsyncWaitHandle.WaitOne(2000, $false)
        if ($ok2 -and $tcp.Connected) {
            Write-OK $svc.n "$($svc.h):$($svc.p) - porta aberta"
            $ok++
        } else {
            Write-WARN $svc.n "$($svc.h):$($svc.p) - inacessivel (Docker parado?)"
            $warn++
        }
        $tcp.Close()
    } catch {
        Write-WARN $svc.n "Erro de conexao: $_"
        $warn++
    }
}

Write-Host ""

# 5. Docker daemon
Write-Host "${BOLD}5. Docker MCP${RESET}"
Write-Host "--------------------------------------------"

$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-OK "Docker" "Daemon em execucao"
    $ok++
    $img = docker images ghcr.io/github/github-mcp-server --format "{{.Tag}}" 2>&1
    if ($img) {
        Write-OK "GitHub MCP" "Imagem local disponivel: $img"
        $ok++
    } else {
        Write-WARN "GitHub MCP" "Imagem nao baixada (puxada automaticamente no primeiro uso)"
        $warn++
    }
} else {
    Write-WARN "Docker" "Daemon nao esta em execucao - github-mcp-server indisponivel"
    $warn++
}

Write-Host ""

# 6. Variaveis de ambiente
Write-Host "${BOLD}6. Variaveis de Ambiente${RESET}"
Write-Host "--------------------------------------------"

$envs = @(
    @{ v="STITCH_API_KEY";               d="Google Stitch MCP" },
    @{ v="GITHUB_PERSONAL_ACCESS_TOKEN"; d="GitHub MCP"        },
    @{ v="GOOGLE_CLOUD_PROJECT";          d="Google Cloud"     },
    @{ v="GOOGLE_APPLICATION_CREDENTIALS"; d="GCP Auth File"  }
)

foreach ($ev in $envs) {
    $val = [System.Environment]::GetEnvironmentVariable($ev.v)
    if ($val) {
        $m = $val.Substring(0,[Math]::Min(8,$val.Length)) + "..."
        Write-OK "ENV" "$($ev.v) ($($ev.d)) = $m"
        $ok++
    } else {
        Write-WARN "ENV" "$($ev.v) ($($ev.d)) - NAO definido"
        $warn++
    }
}

Write-Host ""

# 7. mcp_config.json
Write-Host "${BOLD}7. Arquivo mcp_config.json${RESET}"
Write-Host "--------------------------------------------"

$cfgPath = "$env:USERPROFILE\.gemini\antigravity\mcp_config.json"
if (Test-Path $cfgPath) {
    try {
        $cfg   = Get-Content $cfgPath -Raw | ConvertFrom-Json
        $count = ($cfg.mcpServers | Get-Member -MemberType NoteProperty).Count
        $names = ($cfg.mcpServers | Get-Member -MemberType NoteProperty).Name -join ", "
        Write-OK "mcp_config" "Valido - $count servidores configurados"
        Write-INFO "Servidores" $names
        $ok++
    } catch {
        Write-FAIL "mcp_config" "JSON invalido: $_"
        $fail++
    }
} else {
    Write-FAIL "mcp_config" "Nao encontrado: $cfgPath"
    $fail++
}

Write-Host ""

# Sumario
$total = $ok + $warn + $fail
Write-Host "${BOLD}${BLUE}============================================${RESET}"
Write-Host "${BOLD}  Sumario Final${RESET}"
Write-Host "${BOLD}${BLUE}============================================${RESET}"
Write-Host "${GREEN}${BOLD}  OK   : $ok${RESET}"
Write-Host "${YELLOW}${BOLD}  AVISO: $warn${RESET}"
Write-Host "${RED}${BOLD}  FALHA: $fail${RESET}"
Write-Host "  TOTAL: $total verificacoes"
Write-Host ""

if ($fail -eq 0) {
    Write-Host "${GREEN}${BOLD}Configuracao MCP validada com sucesso!${RESET}"
    exit 0
} else {
    Write-Host "${RED}${BOLD}Ha falhas criticas a corrigir.${RESET}"
    exit 1
}
