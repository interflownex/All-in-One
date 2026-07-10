param(
    [switch]$IncludeCloudflared,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Write-Step {
    param([string]$Message)
    Write-Host ("[stop-valley-runtime] {0}" -f $Message)
}

function Get-TargetProcesses {
    $patterns = @(
        '*\scripts\serve_valley_admin.py*',
        '*\scripts\start_valley_admin_public.ps1*',
        '*\scripts\start_valley_localhost_run_public.ps1*',
        '*\scripts\ensure_valley_product_public.ps1*'
    )

    $processes = Get-CimInstance Win32_Process | Where-Object {
        $commandLine = [string]$_.CommandLine
        if ([string]::IsNullOrWhiteSpace($commandLine)) {
            return $false
        }

        foreach ($pattern in $patterns) {
            if ($commandLine -like $pattern) {
                return $true
            }
        }

        if ($IncludeCloudflared -and $_.Name -eq 'cloudflared.exe' -and $commandLine -like '*8085*') {
            return $true
        }

        return $false
    }

    return @($processes | Sort-Object ProcessId -Unique)
}

function Stop-TargetProcesses {
    $targets = Get-TargetProcesses
    if (-not $targets) {
        Write-Step "Nenhum processo conflitando do VALLEY foi encontrado."
        return
    }

    foreach ($process in $targets) {
        $summary = "{0} PID {1}" -f $process.Name, $process.ProcessId
        if ($WhatIf) {
            Write-Step ("WhatIf: encerraria {0}" -f $summary)
            continue
        }

        Write-Step ("Encerrando {0}" -f $summary)
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Disable-ValleyTasks {
    $taskNames = @(
        'ValleyProductPublicRuntime',
        'ValleyReleaseRuntimeGate',
        'ValleyCommunicationBridge',
        'ValleyGeminiRefactorLoop',
        'ValleyMvpAutonomousClosure',
        'ValleyCloudflareTokenRegeneration',
        'ValleySafeAutonomousResume',
        'ValleyLocalhostRunPublicRuntime'
    )

    foreach ($taskName in $taskNames) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if (-not $task) {
            continue
        }

        if ($WhatIf) {
            Write-Step ("WhatIf: desabilitaria a tarefa agendada {0}" -f $taskName)
            continue
        }

        Write-Step ("Desabilitando tarefa agendada {0}" -f $taskName)
        Disable-ScheduledTask -TaskName $taskName | Out-Null

        try {
            Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Out-Null
        } catch {
        }
    }
}

function Remove-StartupShortcut {
    $startupShortcut = Join-Path ([Environment]::GetFolderPath('Startup')) 'ValleyLocalhostRunPublicRuntime.vbs'
    if (-not (Test-Path -LiteralPath $startupShortcut -PathType Leaf)) {
        return
    }

    if ($WhatIf) {
        Write-Step ("WhatIf: removeria o atalho de inicializacao {0}" -f $startupShortcut)
        return
    }

    Write-Step ("Removendo atalho de inicializacao {0}" -f $startupShortcut)
    Remove-Item -LiteralPath $startupShortcut -Force
}

function Write-Status {
    $status = [ordered]@{
        status = 'ok'
        generated_at = (Get-Date).ToString('o')
        include_cloudflared = [bool]$IncludeCloudflared
        what_if = [bool]$WhatIf
        note = 'Rotinas persistentes do projeto VALLEY desabilitadas para liberar o ambiente do all-in-one.'
    }

    $runtimeDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'tmp\runtime'
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    $statusPath = Join-Path $runtimeDir 'conflicting_valley_runtime_stop.json'

    if (-not $WhatIf) {
        $status | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statusPath -Encoding UTF8
        Write-Step ("Status gravado em {0}" -f $statusPath)
    }
}

if (-not (Test-IsAdministrator)) {
    throw "Execute este script em um PowerShell com privilegios de administrador."
}

Disable-ValleyTasks
Stop-TargetProcesses
Remove-StartupShortcut
Write-Status

Write-Host ""
Write-Host "Runtime conflitante do VALLEY desligado de forma persistente."
