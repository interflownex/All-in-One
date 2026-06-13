# Provisionamento Autonomo do All-in-One no Antigravity IDE

## Instrucao mandataria para o Codex

Este documento e uma ordem de execucao completa para o Codex operando na
maquina Windows do usuario. Ao receber a ordem para executar este arquivo, o
Codex deve realizar todas as etapas abaixo de forma autonoma, sequencial e
verificavel.

O Codex nao deve apenas explicar os comandos. Deve executa-los, corrigir falhas
recuperaveis e continuar ate que todos os criterios de sucesso sejam atendidos.
So e permitido interromper quando uma autenticacao interativa exigir acao
humana ou quando um recurso externo estiver comprovadamente indisponivel.

## Objetivo

Substituir integralmente a base local existente:

```text
C:\Users\ereta\.codex\worktrees\all-in-one
```

pela versao remota oficial:

```text
Repositorio: https://github.com/interflownex/All-in-One.git
Branch: main
Referencia autoritativa: origin/main
```

Depois da substituicao, instalar e configurar o ambiente de desenvolvimento
Windows para uso no Antigravity IDE, incluindo Git, GitHub CLI, PowerShell 7,
Python 3.12, Node.js 22.14.0, Java 17, Docker Desktop, Android Studio,
Terraform, Kubernetes CLI, dependencias Python, dependencias web, variaveis
locais, Docker Compose, servidores MCP e validacoes do repositorio.

O ambiente deve ser **local-first** e autossuficiente. A aplicacao, bancos,
filas, cache, frontends, testes e build Android nao podem depender de Cloud
Shell, Cloud Build, Cloud Run, GKE, AlloyDB ou qualquer runtime Google.
Integracoes Google podem permanecer instaladas como opcionais, mas devem ficar
desativadas no perfil local e nao podem bloquear o provisionamento.

## Regras inegociaveis

1. A nuvem, representada por `origin/main`, e a fonte de verdade.
2. O conteudo antigo do diretorio alvo nao pode ser mesclado ou reaplicado
   automaticamente sobre o clone novo.
3. Antes da substituicao, criar um backup fechado e datado fora do diretorio
   alvo.
4. Nunca copiar `.env`, tokens, chaves, credenciais ou configuracoes secretas
   do backup para o clone novo.
5. Nunca executar `git reset --hard` dentro da base antiga.
6. A substituicao deve ser feita movendo a base antiga inteira e clonando uma
   copia limpa no caminho original.
7. Nao apagar o backup automaticamente.
8. Nao versionar `.env`, credenciais ou arquivos gerados.
9. Executar comandos elevados somente quando a instalacao do Windows ou Docker
   exigir.
10. Nao declarar sucesso sem executar os checkpoints deste documento.
11. Preservar os arquivos `AGENTS.md`, `GEMINI.md` e as politicas versionadas
    recebidas de `origin/main`.
12. Depois do clone, todo desenvolvimento deve ocorrer em branch
    `codex/<descricao>`, nunca diretamente em `main`.
13. O perfil local deve funcionar sem login Google, projeto Google Cloud,
    billing, ADC ou acesso a servicos remotos.
14. MCPs locais devem ser instalados e testados. MCPs SaaS que exijam conta,
    token ou OAuth devem ser configurados sem segredo literal e marcados como
    pendentes, sem bloquear o restante do ambiente.

## Estado final esperado

Ao concluir:

- o caminho alvo deve ser um clone limpo de `origin/main`;
- `git status --short --branch` nao deve mostrar alteracoes;
- Python deve usar `.venv\Scripts\python.exe`;
- Node.js deve estar na versao definida por `.nvmrc`;
- Docker Desktop deve estar operacional com containers Linux;
- o Docker Compose deve ser valido;
- as dependencias devem estar instaladas;
- as validacoes basicas devem passar;
- o Antigravity IDE deve conseguir abrir o workspace;
- os MCPs locais essenciais devem responder no Antigravity;
- o projeto deve funcionar com todas as flags Google e AlloyDB desativadas;
- nenhum segredo deve estar versionado.

## Fase 1 - Preflight e inventario

Executar no PowerShell 7:

```powershell
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Target = "C:\Users\ereta\.codex\worktrees\all-in-one"
$Parent = Split-Path $Target -Parent
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupRoot = "C:\Users\ereta\.codex\backups"
$Backup = Join-Path $BackupRoot "all-in-one-before-cloud-$Timestamp"
$Repository = "https://github.com/interflownex/All-in-One.git"
$Branch = "main"

New-Item -ItemType Directory -Force -Path $Parent | Out-Null
New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
```

Registrar o inventario da base antiga quando ela existir:

```powershell
if (Test-Path $Target) {
    $Inventory = Join-Path $BackupRoot "all-in-one-inventory-$Timestamp.txt"
    @(
        "Data UTC: $([DateTime]::UtcNow.ToString('o'))"
        "Origem local: $Target"
        "Destino do backup: $Backup"
    ) | Set-Content -Encoding UTF8 $Inventory

    if (Test-Path (Join-Path $Target ".git")) {
        git -C $Target status --short --branch |
            Add-Content -Encoding UTF8 $Inventory
        git -C $Target log -1 --format="%H %cI %s" |
            Add-Content -Encoding UTF8 $Inventory
        git -C $Target remote -v |
            Add-Content -Encoding UTF8 $Inventory
    }
}
```

Se houver processos usando o diretorio, fechar terminais, agentes e janelas do
Antigravity associados ao workspace. O Codex pode encerrar apenas processos
claramente vinculados ao caminho alvo. Nao encerrar processos nao relacionados.

## Fase 2 - Backup e substituicao integral

Sair do diretorio que sera substituido:

```powershell
Set-Location $Parent
```

Mover a base antiga inteira:

```powershell
if (Test-Path $Target) {
    Move-Item -LiteralPath $Target -Destination $Backup
}
```

Clonar exclusivamente a referencia remota:

```powershell
try {
    git clone `
        --branch $Branch `
        --single-branch `
        --origin origin `
        $Repository `
        $Target

    if ($LASTEXITCODE -ne 0) {
        throw "git clone retornou codigo $LASTEXITCODE."
    }

    Set-Location $Target
    git fetch --prune origin
    git checkout $Branch
    git pull --ff-only origin $Branch
} catch {
    Set-Location $Parent

    if (Test-Path $Target) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }

    if (Test-Path $Backup) {
        Move-Item -LiteralPath $Backup -Destination $Target
    }

    throw "Clone remoto falhou e a base anterior foi restaurada: $($_.Exception.Message)"
}
```

Validar que o clone corresponde exatamente a `origin/main`:

```powershell
$LocalHead = git rev-parse HEAD
$RemoteHead = git rev-parse "origin/$Branch"

if ($LocalHead -ne $RemoteHead) {
    throw "Clone local nao corresponde a origin/$Branch."
}

if (git status --porcelain) {
    throw "O clone novo nao esta limpo."
}
```

Depois de um clone valido, o backup deve permanecer intacto em
`C:\Users\ereta\.codex\backups`.

## Fase 3 - Instalar ferramentas obrigatorias

Verificar a existencia do `winget`. Quando disponivel, instalar ou atualizar:

```powershell
$Packages = @(
    "Git.Git",
    "Microsoft.PowerShell",
    "Microsoft.WindowsTerminal",
    "Docker.DockerDesktop",
    "Python.Python.3.12",
    "GitHub.cli",
    "EclipseAdoptium.Temurin.17.JDK",
    "Schniz.fnm",
    "Google.AndroidStudio",
    "Google.Chrome",
    "7zip.7zip",
    "Hashicorp.Terraform",
    "Kubernetes.kubectl",
    "Helm.Helm",
    "DBeaver.DBeaver.Community",
    "Bruno.Bruno"
)

foreach ($Package in $Packages) {
    winget install `
        --id $Package `
        --exact `
        --silent `
        --accept-package-agreements `
        --accept-source-agreements
}
```

O Codex deve tolerar o retorno que indica pacote ja instalado e verificar o
resultado com o executavel correspondente.

Instalar a versao Node.js exigida pelo repositorio:

```powershell
fnm env --use-on-cd | Out-String | Invoke-Expression
$NodeVersion = (Get-Content ".nvmrc" -Raw).Trim().TrimStart("v")
fnm install $NodeVersion
fnm use $NodeVersion
fnm default $NodeVersion
```

Verificacoes obrigatorias:

```powershell
git --version
pwsh --version
python --version
node --version
npm --version
java -version
docker version
docker compose version
gh --version
terraform version
kubectl version --client
helm version
```

Se algum identificador do `winget` tiver mudado, pesquisar pelo nome com
`winget search`, selecionar somente o editor oficial e registrar o ID
efetivamente instalado. Google Cloud CLI nao e requisito do perfil local.

Se uma alteracao de `PATH`, instalacao do WSL ou Docker exigir reinicializacao,
o Codex deve concluir as instalacoes, registrar o ponto de retomada e continuar
automaticamente depois da reinicializacao quando o ambiente permitir.

## Fase 4 - Instalar o Antigravity IDE

Verificar se o produto **Antigravity IDE** esta instalado. Ele e diferente do
aplicativo independente **Antigravity 2.0**.

Fonte oficial:

```text
https://antigravity.google/download
```

O Codex deve:

1. procurar primeiro um pacote oficial no `winget`;
2. se nao houver, baixar o instalador Windows x64 da pagina oficial;
3. validar que o dominio de origem e `antigravity.google`;
4. executar o instalador;
5. confirmar que a versao instalada e `1.21.5` ou superior;
6. nunca baixar instaladores de espelhos ou sites de terceiros;
7. abrir o Antigravity IDE ao final;
8. aguardar somente a autenticacao Google interativa, quando solicitada.

## Fase 5 - Ambiente Python

No clone novo:

```powershell
Set-Location $Target

if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force
}

python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
```

Instalar tambem os requisitos dos modulos e workers:

```powershell
Get-ChildItem -Path "modules", "workers" -Filter "requirements.txt" -Recurse |
    ForEach-Object {
        & ".\.venv\Scripts\python.exe" -m pip install -r $_.FullName
    }
```

Instalar o navegador de testes:

```powershell
& ".\.venv\Scripts\python.exe" -m playwright install chromium
```

## Fase 6 - Configuracao local segura

Criar `.env` somente quando ele nao existir:

```powershell
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}
```

Gerar uma chave nova para desenvolvimento local:

```powershell
$EncryptionKey = & ".\.venv\Scripts\python.exe" -c `
    "import base64,secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

$EnvContent = Get-Content ".env" -Raw
$EnvContent = $EnvContent -replace `
    "(?m)^ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY=.*$", `
    "ALL_IN_ONE_DOCUMENT_ENCRYPTION_KEY=$EncryptionKey"
$EnvContent | Set-Content -Encoding UTF8 ".env"
```

Garantir valores locais de desenvolvimento, sem credenciais produtivas:

```dotenv
POSTGRES_DB=all_in_one
POSTGRES_USER=all_in_one
POSTGRES_PASSWORD=local-development-only
MONGO_INITDB_DATABASE=all_in_one
RABBITMQ_DEFAULT_USER=all_in_one
RABBITMQ_DEFAULT_PASS=local-development-only
GOOGLE_INTEGRATIONS_ENABLED=false
GOOGLE_CLOUD_ENABLED=false
GOOGLE_AI_STUDIO_ENABLED=false
GOOGLE_CODE_CLI_ENABLED=false
ALLOYDB_ENABLED=false
ALLOYDB_DSN=
GEMINI_CODE_ASSIST_ENABLED=false
STITCH_REMOTE_SYNC_ENABLED=false
```

Credenciais de integracoes Google e Stitch devem permanecer vazias. Nao copiar
credenciais do ambiente remoto.

Confirmar que `.env` esta ignorado:

```powershell
git check-ignore ".env"
```

## Fase 7 - Configurar Antigravity e extensoes

Abrir o diretorio:

```text
C:\Users\ereta\.codex\worktrees\all-in-one
```

No workspace, o Antigravity deve respeitar:

```text
AGENTS.md
GEMINI.md
.agents\antigravity.json
config\autonomy\multi_agent_sync_policy.json
```

Instalar as extensoes disponiveis equivalentes a:

```text
ms-python.python
ms-python.vscode-pylance
ms-python.debugpy
charliermarsh.ruff
ms-azuretools.vscode-docker
ms-vscode.powershell
redhat.vscode-yaml
esbenp.prettier-vscode
dbaeumer.vscode-eslint
github.vscode-github-actions
github.vscode-pull-request-github
eamodio.gitlens
ms-vscode-remote.remote-wsl
ms-kubernetes-tools.vscode-kubernetes-tools
hashicorp.terraform
vscjava.vscode-java-pack
vscjava.vscode-gradle
fwcd.kotlin
humao.rest-client
editorconfig.editorconfig
GoogleCloudTools.datacloud
```

Selecionar como interpretador:

```text
C:\Users\ereta\.codex\worktrees\all-in-one\.venv\Scripts\python.exe
```

Se `.vscode\settings.json` apontar para `.venv/bin/python`, criar uma
configuracao local do editor ou selecionar o interpretador pela interface. Nao
fazer commit de uma alteracao especifica de maquina sem necessidade.

### Configurar todos os servidores MCP

Antigravity IDE, Antigravity 2.0 e Antigravity CLI usam a configuracao central:

```text
C:\Users\ereta\.gemini\config\mcp_config.json
```

O Codex deve criar backup do arquivo existente e fazer merge por JSON. Nao
concatenar texto JSON e nao sobrescrever servidores preexistentes:

```powershell
$McpDirectory = Join-Path $env:USERPROFILE ".gemini\config"
$McpConfig = Join-Path $McpDirectory "mcp_config.json"
$McpBackup = Join-Path $McpDirectory `
    "mcp_config.before-all-in-one-$Timestamp.json"

New-Item -ItemType Directory -Force -Path $McpDirectory | Out-Null

if (Test-Path $McpConfig) {
    Copy-Item $McpConfig $McpBackup
    try {
        $Mcp = Get-Content $McpConfig -Raw |
            ConvertFrom-Json -AsHashtable
    } catch {
        throw "mcp_config.json existente e invalido: $($_.Exception.Message)"
    }
} else {
    $Mcp = @{}
}

if (-not $Mcp.ContainsKey("mcpServers")) {
    $Mcp["mcpServers"] = @{}
}
```

#### MCPs locais obrigatorios

Instalar previamente os pacotes Node usados pelos servidores locais:

```powershell
npm install --global `
    @playwright/mcp `
    @modelcontextprotocol/server-filesystem
```

Configurar:

```powershell
$Mcp["mcpServers"]["filesystem-all-in-one"] = @{
    command = "npx"
    args = @(
        "-y",
        "@modelcontextprotocol/server-filesystem",
        $Target
    )
}

$Mcp["mcpServers"]["playwright"] = @{
    command = "npx"
    args = @("-y", "@playwright/mcp@latest", "--headless")
}

$Mcp["mcpServers"]["context7"] = @{
    serverUrl = "https://mcp.context7.com/mcp"
}
```

O filesystem deve ficar restrito ao workspace. Nao conceder acesso ao perfil
inteiro do usuario, `.ssh`, diretórios de credenciais ou backups.

#### Docker MCP Toolkit e Gateway

Exigir Docker Desktop `4.62` ou superior e verificar:

```powershell
docker mcp --help
```

Criar um perfil dedicado:

```powershell
$McpProfile = "all-in-one-local"
$Profiles = docker mcp profile list 2>$null | Out-String

if ($Profiles -notmatch [regex]::Escape($McpProfile)) {
    docker mcp profile create --name $McpProfile
}
```

Consultar o catalogo antes de adicionar servidores, pois IDs podem evoluir:

```powershell
$Catalog = docker mcp catalog server ls mcp/docker-mcp-catalog |
    Out-String

$DesiredCatalogServers = @(
    "playwright",
    "github-official",
    "terraform",
    "filesystem"
)

foreach ($ServerId in $DesiredCatalogServers) {
    if ($Catalog -match "(?m)^\s*$([regex]::Escape($ServerId))\s") {
        docker mcp profile server add $McpProfile `
            --server "catalog://mcp/docker-mcp-catalog/$ServerId"
    }
}
```

Conectar o Gateway ao Antigravity:

```powershell
$Mcp["mcpServers"]["docker"] = @{
    command = "docker"
    args = @("mcp", "gateway", "run", "--profile", $McpProfile)
}
```

Se Docker Desktop for anterior a `4.62`, atualizar antes de continuar. Nao
substituir o Docker MCP Gateway por comandos Docker com `shell=true`.

#### Terraform MCP

O executavel `terraform` deve estar instalado localmente. Quando o servidor
`terraform` existir no Docker MCP Catalog, ele deve integrar o perfil acima.
Se nao existir, baixar somente um binario oficial do Terraform MCP Server a
partir das releases da HashiCorp e configurá-lo por `command`/`args`.

O MCP Terraform local deve iniciar em modo somente leitura/documentacao. Nao
autorizar `apply`, destruicao, HCP Terraform ou Terraform Enterprise sem uma
ordem separada e credenciais explicitas.

#### MCPs SaaS opcionais

Os servidores abaixo podem ser cadastrados, mas nao sao requisitos para o
runtime local:

```text
cloudflare-api
figma
linear
stitch
cloudrun
gke-oss
```

Regras:

1. `cloudrun`, `gke-oss` e `stitch` devem ficar desativados no perfil local,
   pois dependem do ambiente Google abandonado nesta configuracao.
2. Cloudflare, Figma e Linear so podem ser ativados depois de OAuth ou token
   legitimo fornecido externamente.
3. Tokens nunca devem ser escritos em `mcp_config.json`.
4. Usar variaveis como `CLOUDFLARE_API_TOKEN`, `FIGMA_ACCESS_TOKEN`,
   `LINEAR_API_KEY` e `CONTEXT7_API_KEY`.
5. Ausencia dessas credenciais deve resultar em `pendente`, nao em falha do
   provisionamento local.

#### Persistir e validar o JSON MCP

```powershell
$Mcp |
    ConvertTo-Json -Depth 20 |
    Set-Content -Encoding UTF8 $McpConfig

Get-Content $McpConfig -Raw |
    ConvertFrom-Json |
    Out-Null
```

Reabrir o Antigravity e acessar:

```text
Agent panel > ... > MCP Servers > Manage MCP Servers > Refresh
```

Validar no minimo:

- `filesystem-all-in-one`: lista apenas arquivos do workspace;
- `playwright`: abre `http://localhost:8100/health`;
- `docker`: lista containers do projeto pelo Gateway;
- `context7`: consulta documentacao publica;
- `terraform`: consulta documentacao sem executar `apply`.

Nenhum MCP local pode aparecer como `Disconnected` ao final. Para cada MCP SaaS
opcional, registrar claramente `desativado sem credencial`.

### Recuperar falha de instalacao do Google Cloud Data Agent Kit

O nome atual da extensao e **Google Cloud Data Agent Kit**. O identificador
oficial no Visual Studio Marketplace e:

```text
GoogleCloudTools.datacloud
```

Quando a instalacao retornar:

```text
Unexpected non-whitespace character after JSON
```

o Codex deve tratar o problema como resposta JSON concatenada ou cache de
download corrompido. Nao deve repetir indefinidamente a mesma instalacao pela
interface.

Fechar todas as instancias do Antigravity:

```powershell
Get-Process |
    Where-Object { $_.ProcessName -match "Antigravity" } |
    Stop-Process -Force
```

Descobrir os diretorios existentes e remover somente caches descartaveis:

```powershell
$AntigravityRoots = @(
    (Join-Path $env:APPDATA "Antigravity"),
    (Join-Path $env:LOCALAPPDATA "Antigravity")
) | Where-Object { Test-Path $_ }

$DisposableCacheNames = @(
    "Cache",
    "CachedData",
    "CachedExtensionVSIXs",
    "Code Cache",
    "GPUCache"
)

foreach ($Root in $AntigravityRoots) {
    foreach ($CacheName in $DisposableCacheNames) {
        $CachePath = Join-Path $Root $CacheName
        if (Test-Path $CachePath) {
            Remove-Item -LiteralPath $CachePath -Recurse -Force
        }
    }
}
```

Nao remover:

```text
User
User\globalStorage
User\workspaceStorage
state.vscdb
gcloud
Application Default Credentials
```

Remover somente uma instalacao incompleta da extensao:

```powershell
$ExtensionRoots = @(
    (Join-Path $env:USERPROFILE ".antigravity\extensions"),
    (Join-Path $env:USERPROFILE ".vscode\extensions")
) | Where-Object { Test-Path $_ }

foreach ($Root in $ExtensionRoots) {
    Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -like "googlecloudtools.datacloud-*"
        } |
        Remove-Item -Recurse -Force
}
```

Baixar o VSIX diretamente do endpoint oficial do Visual Studio Marketplace,
evitando o catalogo JSON que falhou:

```powershell
$Vsix = Join-Path $env:TEMP "GoogleCloudTools.datacloud.vsix"
$VsixUri = "https://marketplace.visualstudio.com/_apis/public/gallery/" +
    "publishers/GoogleCloudTools/vsextensions/datacloud/latest/vspackage"

Remove-Item $Vsix -Force -ErrorAction SilentlyContinue
Invoke-WebRequest `
    -Uri $VsixUri `
    -OutFile $Vsix `
    -MaximumRedirection 10 `
    -Headers @{ "Accept" = "application/octet-stream" }

if ((Get-Item $Vsix).Length -lt 100000) {
    throw "O pacote VSIX baixado e inesperadamente pequeno."
}

# O Marketplace pode entregar o VSIX encapsulado em gzip.
$InputStream = [System.IO.File]::OpenRead($Vsix)
try {
    $FirstByte = $InputStream.ReadByte()
    $SecondByte = $InputStream.ReadByte()
} finally {
    $InputStream.Dispose()
}

if (($FirstByte -eq 0x1f) -and ($SecondByte -eq 0x8b)) {
    $ExpandedVsix = "$Vsix.expanded"
    $CompressedStream = [System.IO.File]::OpenRead($Vsix)
    $OutputStream = [System.IO.File]::Create($ExpandedVsix)
    $GzipStream = [System.IO.Compression.GzipStream]::new(
        $CompressedStream,
        [System.IO.Compression.CompressionMode]::Decompress
    )

    try {
        $GzipStream.CopyTo($OutputStream)
    } finally {
        $GzipStream.Dispose()
        $OutputStream.Dispose()
        $CompressedStream.Dispose()
    }

    Move-Item -LiteralPath $ExpandedVsix -Destination $Vsix -Force
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$Archive = [System.IO.Compression.ZipFile]::OpenRead($Vsix)
try {
    if (-not ($Archive.Entries.FullName -contains "extension/package.json")) {
        throw "O arquivo baixado nao e um VSIX valido."
    }
} finally {
    $Archive.Dispose()
}
```

Localizar a CLI do Antigravity:

```powershell
$AntigravityCandidates = @(
    (Get-Command antigravity -ErrorAction SilentlyContinue).Source,
    (Join-Path $env:LOCALAPPDATA "Programs\Antigravity\bin\antigravity.cmd"),
    (Join-Path $env:LOCALAPPDATA "Programs\Antigravity\Antigravity.exe")
) | Where-Object { $_ -and (Test-Path $_) }

$AntigravityCli = $AntigravityCandidates | Select-Object -First 1

if (-not $AntigravityCli) {
    throw "CLI do Antigravity nao encontrada. Atualize ou reinstale o IDE."
}
```

Instalar o pacote local validado:

```powershell
& $AntigravityCli `
    --install-extension $Vsix `
    --force

if ($LASTEXITCODE -ne 0) {
    throw "Instalacao do Google Cloud Data Agent Kit falhou."
}

$InstalledExtensions = & $AntigravityCli --list-extensions
if ($InstalledExtensions -notcontains "GoogleCloudTools.datacloud") {
    throw "GoogleCloudTools.datacloud nao aparece na lista de extensoes."
}
```

Se a distribuicao instalada do Antigravity nao expuser
`--install-extension`, abrir o IDE e usar:

```text
Extensions > ... > Install from VSIX
```

Selecionar o arquivo `%TEMP%\GoogleCloudTools.datacloud.vsix`. Esse e o unico
passo de interface permitido nesse fallback.

O Codex deve reabrir o Antigravity, confirmar que o icone do Google Cloud Data
Agent Kit aparece. No perfil local-first, nao autenticar a extensao nem exigir
Google Cloud. Ela deve permanecer instalada, mas inativa.

## Fase 8 - GitHub e integracoes remotas opcionais

Verificar a autenticacao:

```powershell
gh auth status
```

Se necessario, iniciar o fluxo oficial:

```powershell
gh auth login --web
```

Google Cloud CLI, ADC, Cloud Build, Cloud Run e GKE nao devem ser configurados
no perfil local. Se ja estiverem instalados, nao apagar credenciais existentes,
mas nao usa-las nem torna-las requisito.

Nunca imprimir tokens ou credenciais nos logs.

## Fase 9 - Dependencias web

Instalar dependencias somente nos aplicativos que possuam `package.json`:

```powershell
$Applications = @(
    "apps\all-in-one",
    "apps\all-in-one-business",
    "apps\valley",
    "apps\valley_business",
    "apps\valley_rider",
    "desktop\valley-erp"
)

foreach ($Application in $Applications) {
    if (Test-Path (Join-Path $Application "package.json")) {
        Push-Location $Application
        try {
            if (Test-Path "package-lock.json") {
                npm ci
            } else {
                npm install
            }
        } finally {
            Pop-Location
        }
    }
}
```

## Fase 10 - Docker Desktop e servicos

Iniciar o Docker Desktop quando o daemon nao estiver acessivel. Aguardar ate:

```powershell
docker info
```

Validar o manifesto:

```powershell
docker compose -f infra/docker/docker-compose.yml config --quiet
```

Subir o ambiente:

```powershell
docker compose -f infra/docker/docker-compose.yml up --build -d
```

Verificar:

```powershell
docker compose -f infra/docker/docker-compose.yml ps
docker compose -f infra/docker/docker-compose.yml logs --tail 200
```

O Codex deve investigar containers `unhealthy`, `exited` ou reiniciando,
corrigir configuracoes locais recuperaveis e repetir a validacao.

## Fase 11 - Validacoes obrigatorias

Executar:

```powershell
& ".\.venv\Scripts\python.exe" scripts\scaffold_modules.py --check
& ".\.venv\Scripts\python.exe" scripts\validate_repository.py
& ".\.venv\Scripts\python.exe" -m pytest --import-mode=importlib
```

Testar endpoints essenciais:

```powershell
$HealthEndpoints = @(
    "http://localhost:8100/health",
    "http://localhost:8101/health",
    "http://localhost:8102/health",
    "http://localhost:8112/health",
    "http://localhost:8113/health"
)

foreach ($Endpoint in $HealthEndpoints) {
    $Response = Invoke-WebRequest -UseBasicParsing -Uri $Endpoint -TimeoutSec 15
    if ($Response.StatusCode -ne 200) {
        throw "Healthcheck falhou: $Endpoint"
    }
}
```

Validar builds web:

```powershell
foreach ($Application in $Applications) {
    if (Test-Path (Join-Path $Application "package.json")) {
        Push-Location $Application
        try {
            npm run build
        } finally {
            Pop-Location
        }
    }
}
```

## Fase 12 - Android

Validar que o builder Android pode ser criado:

```powershell
docker build `
    -t all-in-one-android-builder `
    -f infra/docker/android-builder.Dockerfile `
    .
```

Gerar o APK:

```powershell
docker run --rm `
    -v "${Target}:/workspace" `
    -w /workspace/apps/valley-android `
    all-in-one-android-builder `
    bash ./gradlew --no-daemon assembleDebug
```

Confirmar:

```powershell
$Apk = Join-Path $Target `
    "apps\valley-android\app\build\outputs\apk\debug\app-debug.apk"

if (-not (Test-Path $Apk)) {
    throw "APK nao foi gerado."
}

Get-FileHash $Apk -Algorithm SHA256
Get-Item $Apk | Select-Object FullName, Length, LastWriteTime
```

O APK e artefato local e nao deve ser commitado.

## Fase 13 - Higiene e branch de trabalho

Remover somente caches e artefatos reconhecidamente gerados pelo
provisionamento quando necessario. Nao remover o APK solicitado.

Confirmar que o clone base continua sem alteracoes versionaveis:

```powershell
git status --short --branch
git diff --check
```

Criar uma branch para trabalhos futuros:

```powershell
$WorkBranch = "codex/ambiente-local-antigravity"

if (-not (git branch --list $WorkBranch)) {
    git switch -c $WorkBranch
} else {
    git switch $WorkBranch
}
```

Nao criar commit apenas por instalar dependencias, criar `.env` ou gerar
artefatos ignorados.

## Criterios de sucesso

Todos os itens devem ser verdadeiros:

- [ ] a base antiga foi movida para um backup datado;
- [ ] o caminho alvo foi recriado por `git clone`;
- [ ] `HEAD` era igual a `origin/main` imediatamente apos o clone;
- [ ] o repositorio nao recebeu arquivos da base antiga;
- [ ] Python 3.12 e `.venv` estao funcionais;
- [ ] Node.js corresponde a `.nvmrc`;
- [ ] Java 17 esta disponivel;
- [ ] Docker e Docker Compose respondem;
- [ ] o manifesto Compose e valido;
- [ ] as dependencias Python e web foram instaladas;
- [ ] os validadores e testes foram executados;
- [ ] os healthchecks essenciais retornam HTTP 200;
- [ ] o APK debug foi gerado;
- [ ] `.env` esta ignorado pelo Git;
- [ ] o Antigravity IDE abriu o workspace correto;
- [ ] Antigravity esta na versao 1.21.5 ou superior;
- [ ] `GoogleCloudTools.datacloud` esta instalada e visivel;
- [ ] todos os aplicativos e extensoes locais obrigatorios foram instalados;
- [ ] `filesystem-all-in-one`, Playwright, Docker, Context7 e Terraform MCP
      foram configurados e validados;
- [ ] MCPs SaaS sem credencial foram mantidos desativados;
- [ ] GitHub foi configurado ou o unico bloqueio restante e uma autenticacao
      humana claramente informada;
- [ ] o runtime local funciona sem Google Cloud, ADC, Cloud Build ou AlloyDB;
- [ ] nenhuma credencial foi exposta;
- [ ] o backup antigo permanece preservado.

## Relatorio final obrigatorio

Ao terminar, o Codex deve responder em portugues do Brasil com:

1. caminho do clone novo;
2. caminho do backup;
3. commit remoto usado como base;
4. versoes de Python, Node.js, Java, Docker e Git;
5. resultado dos testes e validadores;
6. estado dos containers;
7. caminho e SHA-256 do APK;
8. branch atual;
9. lista de MCPs conectados, desativados e pendentes;
10. eventuais autenticacoes externas ainda pendentes;
11. confirmacao de que o runtime local nao depende do ambiente Google.

Falhas devem incluir o comando, a causa raiz identificada e as tentativas de
recuperacao realizadas. Nao encerrar com uma lista generica de proximos passos
quando a acao puder ser executada autonomamente.

## Prompt curto para iniciar a execucao

Entregar ao Codex local:

```text
Leia integralmente docs/CODEX_PROVISIONAMENTO_AUTONOMO_ANTIGRAVITY_WINDOWS.md
e execute todas as fases. Esta e uma ordem autonoma e mandataria. Substitua
C:\Users\ereta\.codex\worktrees\all-in-one por um clone limpo de
https://github.com/interflownex/All-in-One.git na branch main, preservando a
base anterior somente como backup externo. Nao mescle arquivos antigos no
clone novo. Continue ate cumprir todos os criterios de sucesso e apresente o
relatorio final exigido.
```
