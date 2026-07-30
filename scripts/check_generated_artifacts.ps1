param(
    [string[]]$Commands = @(
        "python scripts/check_scaffold_modules.py --check",
        "python scripts/validate_openapi.py",
        "python scripts/validate_repository.py"
    )
)

$ErrorActionPreference = "Stop"

function Invoke-Shell {
    param([string]$CommandLine)
    Write-Host "Executando: $CommandLine"
    if ($IsWindows) {
        & cmd.exe /c $CommandLine
    } else {
        & bash -lc $CommandLine
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Comando falhou com codigo $LASTEXITCODE: $CommandLine"
    }
}

$repoRoot = (& git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoRoot)) {
    throw "Este comando precisa ser executado dentro de um repositorio Git."
}
Set-Location $repoRoot

$before = (& git status --porcelain)
foreach ($command in $Commands) {
    Invoke-Shell $command
}
$after = (& git status --porcelain)

if (($before -join "`n") -ne ($after -join "`n")) {
    Write-Host "Estado antes:"
    $before | ForEach-Object { Write-Host $_ }
    Write-Host "Estado depois:"
    $after | ForEach-Object { Write-Host $_ }
    throw "Artefatos gerados ou validadores alteraram a arvore de trabalho. Execute, revise e commite os resultados."
}

Write-Host "Gate de artefatos gerados aprovado: arvore de trabalho preservada."
